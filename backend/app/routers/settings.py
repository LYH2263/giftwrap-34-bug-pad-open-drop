from fastapi import APIRouter, HTTPException
from app.repositories import settings_repo
from app.schemas.estimate import SettingsUpdate
router = APIRouter()
@router.get("/settings")
def settings(): return settings_repo.get_all()
@router.post("/settings")
def update_settings(body: SettingsUpdate):
    if body.pad_pct_default < 0:
        raise HTTPException(422, "pad_pct_default must not be negative")
    settings_repo.set_pad_pct_default(body.pad_pct_default)
    return settings_repo.get_all()
