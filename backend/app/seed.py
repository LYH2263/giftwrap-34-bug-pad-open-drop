from app.db import connect
from app.config import DEFAULT_PAD_PCT

def _columns(conn, table):
    return {r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}

def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS boxes(id INTEGER PRIMARY KEY,name TEXT,length REAL,width REAL,height REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS papers(id INTEGER PRIMARY KEY,name TEXT,roll_width REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,box_id INT,overlap REAL,result_json TEXT,note TEXT,created_at TEXT,
        pad_enabled INT NOT NULL DEFAULT 0,pad_pct REAL,pad_order TEXT);
    """)
    # 旧库迁移：补齐防压垫列，历史记录视为关闭、面积不动
    cols = _columns(c, "calc_runs")
    if "pad_enabled" not in cols:
        c.execute("ALTER TABLE calc_runs ADD COLUMN pad_enabled INT NOT NULL DEFAULT 0")
    if "pad_pct" not in cols:
        c.execute("ALTER TABLE calc_runs ADD COLUMN pad_pct REAL")
    if "pad_order" not in cols:
        c.execute("ALTER TABLE calc_runs ADD COLUMN pad_order TEXT")

    if c.execute("SELECT COUNT(*) c FROM boxes").fetchone()["c"] == 0:
        c.executemany("INSERT INTO boxes(name,length,width,height,data_quality,note) VALUES (?,?,?,?,?,?)",[
            ("书型盒",0.30,0.20,0.15,"clean",""),
            ("方形礼盒",0.25,0.25,0.10,"clean",""),
            ("脏数据-负高",0.2,0.2,-0.1,"dirty","高度负"),
        ])
        c.executemany("INSERT INTO papers(name,roll_width,data_quality,note) VALUES (?,?,?,?)",[
            ("哑光纸1.0m",1.0,"clean",""),
            ("牛皮纸0.7m",0.7,"clean",""),
        ])
        c.execute("INSERT INTO settings(key,value) VALUES ('overlap','1.15')")
        c.execute("INSERT INTO settings(key,value) VALUES ('pad_pct_default',?)", (str(DEFAULT_PAD_PCT),))
        c.commit()
    else:
        # 既有库也补上默认垫层百分比设置（不影响已落库记录）
        row = c.execute("SELECT 1 FROM settings WHERE key='pad_pct_default'").fetchone()
        if not row:
            c.execute("INSERT INTO settings(key,value) VALUES ('pad_pct_default',?)", (str(DEFAULT_PAD_PCT),))
            c.commit()
    c.close()
