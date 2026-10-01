from app.config import DEFAULT_OVERLAP, DEFAULT_PAD_PCT
from app.db import connect

def get_all():
    c = connect()
    try:
        d = {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM settings").fetchall()}
        d.setdefault("overlap", str(DEFAULT_OVERLAP))
        d.setdefault("pad_pct_default", str(DEFAULT_PAD_PCT))
        return d
    finally:
        c.close()

def get_overlap():
    return float(get_all().get("overlap", DEFAULT_OVERLAP))

def get_pad_pct_default():
    return float(get_all().get("pad_pct_default", DEFAULT_PAD_PCT))

def set_pad_pct_default(pct: float):
    c = connect()
    try:
        c.execute(
            "INSERT INTO settings(key,value) VALUES ('pad_pct_default',?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(float(pct)),),
        )
        c.commit()
    finally:
        c.close()
