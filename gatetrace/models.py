from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


GateType = Literal[
    "required_columns", "max_missing_rate", "time_order", "forbidden_columns"
]
GateId = Literal[
    "required_columns", "missing_rate", "time_order", "forbidden_columns"
]
SafeColumn = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
    ),
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RequiredColumnsGate(StrictModel):
    type: Literal["required_columns"]
    columns: list[SafeColumn] = Field(min_length=1, max_length=32)


class MaxMissingRateGate(StrictModel):
    type: Literal["max_missing_rate"]
    columns: list[SafeColumn] = Field(min_length=1, max_length=32)
    max_rate: float = Field(ge=0, le=1)


class TimeOrderGate(StrictModel):
    type: Literal["time_order"]
    time_column: SafeColumn
    group_by: list[SafeColumn] = Field(default_factory=list, max_length=8)


class ForbiddenColumnsGate(StrictModel):
    type: Literal["forbidden_columns"]
    columns: list[SafeColumn] = Field(min_length=1, max_length=32)


GateSpec = Annotated[
    RequiredColumnsGate
    | MaxMissingRateGate
    | TimeOrderGate
    | ForbiddenColumnsGate,
    Field(discriminator="type"),
]


class GatePlan(StrictModel):
    gates: list[GateSpec] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def unique_gate_types(self) -> "GatePlan":
        types = [gate.type for gate in self.gates]
        if len(types) != len(set(types)):
            raise ValueError("gate types must be unique")
        required_types = {
            "required_columns",
            "max_missing_rate",
            "time_order",
            "forbidden_columns",
        }
        if set(types) != required_types:
            raise ValueError("gate plan must contain every supported gate type exactly once")
        return self


class RunRequest(StrictModel):
    dataset_id: Literal["clean", "contaminated"]
    research_goal: str = Field(min_length=1, max_length=1000)


class GateResult(StrictModel):
    id: GateId
    status: Literal["PASS", "FAIL"]
    message_key: str = Field(min_length=1, max_length=100)
    evidence: dict[str, Any]


class BilingualSummary(StrictModel):
    ko: str = Field(min_length=1, max_length=2000)
    en: str = Field(min_length=1, max_length=2000)


class TimelineItem(StrictModel):
    key: str = Field(min_length=1, max_length=100)
    status: Literal["DONE", "ERROR"]
    duration_ms: int | None = Field(default=None, ge=0)


class RunResponse(StrictModel):
    run_id: str
    status: Literal["COMPLETED"] = "COMPLETED"
    verdict: Literal["APPROVED", "QUARANTINED"]
    dataset_id: Literal["clean", "contaminated"]
    sandbox_id: str
    nosana_model_id: str | None
    duration_ms: int = Field(ge=0)
    plan_generated: bool
    summary_generated: bool
    gates: list[GateResult]
    summary: BilingualSummary
    timeline: list[TimelineItem]


class ErrorMessage(StrictModel):
    ko: str
    en: str


class DaytonaErrorDetail(StrictModel):
    code: Literal["DAYTONA_ERROR"] = "DAYTONA_ERROR"
    message_key: Literal["error.daytona"] = "error.daytona"
    message: ErrorMessage
