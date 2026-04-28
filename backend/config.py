import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 数据库配置（支持SQLite和PostgreSQL）
    DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
    if DB_TYPE == "postgresql":
        DATABASE = os.environ.get("DATABASE_URL", "")
    else:
        DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "paike.db"))
    
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
    SECRET_KEY = os.environ.get("SECRET_KEY", "paike-secret-key-dev")
    ITEMS_PER_PAGE = 20

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DATABASE = ":memory:"

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
