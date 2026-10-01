from fastapi import APIRouter, HTTPException
from app.repositories import history as repo
from app.services.pad_open_view import pad_projection

router = APIRouter()

@router.get("/runs")
def runs(limit: int = 50):
    return {"items": repo.list_runs(limit)}

@router.get("/runs/{run_id}")
def run_detail(run_id: int):
    r = repo.get_run(run_id)
    if not r:
        raise HTTPException(404)
    # 投影与列表、详情同源：只复制写入时钉住的字段，不剥垫、不重抬
    r["open_projection"] = pad_projection(r.get("result") or {})
    return r
