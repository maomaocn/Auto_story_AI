# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     PROJECT_NAME: str = "NarratoAI Backend"
#     API_V1_STR: str = "/api/v1"

#     # --- 数据库配置 ---
#     DB_HOST: str = "localhost"
#     DB_USER: str = "root"
#     DB_PASSWORD: str = "root"
#     DB_NAME: str = "narrato_db"
#     DB_PORT: int = 3306
    
#     # SQLAlchemy 异步连接 URL
#     # 使用 asyncmy 驱动: mysql+asyncmy://USER:PASSWORD@HOST:PORT/NAME
#     DATABASE_URL: str = (
#         f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#     )

#     class Config:
#         env_file = ".env" # 允许从 .env 文件加载配置

# settings = Settings()
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "NarratoAI Backend"
    API_V1_STR: str = "/api/v1"
    
    # --- 数据库配置 ---
    DB_HOST: str = "localhost"
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_NAME: str = "narrato_db"
    DB_PORT: int = 3306
    
    # SQLAlchemy 异步连接 URL
    # 使用 asyncmy 驱动: mysql+asyncmy://USER:PASSWORD@HOST:PORT/NAME
    DATABASE_URL: str = (
        f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React前端
        "http://localhost:8000",  # 后端自身
    ]
    
    # AI服务配置（可选）
    OPENAI_API_KEY: Optional[str] = None
    STABILITY_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # 文件存储配置
    MEDIA_ROOT: str = "media"
    MAX_VIDEO_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_VIDEO_TYPES: List[str] = ["mp4", "avi", "mov", "mkv"]
    
    # 应用配置
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env" # 允许从 .env 文件加载配置
        case_sensitive = True

settings = Settings()