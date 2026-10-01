"""回看投影钉住契约（旧 bug: pad-open-drop）。

修复前：列表行是写入时的抬升面积，详情却在 pad_enabled 或 pad_pct>0 时
剥回「六面 × 折边」的未加垫面积，且按当前默认百分比 live 重抬——双入口
不一致、旧编号被新默认重抬。修复后列表 / 详情 / 开放投影三处同源钉住。
"""
import pytest

from app import seed
from app.repositories import history, settings_repo
from app.services import estimate_service
from app.services.pad_open_view import open_drop_pad, pad_projection, pinned_view
from app.engines.wrap_math import PAD_ORDER


@pytest.fixture(autouse=True)
def _fresh_db():
    seed.init_db()
    yield


def test_pinned_view_keeps_uplifted_paper_m2():
    raw = {"pad_enabled": True, "pad_pct": 10, "pad_order": PAD_ORDER,
           "box_surface": 0.27, "overlap": 1.15, "paper_m2": 0.342}
    out = pinned_view(raw, view="detail")
    # 详情不得剥回 base*overlap=0.310
    assert out["paper_m2"] == 0.342
    assert out["list_paper_m2"] == 0.342
    assert out["open_pad_dropped"] is False


def test_open_drop_pad_compat_shim_does_not_strip_or_restamp():
    raw = {"pad_enabled": True, "pad_pct": 12, "pad_order": PAD_ORDER,
           "base_surface": 0.27, "overlap": 1.15, "paper_m2": 0.348}
    # 即便传入 live_pct=50（旧的重抬入口），也必须被忽略
    out = open_drop_pad(raw, live_pct=50, view="detail")
    assert out["paper_m2"] == 0.348
    assert out["pad_pct"] == 12
    assert out["list_paper_m2"] == 0.348


def test_pad_projection_pins_order_and_area():
    raw = {"pad_enabled": True, "pad_pct": 12, "pad_order": PAD_ORDER, "paper_m2": 0.348}
    p = pad_projection(raw)
    assert p == {
        "pad_enabled": True,
        "pad_pct": 12,
        "pad_order": PAD_ORDER,
        "paper_m2": 0.348,
        "list_paper_m2": 0.348,
        "open_pad_dropped": False,
    }


def test_list_and_detail_share_pinned_uplifted_area():
    """端到端：开垫写入 → 改默认 → 列表与详情仍是同一写入抬升面积。"""
    r = estimate_service.run_estimate(1, None, "cross", True, "", pad_enabled=True, pad_pct=12)
    rid, pinned_m2 = r["run_id"], r["paper_m2"]

    settings_repo.set_pad_pct_default(50)  # 改默认后再开旧编号不得重抬

    detail = history.get_run(rid)
    top = next(x for x in history.list_runs(500) if x["id"] == rid)

    # 双入口同一抬升面积（核心修复点：不得一个 0.348 一个 0.310）
    assert detail["result"]["paper_m2"] == pinned_m2
    assert top["result"]["paper_m2"] == pinned_m2
    assert detail["result"]["list_paper_m2"] == pinned_m2
    assert top["result"]["list_paper_m2"] == pinned_m2
    # 开关 / 百分比 / 顺序三处同源
    for d in (detail, top):
        assert d["pad_enabled"] is True
        assert d["pad_pct"] == 12.0
        assert d["pad_order"] == PAD_ORDER
        assert d["result"]["pad_pct"] == 12.0
        assert d["result"]["pad_order"] == PAD_ORDER
    # 开放投影也同源，不剥垫
    proj = pad_projection(detail["result"])
    assert proj["paper_m2"] == pinned_m2
    assert proj["pad_pct"] == 12.0
    assert proj["open_pad_dropped"] is False


def test_disabled_run_detail_and_list_equal_unpadded():
    r = estimate_service.run_estimate(1, 1.15, "cross", True, "", pad_enabled=False)
    rid = r["run_id"]
    detail = history.get_run(rid)
    top = next(x for x in history.list_runs(500) if x["id"] == rid)
    # 关垫：两入口都是改造前的六面×折边，且不出现任何剥垫标记
    assert detail["result"]["paper_m2"] == 0.31
    assert top["result"]["paper_m2"] == 0.31
    assert detail["result"]["open_pad_dropped"] is False
    assert detail["pad_order"] is None
