import os
import tempfile

# 任何 app.config 导入之前钉死测试数据目录，避免碰真实库
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="giftwrap-test-"))
