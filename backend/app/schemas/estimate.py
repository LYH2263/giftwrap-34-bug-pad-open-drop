from pydantic import BaseModel

class EstimateRequest(BaseModel):
    box_id: int
    overlap: float | None = None
    wrap_style: str = "cross"
    save: bool = False
    note: str = ""
    pad_enabled: bool = False
    # 百分比，单位 %；开启时缺省由服务端取系统默认
    pad_pct: float | None = None

class SettingsUpdate(BaseModel):
    pad_pct_default: float
