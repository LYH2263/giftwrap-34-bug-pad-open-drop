import pytest
from fastapi import HTTPException

from app import seed
from app.repositories import history, settings_repo
from app.services import estimate_service
from app.engines.wrap_math import PAD_ORDER


@pytest.fixture(autouse=True)
def _fresh_db():
    seed.init_db()
    yield


def test_run_off_then_on_same_box():
    off = estimate_service.run_estimate(1, None, "cross", False, "", pad_enabled=False)
    on = estimate_service.run_estimate(1, None, "cross", False, "", pad_enabled=True, pad_pct=10)
    assert off["paper_m2"] == 0.31
    assert on["paper_m2"] > off["paper_m2"]
    assert on["pad_enabled"] is True
    assert on["pad_pct"] == 10.0
    assert on["pad_order"] == PAD_ORDER
    # ribbon 只跟基础三边：两次结果一致
    assert off["ribbon"] == on["ribbon"]


def test_saved_run_records_pad_fields_and_paper_m2():
    r = estimate_service.run_estimate(1, 1.15, "cross", True, "首单", pad_enabled=True, pad_pct=12)
    rid = r["run_id"]
    assert rid is not None
    saved = history.get_run(rid)
    assert saved["pad_enabled"] is True
    assert saved["pad_pct"] == 12.0
    assert saved["pad_order"] == PAD_ORDER
    # 列、result_json、接口返回三处的最终面积必须一致
    assert saved["result"]["paper_m2"] == r["paper_m2"]
    assert saved["overlap"] == 1.15
    # 先折边再垫：0.27 * 1.15 * 1.12 = 0.34776 -> 0.348
    assert r["paper_m2"] == 0.348
    # 列表也带垫字段
    listing = history.list_runs()
    top = next(x for x in listing if x["id"] == rid)
    assert top["pad_enabled"] is True
    assert top["pad_pct"] == 12.0
    assert top["result"]["paper_m2"] == r["paper_m2"]


def test_negative_pct_fails_and_is_not_persisted():
    before = len(history.list_runs(500))
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, None, "cross", True, "负数单", pad_enabled=True, pad_pct=-3)
    assert ei.value.status_code == 422
    after = len(history.list_runs(500))
    assert after == before, "负数百分比失败时不得落库"


def test_records_pinned_after_default_changes_and_recompute_matches():
    # 以 12% 写入
    saved = estimate_service.run_estimate(1, None, "cross", True, "", pad_enabled=True, pad_pct=12)
    rid = saved["run_id"]
    pinned_m2 = saved["paper_m2"]

    # 写入后改系统默认垫层百分比
    settings_repo.set_pad_pct_default(50)
    assert settings_repo.get_pad_pct_default() == 50.0

    # 用纸档详情与列表仍钉住写入时的百分比与面积
    detail = history.get_run(rid)
    assert detail["pad_pct"] == 12.0
    assert detail["pad_order"] == PAD_ORDER
    assert detail["result"]["pad_pct"] == 12.0
    assert detail["result"]["paper_m2"] == pinned_m2
    top = next(x for x in history.list_runs(500) if x["id"] == rid)
    assert top["result"]["pad_pct"] == 12.0
    assert top["result"]["paper_m2"] == pinned_m2

    # 不传 pad_pct 的新算应跟随新默认（证明默认确实变了）
    fresh_default = estimate_service.run_estimate(1, None, "cross", False, "", pad_enabled=True)
    assert fresh_default["pad_pct"] == 50.0
    assert fresh_default["paper_m2"] != pinned_m2

    # 算纸台同参再干算，须与回看互证
    redo = estimate_service.run_estimate(1, detail["overlap"], "cross", False, "",
                                         pad_enabled=True, pad_pct=12)
    assert redo["paper_m2"] == pinned_m2
    assert redo["pad_order"] == detail["pad_order"]


def test_disabled_run_stored_without_pad_lift():
    r = estimate_service.run_estimate(1, 1.15, "cross", True, "", pad_enabled=False)
    saved = history.get_run(r["run_id"])
    assert saved["pad_enabled"] is False
    assert saved["pad_pct"] is None
    assert saved["pad_order"] is None
    assert saved["result"]["paper_m2"] == 0.31
