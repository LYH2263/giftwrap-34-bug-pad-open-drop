"""回看整形回归：列表与详情同口径，均呈现写入时钉住的垫层字段。

对应 bug：详情曾把已抬垫面积打回未加垫的六面×折边，并按当前默认
重钉百分比；此处钉死修复后的行为。
"""
from app.services.pad_open_view import open_drop_pad, pad_projection
from app.engines.wrap_math import PAD_ORDER


def test_detail_keeps_pinned_pad_uplift():
    raw = {"pad_enabled": True, "pad_pct": 10, "pad_order": PAD_ORDER,
           "box_surface": 0.27, "overlap": 1.15, "paper_m2": 0.341}
    out = open_drop_pad(raw, view="detail")
    assert out["pad_enabled"] is True
    # 面积保持写入值，不得回到 0.27 * 1.15 = 0.31
    assert out["paper_m2"] == 0.341
    assert out["pad_pct"] == 10
    assert out["pad_order"] == PAD_ORDER
    assert out["list_paper_m2"] == 0.341


def test_list_and_detail_agree():
    raw = {"pad_enabled": True, "pad_pct": 12, "pad_order": PAD_ORDER,
           "box_surface": 0.27, "overlap": 1.15, "paper_m2": 0.348}
    detail = open_drop_pad(raw, view="detail")
    listing = open_drop_pad(raw, view="list")
    for key in ("paper_m2", "pad_pct", "pad_order", "list_paper_m2"):
        assert detail[key] == listing[key]


def test_no_live_default_restamp():
    """整形函数不接受任何 live 默认：同一写入记录重复整形结果稳定。"""
    raw = {"pad_enabled": True, "pad_pct": 12, "pad_order": PAD_ORDER,
           "box_surface": 0.27, "overlap": 1.15, "paper_m2": 0.348}
    once = open_drop_pad(raw, view="detail")
    twice = open_drop_pad(once, view="detail")
    assert once == twice
    assert twice["pad_pct"] == 12
    assert twice["paper_m2"] == 0.348


def test_pad_order_marker_filled_when_missing():
    """开垫旧档缺垫序标记时按引擎唯一口径补齐，面积仍不动。"""
    raw = {"pad_enabled": True, "pad_pct": 8, "paper_m2": 0.335}
    out = open_drop_pad(raw, view="detail")
    assert out["pad_order"] == PAD_ORDER
    assert out["paper_m2"] == 0.335


def test_pad_off_record_untouched():
    raw = {"pad_enabled": False, "box_surface": 0.27, "overlap": 1.15, "paper_m2": 0.31}
    out = open_drop_pad(raw, view="detail")
    assert out["paper_m2"] == 0.31
    assert out["pad_order"] is None
    assert out["list_paper_m2"] == 0.31


def test_projection_carries_pinned_fields():
    raw = {"pad_enabled": True, "pad_pct": 10, "pad_order": PAD_ORDER, "paper_m2": 0.341}
    proj = pad_projection(raw)
    assert proj == {
        "pad_enabled": True,
        "pad_pct": 10,
        "pad_order": PAD_ORDER,
        "paper_m2": 0.341,
        "list_paper_m2": 0.341,
    }
