from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import ValidationError

from .models import BilingualSummary, GatePlan


NOSANA_BASE_URL = "https://inference.nosana.com/v1"


@dataclass(frozen=True)
class NosanaPlanResult:
    plan: GatePlan
    model_id: str | None
    generated: bool


@dataclass(frozen=True)
class NosanaSummaryResult:
    summary: BilingualSummary
    generated: bool


def fallback_plan() -> GatePlan:
    return GatePlan.model_validate(
        {
            "gates": [
                {
                    "type": "required_columns",
                    "columns": [
                        "timestamp",
                        "equipment_id",
                        "temperature_c",
                        "vibration_mm_s",
                        "pressure_bar",
                        "rpm",
                        "failure_within_1h",
                    ],
                },
                {
                    "type": "max_missing_rate",
                    "columns": [
                        "temperature_c",
                        "vibration_mm_s",
                        "pressure_bar",
                        "rpm",
                    ],
                    "max_rate": 0.05,
                },
                {
                    "type": "time_order",
                    "time_column": "timestamp",
                    "group_by": ["equipment_id"],
                },
                {
                    "type": "forbidden_columns",
                    "columns": [
                        "failure_timestamp",
                        "future_failure",
                        "future_failure_label",
                        "time_to_failure_minutes",
                    ],
                },
            ]
        }
    )


def fallback_summary(verdict: str, gates: list[dict[str, Any]]) -> BilingualSummary:
    failed = [gate["id"] for gate in gates if gate["status"] == "FAIL"]
    if failed:
        joined = ", ".join(failed)
        return BilingualSummary(
            ko=f"검증 결과 격리되었습니다. 실패 게이트: {joined}.",
            en=f"The dataset was quarantined. Failed gates: {joined}.",
        )
    return BilingualSummary(
        ko="선택된 모든 데이터 게이트를 통과하여 승인되었습니다.",
        en="The dataset was approved after passing every selected gate.",
    )


class NosanaClient:
    """Small, fail-closed client for Nosana's OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        preferred_model: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else os.getenv("NOSANA_API_KEY")
        self._preferred_model = (
            preferred_model if preferred_model is not None else os.getenv("NOSANA_MODEL")
        )
        self._client = http_client

    def create_plan(
        self, research_goal: str, profile: dict[str, object]
    ) -> NosanaPlanResult:
        fallback = fallback_plan()
        if not self._api_key:
            return NosanaPlanResult(fallback, None, False)

        try:
            with self._client_context() as client:
                model_id = self._discover_model(client)
                if model_id is None:
                    return NosanaPlanResult(fallback, None, False)
                raw = self._chat_json(
                    client,
                    model_id,
                    system=(
                        "You design data-quality gates. Return only JSON matching the supplied "
                        "schema. Never return code. Use only listed dataset columns."
                    ),
                    user=json.dumps(
                        {"research_goal": research_goal, "dataset_profile": profile},
                        ensure_ascii=False,
                    ),
                    schema=GatePlan.model_json_schema(),
                    schema_name="gate_spec",
                )
                plan = GatePlan.model_validate(raw)
                allowed_columns = set(profile.get("columns", []))
                for gate in plan.gates:
                    referenced: list[str]
                    if gate.type in {"required_columns", "forbidden_columns"}:
                        referenced = list(gate.columns)
                    elif gate.type == "max_missing_rate":
                        referenced = list(gate.columns)
                    else:
                        referenced = [gate.time_column, *gate.group_by]
                    permitted = (
                        allowed_columns | self._safe_policy_columns()
                        if gate.type == "forbidden_columns"
                        else allowed_columns
                    )
                    if not set(referenced).issubset(permitted):
                        raise ValueError("gate plan referenced an unsupported column")
                return NosanaPlanResult(plan, model_id, True)
        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
            IndexError,
            ValidationError,
            json.JSONDecodeError,
        ):
            return NosanaPlanResult(fallback, None, False)

    def create_summary(
        self,
        model_id: str | None,
        verdict: str,
        gates: list[dict[str, Any]],
    ) -> NosanaSummaryResult:
        fallback = fallback_summary(verdict, gates)
        if not self._api_key or not model_id:
            return NosanaSummaryResult(fallback, False)
        try:
            with self._client_context() as client:
                raw = self._chat_json(
                    client,
                    model_id,
                    system=(
                        "Explain the provided deterministic gate results concisely in Korean and "
                        "English. Return only JSON matching the supplied schema. Do not change the verdict."
                    ),
                    user=json.dumps({"verdict": verdict, "gates": gates}, ensure_ascii=False),
                    schema=BilingualSummary.model_json_schema(),
                    schema_name="bilingual_summary",
                )
                return NosanaSummaryResult(BilingualSummary.model_validate(raw), True)
        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
            IndexError,
            ValidationError,
            json.JSONDecodeError,
        ):
            return NosanaSummaryResult(fallback, False)

    def _client_context(self):
        if self._client is not None:
            return _BorrowedClient(self._client)
        return httpx.Client(
            base_url=NOSANA_BASE_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=httpx.Timeout(20.0),
        )

    def _discover_model(self, client: httpx.Client) -> str | None:
        response = client.get("/models")
        response.raise_for_status()
        payload = response.json()
        model_ids = sorted(
            item["id"]
            for item in payload["data"]
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        )
        if not model_ids:
            return None
        if self._preferred_model:
            return self._preferred_model if self._preferred_model in model_ids else None
        return model_ids[0]

    def _chat_json(
        self,
        client: httpx.Client,
        model_id: str,
        *,
        system: str,
        user: str,
        schema: dict[str, Any],
        schema_name: str,
    ) -> dict[str, Any]:
        response = client.post(
            "/chat/completions",
            json={
                "model": model_id,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {"name": schema_name, "strict": True, "schema": schema},
                },
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise ValueError("Nosana response content was not JSON text")
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Nosana response must be a JSON object")
        return parsed

    @staticmethod
    def _safe_policy_columns() -> set[str]:
        return {
            "email",
            "phone",
            "ssn",
            "resident_registration_number",
            "failure_timestamp",
            "future_failure",
            "future_failure_label",
            "time_to_failure_minutes",
        }


class _BorrowedClient:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def __enter__(self) -> httpx.Client:
        return self._client

    def __exit__(self, *_args: object) -> None:
        return None
