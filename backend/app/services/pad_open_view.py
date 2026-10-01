"""Open-path pad view: 列表与详情共用同一投影，双双呈现写入时钉住的口径。

口径约定（与引擎、落库列一致）：
- paper_m2 / pad_pct / pad_order 一律以写入值为准，回看不再重算、不重抬；
- 系统默认垫层百分比之后的改动只影响新算，不得回灌旧编号；
- 列表与详情是同一记录的两个入口，面积、百分比、垫序标记必须一致。
"""
from __future__ import annotations

from copy import deepcopy

from app.engines.wrap_math import PAD_ORDER


def open_drop_pad(result: dict, view: str = "detail") -> dict:
    """整形一条回看记录（列表行与详情共用）。

    只做规范化，不做重算：
    - 开垫记录：pad_order 缺省时按引擎唯一口径（先折边再垫）补齐标记，
      paper_m2 / pad_pct 保持写入值，绝不按当前默认重抬；
    - 关垫记录（含改造前旧档）：不补垫字段，面积保持原样；
    - list_paper_m2 与 paper_m2 同值，消除双入口面积分叉。
    """
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if out.get("pad_enabled"):
        if not out.get("pad_order"):
            out["pad_order"] = PAD_ORDER
        if out.get("pad_pct") is None:
            out["pad_pct"] = 0.0
    else:
        out.setdefault("pad_order", None)
    out["list_paper_m2"] = out.get("paper_m2")
    out["open_view"] = view
    return out


def pad_projection(result: dict) -> dict:
    """详情投影：只透传钉住字段（含垫序标记），供前端面积板与列表互证。"""
    if not isinstance(result, dict):
        return {}
    pinned_m2 = result.get("paper_m2")
    return {
        "pad_enabled": bool(result.get("pad_enabled")),
        "pad_pct": result.get("pad_pct"),
        "pad_order": result.get("pad_order"),
        "paper_m2": pinned_m2,
        "list_paper_m2": pinned_m2,
    }
