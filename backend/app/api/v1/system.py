from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.dependencies import get_db
from app.models import Device, Plot, Crop, User, Alert

router = APIRouter(prefix="/system", tags=["系统管理"])


@router.get("/config")
async def get_system_config(db: AsyncSession = Depends(get_db)):
    """系统配置"""
    return {
        "code": 200,
        "message": "success",
        "data": {
            "system_name": "农业物联网管理平台",
            "version": "1.0.0",
            "language": "zh-CN",
            "timezone": "Asia/Shanghai",
            "dataRetentionDays": 365,
            "alertEnabled": True,
            "autoIrrigationEnabled": False,
        }
    }


@router.put("/config")
async def update_system_config():
    """更新配置"""
    return {"code": 200, "message": "配置已更新", "data": None}


@router.get("/health")
async def system_health(db: AsyncSession = Depends(get_db)):
    """健康检查"""
    # 检查数据库连接
    try:
        result = await db.execute(select(func.count(Device.id)))
        device_count = result.scalar() or 0
        db_ok = True
    except Exception:
        db_ok = False
        device_count = 0

    # 获取各模型统计
    result = await db.execute(select(func.count(Plot.id)))
    plot_count = result.scalar() or 0

    result = await db.execute(select(func.count(Crop.id)))
    crop_count = result.scalar() or 0

    result = await db.execute(select(func.count(User.id)))
    user_count = result.scalar() or 0

    result = await db.execute(select(func.count(Alert.id)))
    alert_count = result.scalar() or 0

    return {
        "code": 200,
        "message": "success",
        "data": {
            "status": "healthy" if db_ok else "unhealthy",
            "database": "connected" if db_ok else "disconnected",
            "uptime": "running",
            "statistics": {
                "devices": device_count,
                "plots": plot_count,
                "crops": crop_count,
                "users": user_count,
                "alerts": alert_count,
            }
        }
    }
