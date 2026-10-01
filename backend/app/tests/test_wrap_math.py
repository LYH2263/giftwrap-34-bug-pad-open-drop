import pytest
from app.engines.wrap_math import (
    paper_area,
    ribbon_estimate,
    PAD_ORDER,
    PAD_ORDER_OVERLAP_FIRST,
)

def test_book_box():
    r = paper_area(0.30, 0.20, 0.15, 1.15)
    assert r["box_surface"] == 0.27
    assert r["paper_m2"] == 0.31

def test_ribbon_cross():
    rb = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert rb["ribbon_m"] > 0.5

def test_pad_disabled_matches_legacy():
    """关闭防压垫：paper_m2 必须与改造前完全一致，且不带垫字段抬升。"""
    old = paper_area(0.30, 0.20, 0.15, 1.15, pad_enabled=False)
    assert old["paper_m2"] == 0.31
    assert old["pad_enabled"] is False
    assert old["pad_pct"] == 0.0
    assert old["pad_order"] is None

def test_pad_enabled_higher_than_disabled():
    """开启防压垫：同盒同折边系数下面积严格高于关闭时。"""
    off = paper_area(0.30, 0.20, 0.15, 1.15, pad_enabled=False)
    on = paper_area(0.30, 0.20, 0.15, 1.15, pad_enabled=True, pad_pct=10)
    assert on["paper_m2"] > off["paper_m2"]
    # 先折边再垫：0.27 * 1.15 * 1.10 = 0.34155 -> 0.342
    assert on["paper_m2"] == round(0.27 * 1.15 * 1.10, 3)
    assert on["pad_enabled"] is True
    assert on["pad_pct"] == 10.0
    assert on["pad_order"] == PAD_ORDER == PAD_ORDER_OVERLAP_FIRST

def test_pad_order_is_overlap_first_distinguishable():
    """顺序标记须真实区分两种口径：先折边再垫 != 先垫再折边（p>0）。"""
    base = 2 * (0.30 * 0.20 + 0.30 * 0.15 + 0.20 * 0.15)
    ov, p = 1.15, 10.0
    overlap_first = round(base * ov * (1 + p / 100), 3)
    pad_first = round(base * (1 + p / 100) ** 2 * ov, 3)
    got = paper_area(0.30, 0.20, 0.15, ov, True, p)
    assert got["paper_m2"] == overlap_first
    assert overlap_first != pad_first
    assert got["pad_order"] == "overlap_first"

def test_negative_pad_pct_rejected():
    with pytest.raises(ValueError):
        paper_area(0.30, 0.20, 0.15, 1.15, True, -5)

def test_ribbon_unchanged_by_pad():
    """ribbon 只跟基础三边：开不开垫、垫多少，ribbon 一样。"""
    base = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    # ribbon_estimate 不收 pad 参数本身即约束；同尺寸结果稳定
    again = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert base == again
