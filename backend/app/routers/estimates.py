from fastapi import APIRouter, Query
from app.schemas.estimate import EstimateRequest
from app.services import estimate_service
router = APIRouter()
@router.get("/estimate")
def get_est(
    box_id: int = Query(...),
    overlap: float | None = None,
    wrap_style: str = "cross",
    save: bool = False,
    pad_enabled: bool = False,
    pad_pct: float | None = None,
):
    return estimate_service.run_estimate(box_id, overlap, wrap_style, save, "", pad_enabled, pad_pct)
@router.post("/estimate")
def post_est(body: EstimateRequest):
    return estimate_service.run_estimate(
        body.box_id, body.overlap, body.wrap_style, body.save, body.note,
        body.pad_enabled, body.pad_pct,
    )
