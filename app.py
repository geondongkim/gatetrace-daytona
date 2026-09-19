from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from gatetrace.daytona_runner import DaytonaExecutionError
from gatetrace.models import (
    AugmentationRequest,
    AugmentationResponse,
    DaytonaErrorDetail,
    ErrorMessage,
    RunRequest,
    RunResponse,
)
from gatetrace.service import GateTraceService


app = FastAPI(title="GateTrace API", version="1.0.0")


def get_service() -> GateTraceService:
    return GateTraceService()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "gatetrace"}


@app.post("/api/runs", response_model=RunResponse)
def create_run(
    request: RunRequest,
    service: GateTraceService = Depends(get_service),
) -> RunResponse:
    try:
        return service.run(request)
    except DaytonaExecutionError:
        detail = DaytonaErrorDetail(
            message=ErrorMessage(
                ko="격리된 Daytona 샌드박스에서 검증을 완료하지 못했습니다.",
                en="Validation could not be completed in an isolated Daytona sandbox.",
            )
        )
        raise HTTPException(status_code=502, detail=detail.model_dump(mode="json")) from None


@app.post("/api/augmentations", response_model=AugmentationResponse)
def create_augmentation(
    request: AugmentationRequest,
    service: GateTraceService = Depends(get_service),
) -> AugmentationResponse:
    try:
        return service.augment(request)
    except DaytonaExecutionError:
        detail = DaytonaErrorDetail(
            message=ErrorMessage(
                ko="격리된 Daytona 샌드박스에서 증강과 재검증을 완료하지 못했습니다.",
                en="Augmentation and re-validation could not be completed in an isolated Daytona sandbox.",
            )
        )
        raise HTTPException(status_code=502, detail=detail.model_dump(mode="json")) from None


_static_dir = Path(__file__).resolve().parent / "static"
if _static_dir.is_dir():
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
