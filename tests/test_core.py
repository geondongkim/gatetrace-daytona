from __future__ import annotations

import json
from dataclasses import dataclass

import httpx
from fastapi.testclient import TestClient

from app import app, get_service
from gatetrace.daytona_runner import (
    RESULT_PREFIX,
    DaytonaExecutionError,
    DaytonaRunResult,
    DaytonaRunner,
)
from gatetrace.models import BilingualSummary, GatePlan, GateResult
from gatetrace.nosana import (
    NosanaClient,
    NosanaPlanResult,
    NosanaSummaryResult,
    fallback_plan,
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
