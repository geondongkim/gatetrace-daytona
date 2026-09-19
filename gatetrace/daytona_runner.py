from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from textwrap import dedent
from typing import Any

from daytona import Daytona, DaytonaConfig
from pydantic import TypeAdapter, ValidationError

from .models import AdoptedCandidate, AugmentationPlan, GatePlan, GateResult, LineageItem


RESULT_PREFIX = "GATETRACE_RESULT="
AUGMENT_RESULT_PREFIX = "GATETRACE_AUGMENT_RESULT="
_RESULT_ADAPTER = TypeAdapter(list[GateResult])
_LINEAGE_ADAPTER = TypeAdapter(list[LineageItem])
_CANDIDATE_ADAPTER = TypeAdapter(list[AdoptedCandidate])


class DaytonaExecutionError(RuntimeError):
    """Safe boundary error that deliberately omits SDK exception details."""


@dataclass(frozen=True)
class DaytonaRunResult:
    sandbox_id: str
    gates: list[GateResult]


@dataclass(frozen=True)
class DaytonaAugmentationResult:
    sandbox_id: str
    source_rows: int
    candidate_rows: int
    adopted_rows: int
    candidates: list[AdoptedCandidate]
    gates: list[GateResult]
    lineage: list[LineageItem]


class DaytonaRunner:
    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
        client_factory: Any | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else os.getenv("DAYTONA_API_KEY")
        self._api_url = api_url if api_url is not None else os.getenv("DAYTONA_API_URL")
        self._client_factory = client_factory

    def run(self, rows: list[dict[str, object]], plan: GatePlan) -> DaytonaRunResult:
        if not self._api_key or not self._api_url:
            raise DaytonaExecutionError("Daytona configuration is unavailable")

        try:
            client = self._build_client()
        except Exception:
            raise DaytonaExecutionError("Daytona client initialization failed") from None
        sandbox = None
        primary_error: Exception | None = None
        try:
            sandbox = client.create()
            sandbox_id = str(getattr(sandbox, "id", ""))
            if not sandbox_id:
                raise DaytonaExecutionError("Daytona returned a sandbox without an id")
            # The only executed code is this host-owned deterministic template. Nosana output is
            # constrained data passed through base64 JSON; it can never become Python source.
            response = sandbox.process.code_run(self._validator_source(rows, plan))
            if getattr(response, "exit_code", 1) != 0:
                raise DaytonaExecutionError("Daytona validator exited unsuccessfully")
            gates = self._parse_results(str(getattr(response, "result", "")), plan)
            return DaytonaRunResult(sandbox_id=sandbox_id, gates=gates)
        except DaytonaExecutionError as exc:
            primary_error = exc
            raise
        except Exception as exc:
            primary_error = exc
            raise DaytonaExecutionError("Daytona execution failed") from None
        finally:
            if sandbox is not None:
                try:
                    client.delete(sandbox, wait=True)
                except Exception:
                    if primary_error is None:
                        raise DaytonaExecutionError("Daytona sandbox cleanup failed") from None

    def augment_and_validate(
        self,
        rows: list[dict[str, object]],
        augmentation_plan: AugmentationPlan,
        gate_plan: GatePlan,
    ) -> DaytonaAugmentationResult:
        """Generate candidates and validate them inside one fresh Daytona sandbox."""
        if not self._api_key or not self._api_url:
            raise DaytonaExecutionError("Daytona configuration is unavailable")

        try:
            client = self._build_client()
        except Exception:
            raise DaytonaExecutionError("Daytona client initialization failed") from None
        sandbox = None
        primary_error: Exception | None = None
        try:
            sandbox = client.create()
            sandbox_id = str(getattr(sandbox, "id", ""))
            if not sandbox_id:
                raise DaytonaExecutionError("Daytona returned a sandbox without an id")
            response = sandbox.process.code_run(
                self._augmentation_source(rows, augmentation_plan, gate_plan)
            )
            if getattr(response, "exit_code", 1) != 0:
                raise DaytonaExecutionError("Daytona augmentation exited unsuccessfully")
            return self._parse_augmentation_result(
                str(getattr(response, "result", "")),
                sandbox_id,
                gate_plan,
                augmentation_plan,
                rows,
            )
        except DaytonaExecutionError as exc:
            primary_error = exc
            raise
        except Exception as exc:
            primary_error = exc
            raise DaytonaExecutionError("Daytona augmentation failed") from None
        finally:
            if sandbox is not None:
                try:
                    client.delete(sandbox, wait=True)
                except Exception:
                    if primary_error is None:
                        raise DaytonaExecutionError("Daytona sandbox cleanup failed") from None

    def _build_client(self):
        if self._client_factory is not None:
            return self._client_factory(self._api_key, self._api_url)
        config = DaytonaConfig(api_key=self._api_key, api_url=self._api_url)
        return Daytona(config)

    @staticmethod
    def _validator_source(rows: list[dict[str, object]], plan: GatePlan) -> str:
        payload = json.dumps(
            {"rows": rows, "plan": plan.model_dump(mode="json")},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        encoded = base64.b64encode(payload).decode("ascii")
        return dedent(
            f'''\
            import base64
            import datetime as dt
            import json

            payload = json.loads(base64.b64decode("{encoded}").decode("utf-8"))
            rows = payload["rows"]
            gates = payload["plan"]["gates"]

            def columns_in_rows():
                return set().union(*(set(row) for row in rows)) if rows else set()

            def parse_time(value):
                if not isinstance(value, str):
                    return None
                try:
                    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    return None

            results = []
            present_columns = columns_in_rows()
            for gate in gates:
                gate_type = gate["type"]
                if gate_type == "required_columns":
                    required = gate["columns"]
                    missing = sorted(set(required) - present_columns)
                    passed = not missing
                    evidence = {{"required": required, "present": sorted(present_columns), "missing": missing}}
                    gate_id = "required_columns"
                elif gate_type == "max_missing_rate":
                    columns = gate["columns"]
                    missing_count = sum(
                        row.get(column) is None or row.get(column) == ""
                        for row in rows
                        for column in columns
                    )
                    cell_count = len(rows) * len(columns)
                    rate = missing_count / cell_count if cell_count else 1.0
                    passed = rate <= gate["max_rate"]
                    evidence = {{"columns": columns, "missing_count": missing_count, "cell_count": cell_count, "missing_rate": rate, "max_rate": gate["max_rate"]}}
                    gate_id = "missing_rate"
                elif gate_type == "time_order":
                    time_column = gate["time_column"]
                    group_by = gate["group_by"]
                    previous = {{}}
                    violations = []
                    for index, row in enumerate(rows):
                        group = tuple(row.get(column) for column in group_by)
                        current = parse_time(row.get(time_column))
                        prior = previous.get(group)
                        if current is None or (prior is not None and current < prior):
                            violations.append(index)
                        if current is not None:
                            previous[group] = current
                    passed = not violations
                    evidence = {{"time_column": time_column, "group_by": group_by, "violations": violations, "rows_checked": len(rows)}}
                    gate_id = "time_order"
                elif gate_type == "forbidden_columns":
                    forbidden = gate["columns"]
                    found = sorted(set(forbidden) & present_columns)
                    passed = not found
                    evidence = {{"forbidden_columns": forbidden, "found": found}}
                    gate_id = "forbidden_columns"
                else:
                    raise ValueError("unsupported gate type")
                status = "PASS" if passed else "FAIL"
                results.append({{"id": gate_id, "status": status, "message_key": f"gate.{{gate_id}}.{{status.lower()}}", "evidence": evidence}})

            print("{RESULT_PREFIX}" + json.dumps(results, separators=(",", ":"), sort_keys=True))
            '''
        )

    @staticmethod
    def _augmentation_source(
        rows: list[dict[str, object]],
        augmentation_plan: AugmentationPlan,
        gate_plan: GatePlan,
    ) -> str:
        payload = json.dumps(
            {
                "rows": rows,
                "augmentation_plan": augmentation_plan.model_dump(mode="json"),
                "gate_plan": gate_plan.model_dump(mode="json"),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        encoded = base64.b64encode(payload).decode("ascii")
        return dedent(
            f'''\
            import base64
            import datetime as dt
            import json
            import random

            payload = json.loads(base64.b64decode("{encoded}").decode("utf-8"))
            source_rows = payload["rows"]
            augmentation = payload["augmentation_plan"]
            gates = payload["gate_plan"]["gates"]
            rng = random.Random(augmentation["seed"])

            def parse_time(value):
                if not isinstance(value, str):
                    return None
                try:
                    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    return None

            candidates = []
            lineage = []
            eligible_indices = []
            for index, row in enumerate(source_rows):
                if row.get("partition") != augmentation["partition"]:
                    continue
                try:
                    [float(row[column]) for column in augmentation["feature_columns"]]
                except (KeyError, TypeError, ValueError):
                    continue
                if parse_time(row.get("timestamp")) is None:
                    continue
                eligible_indices.append(index)
            eligible_indices = eligible_indices[-augmentation["count"]:]
            count = min(augmentation["count"], len(eligible_indices))
            candidate_by_source = {{}}
            for source_index in eligible_indices[:count]:
                source = dict(source_rows[source_index])
                derived = dict(source)
                derived["timestamp"] = (parse_time(source["timestamp"]) + dt.timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
                deltas = {{}}
                for column in augmentation["feature_columns"]:
                    value = float(source[column])
                    relative_delta = rng.uniform(-augmentation["max_relative_delta"], augmentation["max_relative_delta"])
                    decimals = 0 if column == "rpm" else 3
                    derived[column] = str(round(value * (1 + relative_delta), decimals))
                    deltas[column] = round(relative_delta, 6)
                source_id = f"source-row-{{source_index + 1:03d}}"
                derived_id = f"aug-{{augmentation['seed']}}-{{source_index + 1:03d}}"
                derived["derived_row_id"] = derived_id
                derived["source_row_id"] = source_id
                derived["partition"] = augmentation["partition"]
                candidate_by_source[source_index] = derived
                candidates.append({{
                    "derived_row_id": derived_id,
                    "source_row_id": source_id,
                    "partition": derived["partition"],
                    "timestamp": derived["timestamp"],
                    "equipment_id": derived["equipment_id"],
                    "temperature_c": float(derived["temperature_c"]),
                    "vibration_mm_s": float(derived["vibration_mm_s"]),
                    "pressure_bar": float(derived["pressure_bar"]),
                    "rpm": int(float(derived["rpm"])),
                    "failure_within_1h": int(derived["failure_within_1h"]),
                }})
                lineage.append({{
                    "derived_row_id": derived_id,
                    "source_row_ids": [source_id],
                    "transform": augmentation["method"],
                    "seed": augmentation["seed"],
                    "parameters": {{"relative_deltas": deltas, "partition": augmentation["partition"]}},
                }})

            combined_rows = []
            for source_index, row in enumerate(source_rows):
                combined_rows.append(dict(row))
                if source_index in candidate_by_source:
                    combined_rows.append(candidate_by_source[source_index])
            present_columns = set().union(*(set(row) for row in combined_rows)) if combined_rows else set()
            results = []
            for gate in gates:
                gate_type = gate["type"]
                if gate_type == "required_columns":
                    required = gate["columns"]
                    missing = sorted(set(required) - present_columns)
                    passed = not missing
                    evidence = {{"required": required, "present": sorted(present_columns), "missing": missing}}
                    gate_id = "required_columns"
                elif gate_type == "max_missing_rate":
                    columns = gate["columns"]
                    missing_count = sum(
                        row.get(column) is None or row.get(column) == ""
                        for row in combined_rows
                        for column in columns
                    )
                    cell_count = len(combined_rows) * len(columns)
                    rate = missing_count / cell_count if cell_count else 1.0
                    passed = rate <= gate["max_rate"]
                    evidence = {{"columns": columns, "missing_count": missing_count, "cell_count": cell_count, "missing_rate": rate, "max_rate": gate["max_rate"]}}
                    gate_id = "missing_rate"
                elif gate_type == "time_order":
                    time_column = gate["time_column"]
                    group_by = gate["group_by"]
                    previous = {{}}
                    violations = []
                    for index, row in enumerate(combined_rows):
                        group = tuple(row.get(column) for column in group_by)
                        current = parse_time(row.get(time_column))
                        prior = previous.get(group)
                        if current is None or (prior is not None and current < prior):
                            violations.append(index)
                        if current is not None:
                            previous[group] = current
                    passed = not violations
                    evidence = {{"time_column": time_column, "group_by": group_by, "violations": violations, "rows_checked": len(combined_rows)}}
                    gate_id = "time_order"
                elif gate_type == "forbidden_columns":
                    forbidden = gate["columns"]
                    found = sorted(set(forbidden) & present_columns)
                    passed = not found
                    evidence = {{"forbidden_columns": forbidden, "found": found}}
                    gate_id = "forbidden_columns"
                else:
                    raise ValueError("unsupported gate type")
                status = "PASS" if passed else "FAIL"
                results.append({{"id": gate_id, "status": status, "message_key": f"gate.{{gate_id}}.{{status.lower()}}", "evidence": evidence}})

            adopted_rows = len(candidates) if all(item["status"] == "PASS" for item in results) else 0
            result = {{
                "source_rows": len(source_rows),
                "candidate_rows": len(candidates),
                "adopted_rows": adopted_rows,
                "candidates": candidates,
                "gates": results,
                "lineage": lineage,
            }}
            print("{AUGMENT_RESULT_PREFIX}" + json.dumps(result, separators=(",", ":"), sort_keys=True))
            '''
        )

    @staticmethod
    def _parse_results(output: str, plan: GatePlan) -> list[GateResult]:
        payload: str | None = None
        for line in output.splitlines():
            if line.startswith(RESULT_PREFIX):
                payload = line[len(RESULT_PREFIX) :]
        if payload is None:
            raise DaytonaExecutionError("Daytona validator returned no structured result")
        try:
            parsed = json.loads(payload)
            gates = _RESULT_ADAPTER.validate_python(parsed)
        except (json.JSONDecodeError, ValidationError):
            raise DaytonaExecutionError("Daytona validator result was malformed") from None
        expected_ids = [
            "missing_rate" if gate.type == "max_missing_rate" else gate.type
            for gate in plan.gates
        ]
        if [gate.id for gate in gates] != expected_ids:
            raise DaytonaExecutionError("Daytona validator result did not match the gate plan")
        return gates

    @staticmethod
    def _parse_augmentation_result(
        output: str,
        sandbox_id: str,
        gate_plan: GatePlan,
        augmentation_plan: AugmentationPlan,
        input_rows: list[dict[str, object]],
    ) -> DaytonaAugmentationResult:
        payload: str | None = None
        for line in output.splitlines():
            if line.startswith(AUGMENT_RESULT_PREFIX):
                payload = line[len(AUGMENT_RESULT_PREFIX) :]
        if payload is None:
            raise DaytonaExecutionError("Daytona augmentation returned no structured result")
        try:
            parsed = json.loads(payload)
            counts = [parsed["source_rows"], parsed["candidate_rows"], parsed["adopted_rows"]]
            if any(type(value) is not int for value in counts):
                raise TypeError("augmentation counts must be strict integers")
            if not isinstance(parsed["lineage"], list) or not isinstance(parsed["candidates"], list):
                raise TypeError("augmentation collections must be lists")
            if any(type(item.get("seed")) is not int for item in parsed["lineage"]):
                raise TypeError("lineage seeds must be strict integers")
            gates = _RESULT_ADAPTER.validate_python(parsed["gates"])
            lineage = _LINEAGE_ADAPTER.validate_python(parsed["lineage"])
            candidates = _CANDIDATE_ADAPTER.validate_python(parsed["candidates"])
            source_rows, candidate_rows, adopted_rows = counts
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, ValidationError):
            raise DaytonaExecutionError("Daytona augmentation result was malformed") from None
        expected_ids = [
            "missing_rate" if gate.type == "max_missing_rate" else gate.type
            for gate in gate_plan.gates
        ]
        if [gate.id for gate in gates] != expected_ids:
            raise DaytonaExecutionError("Daytona augmentation gates did not match the plan")
        if source_rows != len(input_rows):
            raise DaytonaExecutionError("Daytona augmentation source count was inconsistent")
        if candidate_rows > augmentation_plan.count:
            raise DaytonaExecutionError("Daytona augmentation exceeded the candidate limit")
        all_pass = all(gate.status == "PASS" for gate in gates)
        if (
            candidate_rows != len(lineage)
            or candidate_rows != len(candidates)
            or adopted_rows != (candidate_rows if all_pass else 0)
        ):
            raise DaytonaExecutionError("Daytona augmentation adoption evidence was inconsistent")
        if source_rows < 0 or candidate_rows < 0 or adopted_rows < 0:
            raise DaytonaExecutionError("Daytona augmentation counts were invalid")
        lineage_ids = [item.derived_row_id for item in lineage]
        candidate_ids = [item.derived_row_id for item in candidates]
        if len(lineage_ids) != len(set(lineage_ids)) or len(candidate_ids) != len(set(candidate_ids)):
            raise DaytonaExecutionError("Daytona augmentation ids were not unique")
        if set(lineage_ids) != set(candidate_ids):
            raise DaytonaExecutionError("Daytona candidates were not connected to lineage")
        training_source_ids = {
            f"source-row-{index + 1:03d}"
            for index, row in enumerate(input_rows)
            if row.get("partition") == augmentation_plan.partition
        }
        candidate_by_id = {item.derived_row_id: item for item in candidates}
        for item in lineage:
            candidate = candidate_by_id[item.derived_row_id]
            if item.seed != augmentation_plan.seed or item.transform != augmentation_plan.method:
                raise DaytonaExecutionError("Daytona lineage did not match the augmentation plan")
            if item.parameters.get("partition") != augmentation_plan.partition:
                raise DaytonaExecutionError("Daytona lineage partition was inconsistent")
            if len(item.source_row_ids) != 1 or item.source_row_ids[0] not in training_source_ids:
                raise DaytonaExecutionError("Daytona lineage referenced a non-training row")
            source_suffix = item.source_row_ids[0].removeprefix("source-row-")
            expected_derived_id = f"aug-{augmentation_plan.seed}-{source_suffix}"
            if item.derived_row_id != expected_derived_id:
                raise DaytonaExecutionError("Daytona derived id was not stable for its source")
            if candidate.partition != augmentation_plan.partition:
                raise DaytonaExecutionError("Daytona candidate partition was inconsistent")
            if candidate.source_row_id != item.source_row_ids[0]:
                raise DaytonaExecutionError("Daytona candidate source was inconsistent")
        return DaytonaAugmentationResult(
            sandbox_id=sandbox_id,
            source_rows=source_rows,
            candidate_rows=candidate_rows,
            adopted_rows=adopted_rows,
            candidates=candidates,
            gates=gates,
            lineage=lineage,
        )
