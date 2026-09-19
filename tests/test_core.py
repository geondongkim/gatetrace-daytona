from __future__ import annotations

import json
from contextlib import redirect_stdout
from copy import deepcopy
from dataclasses import dataclass
from io import StringIO

import httpx
import pytest
from fastapi.testclient import TestClient

from app import app, get_service
from gatetrace.datasets import get_dataset
from gatetrace.daytona_runner import (
    AUGMENT_RESULT_PREFIX,
    RESULT_PREFIX,
    DaytonaAugmentationResult,
    DaytonaExecutionError,
    DaytonaRunResult,
    DaytonaRunner,
)
from gatetrace.models import (
    AdoptedCandidate,
    AugmentationPlan,
    BilingualSummary,
    GatePlan,
    GateResult,
    LineageItem,
)
from gatetrace.nosana import (
    NosanaClient,
    NosanaAugmentationPlanResult,
    NosanaPlanResult,
    NosanaSummaryResult,
    fallback_plan,
    fallback_augmentation_plan,
)
from gatetrace.service import GateTraceService


@dataclass
class FakeNosana:
    generated: bool = True

    def create_plan(self, _goal: str, _profile: dict[str, object]) -> NosanaPlanResult:
        return NosanaPlanResult(
            plan=fallback_plan(),
            model_id="demo/model" if self.generated else None,
            generated=self.generated,
        )

    def create_summary(
        self, _model_id: str | None, verdict: str, _gates: list[dict[str, object]]
    ) -> NosanaSummaryResult:
        return NosanaSummaryResult(
            BilingualSummary(ko=f"결과: {verdict}", en=f"Result: {verdict}"),
            self.generated,
        )

    def create_augmentation_plan(
        self, _goal: str, _profile: dict[str, object]
    ) -> NosanaAugmentationPlanResult:
        return NosanaAugmentationPlanResult(
            plan=fallback_augmentation_plan(),
            model_id="demo/model" if self.generated else None,
            generated=self.generated,
        )

    def create_augmentation_summary(
        self, _model_id: str | None, verdict: str, _gates: list[dict[str, object]]
    ) -> NosanaSummaryResult:
        return NosanaSummaryResult(
            BilingualSummary(ko=f"증강: {verdict}", en=f"Augmentation: {verdict}"),
            self.generated,
        )


class FakeDaytona:
    def __init__(self, *, failed: bool = False, execution_error: bool = False) -> None:
        self.failed = failed
        self.execution_error = execution_error
        self.called = False

    def run(self, _rows: list[dict[str, object]], plan: GatePlan) -> DaytonaRunResult:
        self.called = True
        if self.execution_error:
            raise DaytonaExecutionError("safe test failure")
        results = []
        for gate in plan.gates:
            gate_id = "missing_rate" if gate.type == "max_missing_rate" else gate.type
            status = "FAIL" if self.failed and gate_id == "missing_rate" else "PASS"
            results.append(
                GateResult(
                    id=gate_id,
                    status=status,
                    message_key=f"gate.{gate_id}.{status.lower()}",
                    evidence={"source": "mock"},
                )
            )
        return DaytonaRunResult(sandbox_id="sandbox-test", gates=results)

    def augment_and_validate(
        self,
        rows: list[dict[str, object]],
        augmentation_plan: AugmentationPlan,
        plan: GatePlan,
    ) -> DaytonaAugmentationResult:
        self.called = True
        if self.execution_error:
            raise DaytonaExecutionError("safe test failure")
        gates = []
        for gate in plan.gates:
            gate_id = "missing_rate" if gate.type == "max_missing_rate" else gate.type
            status = "FAIL" if self.failed and gate_id == "missing_rate" else "PASS"
            gates.append(
                GateResult(
                    id=gate_id,
                    status=status,
                    message_key=f"gate.{gate_id}.{status.lower()}",
                    evidence={"source": "mock"},
                )
            )
        lineage = [
            LineageItem(
                derived_row_id=f"aug-{augmentation_plan.seed}-{index + 1:03d}",
                source_row_ids=[f"source-row-{index + 1:03d}"],
                transform="bounded_jitter",
                seed=augmentation_plan.seed,
                parameters={"partition": "training"},
            )
            for index in range(augmentation_plan.count)
        ]
        candidates = [
            AdoptedCandidate(
                derived_row_id=item.derived_row_id,
                source_row_id=item.source_row_ids[0],
                partition="training",
                timestamp=f"2026-09-18T08:{index:02d}:01Z",
                equipment_id="PUMP-07",
                temperature_c=70.0,
                vibration_mm_s=1.5,
                pressure_bar=4.8,
                rpm=1480,
                failure_within_1h=0,
            )
            for index, item in enumerate(lineage)
        ]
        adopted = 0 if self.failed else len(lineage)
        return DaytonaAugmentationResult(
            sandbox_id="sandbox-augmentation",
            source_rows=len(rows),
            candidate_rows=len(lineage),
            adopted_rows=adopted,
            candidates=candidates,
            gates=gates,
            lineage=lineage,
        )


def _client(service: GateTraceService) -> TestClient:
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app)


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_health() -> None:
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "gatetrace"}


def test_run_response_shape_and_approved_verdict() -> None:
    client = _client(GateTraceService(nosana=FakeNosana(), daytona=FakeDaytona()))
    response = client.post(
        "/api/runs",
        json={"dataset_id": "clean", "research_goal": "Validate the cohort."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "COMPLETED"
    assert body["verdict"] == "APPROVED"
    assert body["dataset_id"] == "clean"
    assert body["sandbox_id"] == "sandbox-test"
    assert body["nosana_model_id"] == "demo/model"
    assert body["plan_generated"] is True
    assert body["summary_generated"] is True
    assert {gate["id"] for gate in body["gates"]} == {
        "required_columns",
        "missing_rate",
        "time_order",
        "forbidden_columns",
    }
    assert all(set(gate) == {"id", "status", "message_key", "evidence"} for gate in body["gates"])
    assert set(body["summary"]) == {"ko", "en"}
    assert all(set(item) == {"key", "status", "duration_ms"} for item in body["timeline"])


def test_nosana_fallback_is_marked_and_can_quarantine() -> None:
    client = _client(
        GateTraceService(nosana=FakeNosana(generated=False), daytona=FakeDaytona(failed=True))
    )
    response = client.post(
        "/api/runs",
        json={"dataset_id": "contaminated", "research_goal": "Check contamination."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "QUARANTINED"
    assert body["nosana_model_id"] is None
    assert body["plan_generated"] is False
    assert body["summary_generated"] is False


def test_daytona_failure_returns_502_without_local_fallback() -> None:
    daytona = FakeDaytona(execution_error=True)
    client = _client(GateTraceService(nosana=FakeNosana(), daytona=daytona))
    response = client.post(
        "/api/runs",
        json={"dataset_id": "clean", "research_goal": "Validate safely."},
    )

    assert daytona.called is True
    assert response.status_code == 502
    assert response.json() == {
        "detail": {
            "code": "DAYTONA_ERROR",
            "message_key": "error.daytona",
            "message": {
                "ko": "격리된 Daytona 샌드박스에서 검증을 완료하지 못했습니다.",
                "en": "Validation could not be completed in an isolated Daytona sandbox.",
            },
        }
    }


def test_augmentation_adopts_only_fully_passing_candidates_with_lineage() -> None:
    client = _client(GateTraceService(nosana=FakeNosana(), daytona=FakeDaytona()))
    response = client.post(
        "/api/augmentations",
        json={"dataset_id": "clean", "research_goal": "Expand the training cohort."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "COMPLETED"
    assert body["verdict"] == "ADOPTED"
    assert body["source_rows"] == 24
    assert body["candidate_rows"] == 6
    assert body["adopted_rows"] == 6
    assert len(body["adopted_candidates"]) == 6
    assert body["augmentation_plan"]["partition"] == "training"
    assert all(gate["status"] == "PASS" for gate in body["gates"])
    assert len(body["lineage"]) == 6
    assert all(item["source_row_ids"] for item in body["lineage"])
    assert all(item["transform"] == "bounded_jitter" for item in body["lineage"])
    assert {item["derived_row_id"] for item in body["lineage"]} == {
        item["derived_row_id"] for item in body["adopted_candidates"]
    }
    assert all(item["partition"] == "training" for item in body["adopted_candidates"])
    assert all(
        set(item)
        == {
            "derived_row_id",
            "source_row_id",
            "partition",
            "timestamp",
            "equipment_id",
            "temperature_c",
            "vibration_mm_s",
            "pressure_bar",
            "rpm",
            "failure_within_1h",
        }
        for item in body["adopted_candidates"]
    )


def test_augmentation_quarantines_entire_candidate_batch_when_gate_fails() -> None:
    client = _client(
        GateTraceService(nosana=FakeNosana(), daytona=FakeDaytona(failed=True))
    )
    response = client.post(
        "/api/augmentations",
        json={"dataset_id": "contaminated", "research_goal": "Expand safely."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "QUARANTINED"
    assert body["candidate_rows"] == 6
    assert body["adopted_rows"] == 0
    assert body["adopted_candidates"] == []
    assert any(gate["status"] == "FAIL" for gate in body["gates"])


def test_augmentation_daytona_failure_returns_502_without_local_fallback() -> None:
    daytona = FakeDaytona(execution_error=True)
    client = _client(GateTraceService(nosana=FakeNosana(), daytona=daytona))
    response = client.post(
        "/api/augmentations",
        json={"dataset_id": "clean", "research_goal": "Expand safely."},
    )

    assert daytona.called is True
    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "DAYTONA_ERROR"
    assert response.json()["detail"]["message_key"] == "error.daytona"


def test_malformed_nosana_response_uses_deterministic_plan() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "demo/model"}]})
        return httpx.Response(200, json={"choices": []})

    http_client = httpx.Client(
        base_url="https://inference.nosana.com/v1",
        transport=httpx.MockTransport(handler),
    )
    result = NosanaClient(api_key="test-key", http_client=http_client).create_plan(
        "Check quality.",
        {
            "dataset_id": "clean",
            "columns": [
                "timestamp",
                "equipment_id",
                "temperature_c",
                "vibration_mm_s",
                "pressure_bar",
                "rpm",
                "failure_within_1h",
            ],
            "row_count": 24,
        },
    )

    assert result.generated is False
    assert result.model_id is None
    assert result.plan == fallback_plan()


class _FakeProcess:
    def __init__(self, result: str, exit_code: int = 0) -> None:
        self._result = result
        self._exit_code = exit_code

    def code_run(self, source: str):
        assert "GATETRACE_RESULT=" in source
        return type("CodeRunResponse", (), {"result": self._result, "exit_code": self._exit_code})()


class _FakeSandbox:
    id = "sandbox-lifecycle"

    def __init__(self, process: _FakeProcess) -> None:
        self.process = process


class _FakeDaytonaClient:
    def __init__(self, process: _FakeProcess) -> None:
        self.sandbox = _FakeSandbox(process)
        self.deleted = False
        self.waited_for_delete = False

    def create(self) -> _FakeSandbox:
        return self.sandbox

    def delete(self, sandbox: _FakeSandbox, *, wait: bool = False) -> None:
        assert sandbox is self.sandbox
        self.deleted = True
        self.waited_for_delete = wait


def _passing_validator_output(plan: GatePlan) -> str:
    payload = []
    for gate in plan.gates:
        gate_id = "missing_rate" if gate.type == "max_missing_rate" else gate.type
        payload.append(
            {
                "id": gate_id,
                "status": "PASS",
                "message_key": f"gate.{gate_id}.pass",
                "evidence": {"source": "sandbox"},
            }
        )
    return RESULT_PREFIX + json.dumps(payload)


def test_daytona_runner_deletes_fresh_sandbox_after_validation() -> None:
    plan = fallback_plan()
    client = _FakeDaytonaClient(_FakeProcess(_passing_validator_output(plan)))
    runner = DaytonaRunner(
        api_key="test-key",
        api_url="https://daytona.invalid/api",
        client_factory=lambda _key, _url: client,
    )

    result = runner.run([], plan)

    assert result.sandbox_id == "sandbox-lifecycle"
    assert all(gate.status == "PASS" for gate in result.gates)
    assert client.deleted is True
    assert client.waited_for_delete is True


def test_daytona_runner_deletes_sandbox_on_validator_failure() -> None:
    client = _FakeDaytonaClient(_FakeProcess("validator failed", exit_code=1))
    runner = DaytonaRunner(
        api_key="test-key",
        api_url="https://daytona.invalid/api",
        client_factory=lambda _key, _url: client,
    )

    try:
        runner.run([], fallback_plan())
    except DaytonaExecutionError:
        pass
    else:
        raise AssertionError("expected DaytonaExecutionError")

    assert client.deleted is True
    assert client.waited_for_delete is True


def test_host_owned_augmentation_is_deterministic_and_fail_closed() -> None:
    augmentation_plan = fallback_augmentation_plan()
    gate_plan = fallback_plan()

    def execute(dataset_id: str):
        output = StringIO()
        source = DaytonaRunner._augmentation_source(
            get_dataset(dataset_id), augmentation_plan, gate_plan
        )
        with redirect_stdout(output):
            exec(source, {})
        return DaytonaRunner._parse_augmentation_result(
            output.getvalue(),
            f"sandbox-{dataset_id}",
            gate_plan,
            augmentation_plan,
            get_dataset(dataset_id),
        )

    clean = execute("clean")
    contaminated = execute("contaminated")

    assert clean.candidate_rows == clean.adopted_rows == 6
    assert all(gate.status == "PASS" for gate in clean.gates)
    assert clean.lineage[0].derived_row_id == "aug-20260919-011"
    assert clean.lineage[0].source_row_ids == ["source-row-011"]
    assert clean.lineage[0].parameters["partition"] == "training"
    assert {candidate.derived_row_id for candidate in clean.candidates} == {
        item.derived_row_id for item in clean.lineage
    }
    assert all(candidate.partition == "training" for candidate in clean.candidates)
    assert all(int(candidate.source_row_id[-3:]) <= 16 for candidate in clean.candidates)

    assert contaminated.candidate_rows > 0
    assert contaminated.adopted_rows == 0
    assert [gate.status for gate in contaminated.gates] == [
        "PASS",
        "FAIL",
        "FAIL",
        "FAIL",
    ]


def _valid_augmentation_payload() -> tuple[dict[str, object], AugmentationPlan, GatePlan, list[dict[str, object]]]:
    augmentation_plan = fallback_augmentation_plan()
    gate_plan = fallback_plan()
    rows = get_dataset("clean")
    output = StringIO()
    with redirect_stdout(output):
        exec(DaytonaRunner._augmentation_source(rows, augmentation_plan, gate_plan), {})
    line = next(
        item for item in output.getvalue().splitlines() if item.startswith(AUGMENT_RESULT_PREFIX)
    )
    return json.loads(line[len(AUGMENT_RESULT_PREFIX) :]), augmentation_plan, gate_plan, rows


def _parse_augmentation_payload(
    payload: dict[str, object],
    augmentation_plan: AugmentationPlan,
    gate_plan: GatePlan,
    rows: list[dict[str, object]],
) -> DaytonaAugmentationResult:
    return DaytonaRunner._parse_augmentation_result(
        AUGMENT_RESULT_PREFIX + json.dumps(payload),
        "sandbox-strict",
        gate_plan,
        augmentation_plan,
        rows,
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "fractional_count",
        "fractional_source_count",
        "fractional_adopted_count",
        "source_count",
        "over_plan_count",
        "duplicate_id",
        "wrong_seed",
        "fractional_seed",
        "wrong_partition",
        "disconnected_candidate",
        "unstable_derived_id",
        "non_training_source",
    ],
)
def test_augmentation_parser_rejects_inconsistent_sandbox_evidence(mutation: str) -> None:
    payload, augmentation_plan, gate_plan, rows = _valid_augmentation_payload()
    mutated = deepcopy(payload)

    if mutation == "fractional_count":
        mutated["candidate_rows"] = 6.0
    elif mutation == "fractional_source_count":
        mutated["source_rows"] = 24.0
    elif mutation == "fractional_adopted_count":
        mutated["adopted_rows"] = 6.0
    elif mutation == "source_count":
        mutated["source_rows"] = len(rows) - 1
    elif mutation == "over_plan_count":
        mutated["candidate_rows"] = augmentation_plan.count + 1
    elif mutation == "duplicate_id":
        mutated["candidates"][1]["derived_row_id"] = mutated["candidates"][0]["derived_row_id"]
    elif mutation == "wrong_seed":
        mutated["lineage"][0]["seed"] = augmentation_plan.seed + 1
    elif mutation == "fractional_seed":
        mutated["lineage"][0]["seed"] = float(augmentation_plan.seed)
    elif mutation == "wrong_partition":
        mutated["lineage"][0]["parameters"]["partition"] = "validation"
    elif mutation == "disconnected_candidate":
        mutated["candidates"][0]["derived_row_id"] = "aug-20260919-999"
    elif mutation == "unstable_derived_id":
        mutated["lineage"][0]["derived_row_id"] = "aug-20260919-999"
        mutated["candidates"][0]["derived_row_id"] = "aug-20260919-999"
    elif mutation == "non_training_source":
        mutated["lineage"][0]["source_row_ids"] = ["source-row-017"]
        mutated["candidates"][0]["source_row_id"] = "source-row-017"

    with pytest.raises(DaytonaExecutionError):
        _parse_augmentation_payload(mutated, augmentation_plan, gate_plan, rows)
