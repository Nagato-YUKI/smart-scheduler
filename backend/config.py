# 这个文件让Render能自动从DATABASE_URL环境变量读取数据库连接
# 同时支持本地SQLite作为fallback
import os

DB_TYPE = os.environ.get("DB_TYPE", "sqlite")

# 优先使用环境变量中的DATABASE_URL
DATABASE = os.environ.get("DATABASE_URL")

# 如果没有设置DATABASE_URL，使用SQLite
if not DATABASE:
    DB_TYPE = "sqlite"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE = os.path.join(BASE_DIR, "paike.db")

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
SECRET_KEY = os.environ.get("SECRET_KEY", "paike-secret-key-dev")
ITEMS_PER_PAGE = 20
