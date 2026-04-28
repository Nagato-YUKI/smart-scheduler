import os


class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
    DATABASE = os.environ.get("DATABASE_URL") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "paike.db"
    )
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
    SECRET_KEY = os.environ.get("SECRET_KEY", "paike-secret-key-dev")
    ITEMS_PER_PAGE = 20


# 模块级变量（向后兼容）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
DATABASE = os.environ.get("DATABASE_URL") or os.path.join(BASE_DIR, "paike.db")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
SECRET_KEY = os.environ.get("SECRET_KEY", "paike-secret-key-dev")
ITEMS_PER_PAGE = 20
