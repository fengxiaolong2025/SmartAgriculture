"""
农业管理平台 - FastAPI 应用入口。
同时 serve 前端静态文件，前后端同源部署。
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import engine, async_session_factory
from app.models.base import Base
from app.models import *  # noqa: 确保所有模型被导入
from app.api.v1.router import api_router
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.mock.seed_data import run_seed
from app.mock.data_generator import data_generator
from fastapi.exceptions import RequestValidationError

# 前端静态文件目录
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "agri-dashboard", "dist")
FRONTEND_DIST = os.path.abspath(FRONTEND_DIST)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。"""
    # 启动事件：创建表 + 种子数据 + 启动数据生成器
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 运行种子数据
    async with async_session_factory() as db:
        await run_seed(db)

    # 启动后台数据生成器
    await data_generator.start()

    yield

    # 关闭事件：停止数据生成器
    await data_generator.stop()
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS 配置（同源部署后主要防止 API 被其他站点调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 异常处理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 注册 API 路由
app.include_router(api_router)


# ---- 前端静态文件 serve ----
@app.get("/health")
async def health_check():
    """健康检查接口。"""
    return {"code": 200, "message": "success", "data": {"status": "healthy"}}


if os.path.exists(FRONTEND_DIST):
    # Mount 静态资源目录
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/favicon.svg")
    async def favicon():
        path = os.path.join(FRONTEND_DIST, "favicon.svg")
        if os.path.exists(path):
            return FileResponse(path)
        return {"detail": "Not Found"}

    @app.get("/icons.svg")
    async def icons():
        path = os.path.join(FRONTEND_DIST, "icons.svg")
        if os.path.exists(path):
            return FileResponse(path)
        return {"detail": "Not Found"}

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve 前端 SPA，API 路由已优先匹配。"""
        # 如果请求路径以 api/ 开头但没被上面路由匹配，返回 404
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # SPA fallback: 返回 index.html
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Frontend not built. Run: cd agri-dashboard && npm run build"}


# 如果前端不存在，使用简单的根路径响应
if not os.path.exists(FRONTEND_DIST):
    @app.get("/")
    async def root():
        return {
            "code": 200,
            "message": "success",
            "data": {
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "status": "running",
                "hint": "Frontend not deployed. Access /docs for API documentation."
            },
        }
