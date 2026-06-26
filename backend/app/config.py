from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "Agri Management Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置 - 默认使用 SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./agri_mgmt.db"

    # JWT 认证配置
    SECRET_KEY: str = "agri-mgmt-platform-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]

    # Redis 配置（可选，用于 token 黑名单等）
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
