from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from textwrap import dedent
from typing import Any

from daytona import Daytona, DaytonaConfig
from pydantic import TypeAdapter, ValidationError

from .models import GatePlan, GateResult


RESULT_PREFIX = "GATETRACE_RESULT="
_RESULT_ADAPTER = TypeAdapter(list[GateResult])


class DaytonaExecutionError(RuntimeError):
    """Safe boundary error that deliberately omits SDK exception details."""


@dataclass(frozen=True)
class DaytonaRunResult:
    sandbox_id: str
    gates: list[GateResult]


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
