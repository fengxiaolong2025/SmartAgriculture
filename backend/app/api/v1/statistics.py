from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db
from app.models import (
    SensorData, Alert, IrrigationRecord, FertilizationRecord,
    PestControlRecord, VentilationRecord, HarvestRecord, Device
)
from datetime import datetime, timedelta

router = APIRouter(prefix="/statistics", tags=["数据统计"])


@router.get("/daily")
async def get_daily_report(db: AsyncSession = Depends(get_db)):
    """日报"""
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")

    # 灌溉
    result = await db.execute(
        select(func.coalesce(func.sum(IrrigationRecord.water_amount), 0)).where(
            IrrigationRecord.start_time >= today_str
        )
    )
    irrigation = result.scalar() or 0

    # 施肥
    result = await db.execute(
        select(func.coalesce(func.sum(FertilizationRecord.amount), 0)).where(
            FertilizationRecord.apply_time >= today_str
        )
    )
    fertilization = result.scalar() or 0

    # 除害
    result = await db.execute(
        select(func.count(PestControlRecord.id)).where(
            PestControlRecord.apply_time >= today_str
        )
    )
    pest_control = result.scalar() or 0

    # 通风
    result = await db.execute(
        select(func.count(VentilationRecord.id)).where(
            VentilationRecord.start_time >= today_str
        )
    )
    ventilation = result.scalar() or 0

    # 告警
    result = await db.execute(
        select(func.count(Alert.id)).where(
            Alert.created_at >= today_str
        )
    )
    alerts = result.scalar() or 0

    # 设备
    result = await db.execute(select(func.count(Device.id)).where(Device.is_active == True))
    total_devices = result.scalar() or 0
    result = await db.execute(
        select(func.count(Device.id)).where(Device.is_active == True, Device.status == "online")
    )
    online_devices = result.scalar() or 0

    # 平均温湿度
    result = await db.execute(
        select(func.avg(SensorData.value)).where(
            SensorData.metric_name == "temperature",
            SensorData.time >= today_str
        )
    )
    avg_temp = result.scalar()

    result = await db.execute(
        select(func.avg(SensorData.value)).where(
            SensorData.metric_name == "humidity",
            SensorData.time >= today_str
        )
    )
    avg_humidity = result.scalar()

    return {
        "code": 200,
        "message": "success",
        "data": {
            "date": today_str,
            "avgTemperature": round(avg_temp, 1) if avg_temp else None,
            "avgHumidity": round(avg_humidity, 1) if avg_humidity else None,
            "irrigation": irrigation,
            "fertilization": fertilization,
            "pestControl": pest_control,
            "ventilation": ventilation,
            "alerts": alerts,
            "deviceOnline": online_devices,
            "deviceTotal": total_devices,
        }
    }


@router.get("/weekly")
async def get_weekly_report(db: AsyncSession = Depends(get_db)):
    """周报"""
    now = datetime.utcnow()
    week_start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")

    # 本周灌溉
    result = await db.execute(
        select(func.coalesce(func.sum(IrrigationRecord.water_amount), 0)).where(
            IrrigationRecord.start_time >= week_start
        )
    )
    irrigation = result.scalar() or 0

    # 本周施肥
    result = await db.execute(
        select(func.coalesce(func.sum(FertilizationRecord.amount), 0)).where(
            FertilizationRecord.apply_time >= week_start
        )
    )
    fertilization = result.scalar() or 0

    # 本周除害
    result = await db.execute(
        select(func.count(PestControlRecord.id)).where(
            PestControlRecord.apply_time >= week_start
        )
    )
    pest_control = result.scalar() or 0

    # 本周告警
    result = await db.execute(
        select(func.count(Alert.id)).where(Alert.created_at >= week_start)
    )
    alerts = result.scalar() or 0

    # 本周采收
    result = await db.execute(
        select(func.coalesce(func.sum(HarvestRecord.yield_amount), 0)).where(
            HarvestRecord.harvest_time >= week_start
        )
    )
    harvest = result.scalar() or 0

    return {
        "code": 200,
        "message": "success",
        "data": {
            "weekStart": week_start,
            "weekEnd": now.strftime("%Y-%m-%d"),
            "irrigation": irrigation,
            "fertilization": fertilization,
            "pestControl": pest_control,
            "alerts": alerts,
            "harvest": harvest,
        }
    }


@router.get("/monthly")
async def get_monthly_report(db: AsyncSession = Depends(get_db)):
    """月报"""
    now = datetime.utcnow()
    month_start = now.strftime("%Y-%m-01")

    # 本月灌溉
    result = await db.execute(
        select(func.coalesce(func.sum(IrrigationRecord.water_amount), 0)).where(
            IrrigationRecord.start_time >= month_start
        )
    )
    irrigation = result.scalar() or 0

    # 本月施肥
    result = await db.execute(
        select(func.coalesce(func.sum(FertilizationRecord.amount), 0)).where(
            FertilizationRecord.apply_time >= month_start
        )
    )
    fertilization = result.scalar() or 0

    # 本月除害
    result = await db.execute(
        select(func.count(PestControlRecord.id)).where(
            PestControlRecord.apply_time >= month_start
        )
    )
    pest_control = result.scalar() or 0

    # 本月告警
    result = await db.execute(
        select(func.count(Alert.id)).where(Alert.created_at >= month_start)
    )
    alerts = result.scalar() or 0

    # 本月采收
    result = await db.execute(
        select(func.coalesce(func.sum(HarvestRecord.yield_amount), 0)).where(
            HarvestRecord.harvest_time >= month_start
        )
    )
    harvest = result.scalar() or 0

    # 本月通风
    result = await db.execute(
        select(func.count(VentilationRecord.id)).where(
            VentilationRecord.start_time >= month_start
        )
    )
    ventilation = result.scalar() or 0

    return {
        "code": 200,
        "message": "success",
        "data": {
            "month": now.strftime("%Y-%m"),
            "irrigation": irrigation,
            "fertilization": fertilization,
            "pestControl": pest_control,
            "alerts": alerts,
            "harvest": harvest,
            "ventilation": ventilation,
        }
    }
