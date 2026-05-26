from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "红文织梦 API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: str = "http://localhost,http://localhost:80,http://localhost:5173"

    # Database (开发环境用 SQLite，部署时改为 PostgreSQL)
    DATABASE_URL: str = "sqlite+aiosqlite:///./novel.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- AI Provider ---
    # 可选值: "deepseek" | "openai" | "volcengine" | "custom"
    AI_PROVIDER: str = "deepseek"

    # DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # OpenAI compat (通用 OpenAI 格式)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"

    # 火山引擎豆包 (基于 OpenAI 兼容格式)
    VOLCENGINE_API_KEY: Optional[str] = None
    VOLCENGINE_API_BASE: str = "https://ark.cn-beijing.volces.com/api/v3"
    VOLCENGINE_MODEL: str = ""  # 填写你的推理接入点 endpoint ID, 如 "ep-2025xxxx-xxxxx"

    # User limits
    FREE_PROJECT_LIMIT: int = 1
    FREE_WORD_LIMIT: int = 20000
    FREE_DAILY_CHAPTER_LIMIT: int = 2
    VIP_DAILY_CHAPTER_LIMIT: int = 50
    PREMIUM_DAILY_CHAPTER_LIMIT: int = 200

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()