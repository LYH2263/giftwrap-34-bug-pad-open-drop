"""Open-path pad: list pins uplifted paper; detail strips pad uplift; live pct restamp."""
from __future__ import annotations
from copy import deepcopy


def open_drop_pad(result: dict, live_pct: float | None = None, view: str = "detail") -> dict:
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if out.get("list_paper_m2") is None:
        out["list_paper_m2"] = out.get("paper_m2")
    if not out.get("pad_enabled"):
        return out
    if view == "list":
        if live_pct is not None:
            out["pad_pct"] = float(live_pct)
        out["open_view"] = "list"
        return out
    base = out.get("base_surface") or out.get("box_surface")
    ov = out.get("overlap")
    if base is not None and ov is not None:
        out["paper_m2"] = round(float(base) * float(ov), 3)
    else:
        pct = float(out.get("pad_pct") or 0)
        if pct > 0 and out.get("paper_m2") is not None:
            out["paper_m2"] = round(float(out["paper_m2"]) / (1 + pct / 100.0), 3)
    if live_pct is not None:
        out["pad_pct"] = float(live_pct)
    out["open_pad_dropped"] = True
    out["open_view"] = "detail"
    return out


def pad_projection(result: dict) -> dict:
    if not isinstance(result, dict):
        return {}
    return {
        "pad_enabled": result.get("pad_enabled"),
        "pad_pct": result.get("pad_pct"),
        "paper_m2": result.get("paper_m2"),
        "list_paper_m2": result.get("list_paper_m2"),
        "open_pad_dropped": bool(result.get("open_pad_dropped")),
    }
