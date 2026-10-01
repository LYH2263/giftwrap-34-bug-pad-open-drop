from app.services.pad_open_view import open_drop_pad

def test_detail_strips_pad_uplift():
    raw = {"pad_enabled": True, "pad_pct": 10, "base_surface": 0.27, "overlap": 1.15, "paper_m2": 0.341}
    out = open_drop_pad(raw, view="detail")
    assert out["pad_enabled"] is True
    assert out["paper_m2"] == round(0.27 * 1.15, 3)
    assert out.get("list_paper_m2") == 0.341
