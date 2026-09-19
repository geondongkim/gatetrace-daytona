from __future__ import annotations

import time
import uuid
from typing import Callable

from .datasets import dataset_profile, get_dataset
from .daytona_runner import DaytonaRunner
from .models import (
    AugmentationRequest,
    AugmentationResponse,
    RunRequest,
    RunResponse,
    TimelineItem,
)
from .nosana import NosanaClient, fallback_plan


class GateTraceService:
    def __init__(
        self,
        nosana: NosanaClient | None = None,
        daytona: DaytonaRunner | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._nosana = nosana or NosanaClient()
        self._daytona = daytona or DaytonaRunner()
        self._clock = clock

    def run(self, request: RunRequest) -> RunResponse:
        started = self._clock()
        timeline: list[TimelineItem] = []

        step = self._clock()
        plan_result = self._nosana.create_plan(
            request.research_goal, dataset_profile(request.dataset_id)
        )
        timeline.append(
            TimelineItem(
                key="nosana.gate_spec",
                status="DONE" if plan_result.generated else "ERROR",
                duration_ms=self._elapsed(step),
            )
        )

        step = self._clock()
        daytona_result = self._daytona.run(
            get_dataset(request.dataset_id), plan_result.plan
        )
        timeline.append(
            TimelineItem(
                key="daytona.validation",
                status="DONE",
                duration_ms=self._elapsed(step),
            )
        )

        gates = [gate.model_dump(mode="json") for gate in daytona_result.gates]
        verdict = "APPROVED" if all(gate.status == "PASS" for gate in daytona_result.gates) else "QUARANTINED"

        step = self._clock()
        summary_result = self._nosana.create_summary(
            plan_result.model_id, verdict, gates
        )
        timeline.append(
            TimelineItem(
                key="nosana.summary",
                status="DONE" if summary_result.generated else "ERROR",
                duration_ms=self._elapsed(step),
            )
        )

        return RunResponse(
            run_id=uuid.uuid4().hex,
            verdict=verdict,
            dataset_id=request.dataset_id,
            sandbox_id=daytona_result.sandbox_id,
            nosana_model_id=plan_result.model_id,
            duration_ms=self._elapsed(started),
            plan_generated=plan_result.generated,
            summary_generated=summary_result.generated,
            gates=daytona_result.gates,
            summary=summary_result.summary,
            timeline=timeline,
        )

    def augment(self, request: AugmentationRequest) -> AugmentationResponse:
        started = self._clock()
        timeline: list[TimelineItem] = []
        rows = get_dataset(request.dataset_id)
        profile = dataset_profile(request.dataset_id)

        step = self._clock()
        plan_result = self._nosana.create_augmentation_plan(
            request.research_goal, profile
        )
        timeline.append(
            TimelineItem(
                key="nosana.augmentation_spec",
                status="DONE" if plan_result.generated else "ERROR",
                duration_ms=self._elapsed(step),
            )
        )

        step = self._clock()
        daytona_result = self._daytona.augment_and_validate(
            rows, plan_result.plan, fallback_plan()
        )
        timeline.append(
            TimelineItem(
                key="daytona.augmentation_validation",
                status="DONE",
                duration_ms=self._elapsed(step),
            )
        )

        gates = [gate.model_dump(mode="json") for gate in daytona_result.gates]
        verdict = (
            "ADOPTED"
            if daytona_result.adopted_rows == daytona_result.candidate_rows
            and daytona_result.candidate_rows > 0
            and all(gate.status == "PASS" for gate in daytona_result.gates)
            else "QUARANTINED"
        )

        step = self._clock()
        summary_result = self._nosana.create_augmentation_summary(
            plan_result.model_id, verdict, gates
        )
        timeline.append(
            TimelineItem(
                key="nosana.summary",
                status="DONE" if summary_result.generated else "ERROR",
                duration_ms=self._elapsed(step),
            )
        )

        return AugmentationResponse(
            run_id=uuid.uuid4().hex,
            verdict=verdict,
            dataset_id=request.dataset_id,
            sandbox_id=daytona_result.sandbox_id,
            nosana_model_id=plan_result.model_id,
            duration_ms=self._elapsed(started),
            plan_generated=plan_result.generated,
            summary_generated=summary_result.generated,
            augmentation_plan=plan_result.plan,
            source_rows=daytona_result.source_rows,
            candidate_rows=daytona_result.candidate_rows,
            adopted_rows=daytona_result.adopted_rows,
            adopted_candidates=(
                daytona_result.candidates if verdict == "ADOPTED" else []
            ),
            gates=daytona_result.gates,
            lineage=daytona_result.lineage,
            summary=summary_result.summary,
            timeline=timeline,
        )

    def _elapsed(self, started: float) -> int:
        return max(0, round((self._clock() - started) * 1000))
