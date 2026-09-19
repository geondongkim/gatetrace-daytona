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


class AugmentationPlan(StrictModel):
    method: Literal["bounded_jitter"] = "bounded_jitter"
    partition: Literal["training"] = "training"
    count: int = Field(default=6, ge=1, le=12)
    seed: int = Field(default=20260919, ge=0, le=2_147_483_647)
    feature_columns: list[SafeColumn] = Field(min_length=1, max_length=8)
    max_relative_delta: float = Field(default=0.01, gt=0, le=0.05)

    @model_validator(mode="after")
    def supported_features_only(self) -> "AugmentationPlan":
        supported = {
            "temperature_c",
            "vibration_mm_s",
            "pressure_bar",
            "rpm",
        }
        if not set(self.feature_columns).issubset(supported):
            raise ValueError("augmentation plan referenced an unsupported feature")
        if len(self.feature_columns) != len(set(self.feature_columns)):
            raise ValueError("augmentation feature columns must be unique")
        return self


class AugmentationRequest(StrictModel):
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


class LineageItem(StrictModel):
    derived_row_id: str = Field(
        min_length=1, max_length=100, pattern=r"^aug-[0-9]+-[0-9]{3}$"
    )
    source_row_ids: list[str] = Field(min_length=1, max_length=4)
    transform: Literal["bounded_jitter"]
    seed: int = Field(ge=0)
    parameters: dict[str, Any]


class AdoptedCandidate(StrictModel):
    derived_row_id: str = Field(
        min_length=1, max_length=100, pattern=r"^aug-[0-9]+-[0-9]{3}$"
    )
    source_row_id: str = Field(
        min_length=1, max_length=100, pattern=r"^source-row-[0-9]{3}$"
    )
    partition: Literal["training"]
    timestamp: str = Field(min_length=1, max_length=64)
    equipment_id: str = Field(min_length=1, max_length=64)
    temperature_c: float
    vibration_mm_s: float
    pressure_bar: float
    rpm: int
    failure_within_1h: Literal[0, 1]


class AugmentationResponse(StrictModel):
    run_id: str
    status: Literal["COMPLETED"] = "COMPLETED"
    verdict: Literal["ADOPTED", "QUARANTINED"]
    dataset_id: Literal["clean", "contaminated"]
    sandbox_id: str
    nosana_model_id: str | None
    duration_ms: int = Field(ge=0)
    plan_generated: bool
    summary_generated: bool
    augmentation_plan: AugmentationPlan
    source_rows: int = Field(ge=0)
    candidate_rows: int = Field(ge=0)
    adopted_rows: int = Field(ge=0)
    adopted_candidates: list[AdoptedCandidate]
    gates: list[GateResult]
    lineage: list[LineageItem]
    summary: BilingualSummary
    timeline: list[TimelineItem]


class ErrorMessage(StrictModel):
    ko: str
    en: str


class DaytonaErrorDetail(StrictModel):
    code: Literal["DAYTONA_ERROR"] = "DAYTONA_ERROR"
    message_key: Literal["error.daytona"] = "error.daytona"
    message: ErrorMessage
