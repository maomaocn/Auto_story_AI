from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时：初始化数据库
    print("Starting up...")
    await init_db()
    yield
    # 关闭时：清理资源
    print("Shutting down...")
    await close_db()

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 配置CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 根路由
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "api": settings.API_V1_STR,
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "isoformat"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发时启用热重载
        log_level="info"
    )