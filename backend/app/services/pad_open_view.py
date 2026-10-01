"""回看投影：列表与详情共用同一条钉住路径（唯一口径）。

写入用纸档时，pad_enabled / pad_pct / pad_order / paper_m2 四件套已按当时
口径钉死落库（先折边再垫：paper_m2 = base * overlap * (1 + pad_pct/100)）。
任何回看入口——列表行、详情板、开放投影——都必须原样返回这四个写入值：

* 不剥垫层：详情不得退回「六面 × 折边」的未加垫面积；
* 不按当前系统默认百分比重抬旧编号（改默认只影响其后的新单）；
* 不重算面积；开启时 paper_m2 即写入时的抬升面积，两个入口必须相等。

展示用镜像字段（list_paper_m2 等）只允许复制 paper_m2，绝不允许分叉。
"""
from __future__ import annotations
from copy import deepcopy

VIEWS = ("list", "detail")


def pinned_view(result: dict, view: str = "detail") -> dict:
    """返回写入时钉住的结果。

    只做 deepcopy 与展示镜像补字段，不改任何定量值；live_pct 之类的
    「按当前默认重盖」入口已删除——旧编号永不重抬。
    """
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    # 镜像必须等于钉住的 paper_m2（开启时即含垫层抬升），禁止与详情分叉
    out["list_paper_m2"] = out.get("paper_m2")
    if view in VIEWS:
        out["open_view"] = view
    # 回看投影从不剥垫：显式置 False，供消费方断言
    out["open_pad_dropped"] = False
    return out


def open_drop_pad(result: dict, live_pct=None, view: str = "detail") -> dict:
    """兼容旧名的薄封装：语义已改为钉住投影，绝不再剥垫/重抬。

    live_pct 参数保留签名但被刻意忽略——它是旧编号被新默认重抬的入口，
    不得复活。
    """
    return pinned_view(result, view=view)


def pad_projection(result: dict) -> dict:
    """开放投影：与列表/详情同源，四件套 + 面积镜像全部钉住。"""
    if not isinstance(result, dict):
        return {}
    paper_m2 = result.get("paper_m2")
    return {
        "pad_enabled": result.get("pad_enabled"),
        "pad_pct": result.get("pad_pct"),
        "pad_order": result.get("pad_order"),
        "paper_m2": paper_m2,
        "list_paper_m2": result.get("list_paper_m2", paper_m2),
        "open_pad_dropped": False,
    }
