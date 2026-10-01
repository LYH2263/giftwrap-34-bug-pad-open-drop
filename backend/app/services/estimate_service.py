from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.repositories import boxes, history, settings_repo

def run_estimate(box_id, overlap, wrap_style, save, note, pad_enabled=False, pad_pct=None):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")

    enabled = bool(pad_enabled)
    # 开启时百分比缺省取系统默认；关闭时不用、置 0
    if enabled:
        pct = settings_repo.get_pad_pct_default() if pad_pct is None else float(pad_pct)
        if pct < 0:
            # 负数直接失败，且发生在任何写库动作之前，不落库
            raise HTTPException(422, "pad_pct must not be negative")
    else:
        pct = 0.0

    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    calc = paper_area(box["length"], box["width"], box["height"], ov, enabled, pct)
    # ribbon 永远只跟基础三边，与防压垫无关
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    stored = {**calc, "ribbon": ribbon}
    run_id = history.insert_run(box_id, ov, stored, note) if save else None
    return {"box": box, "run_id": run_id, **calc, "ribbon": ribbon}
