from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.dependencies import get_db
from app.models import SensorData
from datetime import datetime, timedelta

router = APIRouter(prefix="/sensor-data", tags=["传感器数据"])


@router.get("/realtime")
async def get_realtime(db: AsyncSession = Depends(get_db)):
    """所有传感器最新值（按 metric_name 分组取最新）"""
    metrics = ["temperature", "humidity", "light", "co2", "soil_moisture", "soil_ph", "soil_ec", "wind_speed", "rainfall"]
    result_data = {}
    for metric in metrics:
        result = await db.execute(
            select(SensorData).where(SensorData.metric_name == metric)
            .order_by(desc(SensorData.time)).limit(1)
        )
        row = result.scalar_one_or_none()
        if row:
            result_data[metric] = {
                "device_id": row.device_id,
                "value": row.value,
                "unit": row.unit,
                "time": row.time,
                "plot_id": row.plot_id,
            }
    return {"code": 200, "message": "success", "data": result_data}


@router.get("/history")
async def get_history(
    device_id: str = Query(None),
    metric: str = Query(None, alias="metric"),
    start: str = Query(None),
    end: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """历史数据查询"""
    conditions = []
    if device_id:
        conditions.append(SensorData.device_id == device_id)
    if metric:
        conditions.append(SensorData.metric_name == metric)
    if start:
        conditions.append(SensorData.time >= start)
    if end:
        conditions.append(SensorData.time <= end)

    query = select(SensorData)
    if conditions:
        query = query.where(*conditions)

    result = await db.execute(
        query.order_by(desc(SensorData.time)).limit(limit)
    )
    rows = result.scalars().all()

    data = []
    for r in rows:
        data.append({
            "id": r.id,
            "device_id": r.device_id,
            "metric_name": r.metric_name,
            "value": r.value,
            "unit": r.unit,
            "time": r.time,
            "plot_id": r.plot_id,
        })
    return {"code": 200, "message": "success", "data": data}


@router.get("/trend")
async def get_trend(db: AsyncSession = Depends(get_db)):
    """24小时趋势（最近24个时间点的温度和湿度）"""
    now = datetime.utcnow()
    hours_24_ago = now - timedelta(hours=24)

    result = await db.execute(
        select(SensorData).where(
            SensorData.metric_name.in_(["temperature", "humidity"]),
            SensorData.time >= hours_24_ago.strftime("%Y-%m-%d %H:%M:%S")
        ).order_by(SensorData.time)
    )
    rows = result.scalars().all()

    timestamps = []
    temperatures = []
    humidities = []
    temp_map = {}
    humid_map = {}

    for row in rows:
        ts = row.time[:16]
        if row.metric_name == "temperature":
            if ts not in temp_map:
                temp_map[ts] = row.value
        elif row.metric_name == "humidity":
            if ts not in humid_map:
                humid_map[ts] = row.value

    sorted_ts = sorted(set(list(temp_map.keys()) + list(humid_map.keys())))
    if len(sorted_ts) > 24:
        step = len(sorted_ts) // 24
        sorted_ts = sorted_ts[::step] if step > 0 else sorted_ts

    for ts in sorted_ts:
        timestamps.append(ts)
        temperatures.append(temp_map.get(ts, None))
        humidities.append(humid_map.get(ts, None))

    return {
        "code": 200,
        "message": "success",
        "data": {
            "timestamps": timestamps,
            "temperatures": temperatures,
            "humidities": humidities,
        }
    }
