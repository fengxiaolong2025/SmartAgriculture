from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from app.dependencies import get_db
from app.models import (
    Device, SensorData, Alert, Plot, Crop,
    IrrigationRecord, FertilizationRecord, PestControlRecord,
    VentilationRecord, HarvestRecord
)
from datetime import datetime, timedelta
import random
import math
import hashlib

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


def _flatten_sensors(metric_rows):
    """将后端传感器数据转换为前端期望的扁平格式
    输入: { temperature: {value, unit, time}, humidity: {...}, light: {...}, co2: {...} }
    输出: { airTemp: 35.79, airHumidity: 78.14, lightIntensity: 4053.82, co2: 325.47 }
    """
    result = {}
    for key, meta in metric_rows.items():
        if key == "temperature":
            result["airTemp"] = meta["value"]
        elif key == "humidity":
            result["airHumidity"] = meta["value"]
        elif key == "light":
            result["lightIntensity"] = meta["value"]
        elif key == "co2":
            result["co2"] = meta["value"]
    return result


def _get_maturity_color(days_remaining, total_days):
    """根据剩余天数比例返回颜色"""
    if total_days <= 0:
        return "#00d4ff"
    ratio = days_remaining / total_days
    if ratio <= 0.15:
        return "#ff3d4f"
    elif ratio <= 0.3:
        return "#ffab00"
    elif ratio <= 0.5:
        return "#ff9100"
    else:
        return "#00e676"


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    """大屏概览 - 返回所有面板需要的聚合数据"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    hours_24_ago = now - timedelta(hours=24)

    # --- 实时传感器数据 ---
    metrics = ["temperature", "humidity", "light", "co2", "soil_moisture", "soil_ph", "soil_ec"]
    sensor_data_raw = {}
    for metric in metrics:
        result = await db.execute(
            select(SensorData).where(SensorData.metric_name == metric)
            .order_by(desc(SensorData.time)).limit(1)
        )
        row = result.scalar_one_or_none()
        if row:
            sensor_data_raw[metric] = {"value": row.value, "unit": row.unit, "time": row.time}
    sensors_flat = _flatten_sensors(sensor_data_raw)

    # --- 24小时趋势 ---
    result = await db.execute(
        select(SensorData).where(
            SensorData.metric_name.in_(["temperature", "humidity"]),
            SensorData.time >= hours_24_ago.strftime("%Y-%m-%d %H:%M:%S")
        ).order_by(SensorData.time)
    )
    trend_rows = result.scalars().all()

    timestamps = []
    temperatures = []
    humidities = []
    temp_map = {}
    humid_map = {}

    for row in trend_rows:
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

    # --- 地块状态（扁平化，匹配前端 plots 格式）---
    result = await db.execute(select(Plot).limit(50))
    plots = result.scalars().all()
    plots_status = []
    for plot in plots:
        # 获取该地块最新传感器数据
        result2 = await db.execute(
            select(SensorData).where(
                SensorData.plot_id == plot.id,
                SensorData.metric_name.in_(["temperature", "humidity", "soil_moisture"])
            ).order_by(desc(SensorData.time)).limit(3)
        )
        latest_sensors = result2.scalars().all()
        sensor_values = {}
        for s in latest_sensors:
            if s.metric_name not in sensor_values:
                sensor_values[s.metric_name] = s.value

        # 获取作物名称
        crop_name = None
        if plot.crop_id:
            crop_result = await db.execute(select(Crop).where(Crop.id == plot.crop_id))
            crop_row = crop_result.scalar_one_or_none()
            if crop_row:
                crop_name = crop_row.name

        # 判断状态
        plot_temp = sensor_values.get("temperature", 0)
        plot_humidity = sensor_values.get("humidity", 0)
        plot_status = "warning" if plot_temp > 35 or plot_humidity < 50 else "normal"

        # 模拟设备状态（灌溉、风机等）
        seed = int(hashlib.md5(plot.id.encode()).hexdigest(), 16)
        irrigating = (seed % 3) != 0  # 2/3 概率灌溉开启
        fan_on = plot_temp > 30  # 温度超过30°C开启风机

        plots_status.append({
            "id": plot.code if plot.code else plot.id[:8],
            "name": plot.name,
            "temp": round(plot_temp, 1),
            "humidity": round(plot_humidity, 1),
            "crop": crop_name or "未知",
            "status": plot_status,
            "irrigating": irrigating,
            "fan": fan_on,
        })

    # --- 最新告警（匹配前端 alerts 格式: id, time, level, content, isNew）---
    result = await db.execute(
        select(Alert).order_by(desc(Alert.created_at)).limit(20)
    )
    alerts = result.scalars().all()
    recent_alerts = []
    for i, a in enumerate(alerts):
        time_str = str(a.created_at)[11:19] if a.created_at else ""
        recent_alerts.append({
            "id": a.id,
            "time": time_str,
            "level": a.level if a.level in ("danger", "warning", "info") else "warning",
            "content": a.description or a.title or "",
            "isNew": i == 0,
        })

    # --- 设备在线统计 ---
    result = await db.execute(
        select(func.count(Device.id)).where(Device.is_active == True)
    )
    total_devices = result.scalar() or 0
    result = await db.execute(
        select(func.count(Device.id)).where(Device.is_active == True, Device.status == "online")
    )
    online_devices = result.scalar() or 0

    # --- 今日统计（匹配前端字段名）---
    today_str = today_start.strftime("%Y-%m-%d")
    result = await db.execute(
        select(func.coalesce(func.sum(IrrigationRecord.water_amount), 0)).where(
            IrrigationRecord.start_time >= today_str
        )
    )
    today_irrigation = result.scalar() or 0
    result = await db.execute(
        select(func.coalesce(func.sum(FertilizationRecord.amount), 0)).where(
            FertilizationRecord.apply_time >= today_str
        )
    )
    today_fertilization = result.scalar() or 0
    result = await db.execute(
        select(func.count(PestControlRecord.id)).where(
            PestControlRecord.apply_time >= today_str
        )
    )
    today_pest_control = result.scalar() or 0
    result = await db.execute(
        select(func.count(VentilationRecord.id)).where(
            VentilationRecord.start_time >= today_str
        )
    )
    today_ventilation = result.scalar() or 0

    # --- 成熟度预测（匹配前端: crop, variety, daysLeft, total, color）---
    result = await db.execute(select(Crop).limit(10))
    crops = result.scalars().all()
    maturity = []
    for crop in crops:
        result2 = await db.execute(
            select(Plot).where(Plot.crop_id == crop.id).limit(1)
        )
        plot = result2.scalar_one_or_none()
        days_planted = 0
        if plot and plot.planting_date:
            try:
                planted = datetime.strptime(plot.planting_date, "%Y-%m-%d")
                days_planted = (now - planted).days
            except ValueError:
                days_planted = 0
        growth_cycle = crop.growth_cycle_days or 90
        progress = min(round(days_planted / growth_cycle * 100, 1), 100) if growth_cycle > 0 else 0
        days_remaining = max(growth_cycle - days_planted, 0)
        maturity.append({
            "crop": crop.name or "未知",
            "variety": crop.variety or "",
            "daysLeft": days_remaining,
            "total": growth_cycle,
            "color": _get_maturity_color(days_remaining, growth_cycle),
        })

    # --- 历史产量（匹配前端: month, yield, target）---
    result = await db.execute(
        select(HarvestRecord).order_by(desc(HarvestRecord.harvest_time)).limit(12)
    )
    harvests = result.scalars().all()
    yield_history = []
    months_map = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    for h in reversed(harvests):
        y = round(h.yield_amount or 0, 1)
        yield_history.append({
            "month": months_map[datetime.utcnow().month - 1] if not h.harvest_time else
                     months_map[max(0, min(11, int(str(h.harvest_time)[5:7]) - 1))],
            "yield": y,
            "target": round(y * 1.1, 1),
        })

    # --- 天气信息（扁平化匹配前端: temp, humidity, icon, description）---
    weather_current = {
        "temperature": round(random.uniform(20, 35), 1),
        "humidity": round(random.uniform(40, 80), 1),
        "wind_speed": round(random.uniform(0, 10), 1),
        "condition": random.choice(["晴", "多云", "阴", "小雨"]),
        "icon": random.choice(["sunny", "cloudy", "overcast", "rain"]),
    }
    forecast = []
    for i in range(7):
        forecast.append({
            "date": (now + timedelta(days=i + 1)).strftime("%Y-%m-%d"),
            "temp_high": round(random.uniform(28, 38), 1),
            "temp_low": round(random.uniform(18, 25), 1),
            "humidity": round(random.uniform(40, 85), 1),
            "condition": random.choice(["晴", "多云", "阴", "小雨", "中雨"]),
            "icon": random.choice(["sunny", "cloudy", "overcast", "rain"]),
        })
    weather_flat = {
        "temp": weather_current["temperature"],
        "humidity": weather_current["humidity"],
        "icon": weather_current["condition"],
        "description": weather_current["condition"],
        "forecast": forecast,
    }

    return {
        "code": 200,
        "message": "success",
        "data": {
            "sensors": sensors_flat,
            "trend": {
                "timestamps": timestamps,
                "temperatures": temperatures,
                "humidities": humidities,
            },
            "plotsStatus": plots_status,
            "recentAlerts": recent_alerts,
            "deviceOnline": {
                "online": online_devices,
                "total": total_devices,
            },
            "todayStatistics": {
                "irrigationVolume": today_irrigation,
                "fertilizerKg": today_fertilization,
                "pestControlCount": today_pest_control,
                "ventilationMin": today_ventilation,
            },
            "maturity": maturity,
            "yieldHistory": yield_history,
            "weather": weather_flat,
        },
    }


@router.get("/sensors")
async def get_sensors(db: AsyncSession = Depends(get_db)):
    """实时传感器数据 - 返回前端期望的扁平格式"""
    metrics = ["temperature", "humidity", "light", "co2", "soil_moisture", "soil_ph", "soil_ec"]
    raw_data = {}
    for metric in metrics:
        result = await db.execute(
            select(SensorData).where(SensorData.metric_name == metric)
            .order_by(desc(SensorData.time)).limit(1)
        )
        row = result.scalar_one_or_none()
        if row:
            raw_data[metric] = {"value": row.value, "unit": row.unit, "time": row.time}
    return {"code": 200, "message": "success", "data": _flatten_sensors(raw_data)}


@router.get("/trend")
async def get_trend(db: AsyncSession = Depends(get_db)):
    """24小时趋势"""
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


@router.get("/plots-status")
async def get_plots_status(db: AsyncSession = Depends(get_db)):
    """所有地块状态 - 返回前端期望的扁平格式"""
    result = await db.execute(select(Plot).limit(50))
    plots = result.scalars().all()
    plots_status = []
    for plot in plots:
        result2 = await db.execute(
            select(SensorData).where(
                SensorData.plot_id == plot.id,
                SensorData.metric_name.in_(["temperature", "humidity", "soil_moisture"])
            ).order_by(desc(SensorData.time)).limit(3)
        )
        latest_sensors = result2.scalars().all()
        sensor_values = {}
        for s in latest_sensors:
            if s.metric_name not in sensor_values:
                sensor_values[s.metric_name] = s.value

        crop_name = None
        if plot.crop_id:
            crop_result = await db.execute(select(Crop).where(Crop.id == plot.crop_id))
            crop_row = crop_result.scalar_one_or_none()
            if crop_row:
                crop_name = crop_row.name

        plot_temp = sensor_values.get("temperature", 0)
        plot_humidity = sensor_values.get("humidity", 0)
        plot_status = "warning" if plot_temp > 35 or plot_humidity < 50 else "normal"

        seed = int(hashlib.md5(plot.id.encode()).hexdigest(), 16)
        irrigating = (seed % 3) != 0
        fan_on = plot_temp > 30

        plots_status.append({
            "id": plot.code if plot.code else plot.id[:8],
            "name": plot.name,
            "temp": round(plot_temp, 1),
            "humidity": round(plot_humidity, 1),
            "crop": crop_name or "未知",
            "status": plot_status,
            "irrigating": irrigating,
            "fan": fan_on,
        })
    return {"code": 200, "message": "success", "data": plots_status}


@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """今日统计"""
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")
    result = await db.execute(
        select(func.coalesce(func.sum(IrrigationRecord.water_amount), 0)).where(
            IrrigationRecord.start_time >= today_str
        )
    )
    irrigation = result.scalar() or 0
    result = await db.execute(
        select(func.coalesce(func.sum(FertilizationRecord.amount), 0)).where(
            FertilizationRecord.apply_time >= today_str
        )
    )
    fertilization = result.scalar() or 0
    result = await db.execute(
        select(func.count(PestControlRecord.id)).where(PestControlRecord.apply_time >= today_str)
    )
    pest_control = result.scalar() or 0
    result = await db.execute(
        select(func.count(VentilationRecord.id)).where(VentilationRecord.start_time >= today_str)
    )
    ventilation = result.scalar() or 0

    return {
        "code": 200,
        "message": "success",
        "data": {
            "irrigationVolume": irrigation,
            "fertilizerKg": fertilization,
            "pestControlCount": pest_control,
            "ventilationMin": ventilation,
        }
    }


@router.get("/maturity")
async def get_maturity(db: AsyncSession = Depends(get_db)):
    """成熟度预测 - 返回前端期望的格式"""
    now = datetime.utcnow()
    result = await db.execute(select(Crop).limit(20))
    crops = result.scalars().all()
    maturity = []
    for crop in crops:
        result2 = await db.execute(select(Plot).where(Plot.crop_id == crop.id).limit(1))
        plot = result2.scalar_one_or_none()
        days_planted = 0
        if plot and plot.planting_date:
            try:
                planted = datetime.strptime(plot.planting_date, "%Y-%m-%d")
                days_planted = (now - planted).days
            except ValueError:
                days_planted = 0
        growth_cycle = crop.growth_cycle_days or 90
        progress = min(round(days_planted / growth_cycle * 100, 1), 100) if growth_cycle > 0 else 0
        days_remaining = max(growth_cycle - days_planted, 0)
        maturity.append({
            "crop": crop.name or "未知",
            "variety": crop.variety or "",
            "daysLeft": days_remaining,
            "total": growth_cycle,
            "color": _get_maturity_color(days_remaining, growth_cycle),
        })
    return {"code": 200, "message": "success", "data": maturity}


@router.get("/yield-history")
async def get_yield_history(db: AsyncSession = Depends(get_db)):
    """历史产量 - 返回前端期望的格式"""
    result = await db.execute(
        select(HarvestRecord).order_by(desc(HarvestRecord.harvest_time)).limit(12)
    )
    harvests = result.scalars().all()
    months_map = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    data = []
    for h in reversed(harvests):
        y = round(h.yield_amount or 0, 1)
        month_str = months_map[datetime.utcnow().month - 1]
        if h.harvest_time:
            try:
                m = int(str(h.harvest_time)[5:7])
                month_str = months_map[max(0, min(11, m - 1))]
            except (ValueError, IndexError):
                pass
        data.append({
            "month": month_str,
            "yield": y,
            "target": round(y * 1.1, 1),
        })
    return {"code": 200, "message": "success", "data": data}


@router.get("/weather")
async def get_weather():
    """天气信息（模拟）- 返回前端期望的扁平格式"""
    now = datetime.utcnow()
    temp = round(random.uniform(20, 35), 1)
    humidity = round(random.uniform(40, 80), 1)
    condition = random.choice(["晴", "多云", "阴", "小雨"])
    return {
        "code": 200,
        "message": "success",
        "data": {
            "temp": temp,
            "humidity": humidity,
            "icon": condition,
            "description": condition,
        }
    }


@router.get("/device-online")
async def get_device_online(db: AsyncSession = Depends(get_db)):
    """设备在线率"""
    result = await db.execute(
        select(func.count(Device.id)).where(Device.is_active == True)
    )
    total = result.scalar() or 0
    result = await db.execute(
        select(func.count(Device.id)).where(Device.is_active == True, Device.status == "online")
    )
    online = result.scalar() or 0
    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "online": online,
            "offline": total - online,
            "onlineRate": round(online / total * 100, 1) if total > 0 else 0,
        }
    }
