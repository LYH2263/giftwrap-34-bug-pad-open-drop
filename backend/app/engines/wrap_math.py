"""用纸面积引擎。

口径（唯一可测口径，勿在调用方各算各的）：
1. base = 盒体外表面近似面积 = 2(LW + LH + WH)
2. 折边系数 overlap：含重叠余量的放大
3. 防压垫百分比 pad_pct（单位 %）：开启防压垫时的垫层抬升

垫层抬升与折边系数必须按固定顺序叠乘。本引擎锁定 **先折边再垫**
（PAD_ORDER = "overlap_first"）：

    paper_m2 = base * overlap * (1 + pad_pct/100)

含义：先按折边系数算出含重叠余量的用纸，再在其上整体抬一层防压垫。

备选口径「先垫再折边」（pad_first，不采用，仅留档以便对拍）：
垫层把盒体每边都抬高 pad_pct，相当于 L/W/H 整体乘 (1+p) 后再折边：

    paper_m2 = base * (1 + pad_pct/100)^2 * overlap

两种顺序在 pad_pct>0 时结果不同，因此每条落库记录必须带 pad_order
标记，回看时只能照该标记复算，不得按新默认顺序重抬。
"""

# 叠乘顺序标记：先折边再垫（本引擎唯一生效口径）
PAD_ORDER_OVERLAP_FIRST = "overlap_first"
# 备选标记：先垫再折边（仅用于历史口径对照，当前引擎不产出）
PAD_ORDER_PAD_FIRST = "pad_first"
PAD_ORDER = PAD_ORDER_OVERLAP_FIRST


def paper_area(length, width, height, overlap=1.15, pad_enabled=False, pad_pct=0.0):
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    ov = float(overlap)
    if ov <= 0:
        raise ValueError("overlap must be positive")

    base = 2 * (L * W + L * H + W * H)
    folded = base * ov  # 先折边

    enabled = bool(pad_enabled)
    pct = float(pad_pct) if enabled else 0.0
    if pct < 0:
        # 兜底：正常由服务层在落库前拦截，引擎不接受负数
        raise ValueError("pad_pct must not be negative")

    if enabled:
        # 先折边再垫：在含折边余量的用纸面积上整体抬升垫层
        need = folded * (1.0 + pct / 100.0)
    else:
        # 关闭防压垫：paper_m2 与改造前完全一致
        need = folded

    return {
        "box_surface": round(base, 3),
        "overlap": ov,
        "pad_enabled": enabled,
        "pad_pct": round(pct, 3),
        "pad_order": PAD_ORDER if enabled else None,
        "paper_m2": round(need, 3),
    }


def ribbon_estimate(length, width, height, wrap_style="cross"):
    """丝带只跟基础三边 L/W/H，不吃折边系数也不吃防压垫抬升。"""
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
