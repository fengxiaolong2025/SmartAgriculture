"""
模拟数据生成器 - 后台定时生成传感器数据和自动控制记录。
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.device import Device
from app.models.sensor_data import SensorData
from app.models.alert import Alert
from app.models.alert_rule import AlertRule
from app.models.irrigation_record import IrrigationRecord
from app.models.ventilation_record import VentilationRecord
from app.models.plot import Plot


class SensorDataGenerator:
    """传感器数据模拟生成器。"""

    # 各指标模拟参数: (base, amplitude, unit)
    METRIC_CONFIGS = {
        "temperature": {"base": 25, "amplitude": 5, "unit": "°C"},
        "humidity": {"base": 65, "amplitude": 15, "unit": "%"},
        "soil_moisture": {"base": 55, "amplitude": 20, "unit": "%"},
        "light": {"base": 3000, "amplitude": 2000, "unit": "lux"},
        "co2": {"base": 450, "amplitude": 200, "unit": "ppm"},
        "soil_ph": {"base": 6.5, "amplitude": 1.0, "unit": "pH"},
    }

    # 传感器类型对应的指标
    SENSOR_TYPE_METRICS = {
        "TH": ["temperature", "humidity"],
        "SOIL": ["soil_moisture", "soil_ph"],
        "LC": ["light", "co2"],
    }

    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """启动后台数据生成任务。"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        """停止后台数据生成任务。"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run_loop(self):
        """主循环 - 每 10 秒生成一次数据。"""
        while self._running:
            try:
                await self._generate_cycle()
            except Exception as e:
                print(f"[DataGenerator] Error: {e}")
            await asyncio.sleep(10)

    async def _generate_cycle(self):
        """生成一轮传感器数据并检查告警。"""
        async with async_session_factory() as db:
            try:
                # 获取所有活跃传感器设备
                result = await db.execute(
                    select(Device).where(
                        Device.device_type == "sensor",
                        Device.is_active == True,
                    )
                )
                sensors = result.scalars().all()

                if not sensors:
                    return

                now_str = datetime.now().isoformat()
                alert_rules = await self._get_alert_rules(db)

                for sensor in sensors:
                    metrics = self._get_sensor_metrics(sensor.code)

                    for metric_name in metrics:
                        config = self.METRIC_CONFIGS.get(metric_name)
                        if not config:
                            continue

                        # 生成模拟值（基础值 + 随机波动 + 时间趋势）
                        hour = datetime.now().hour
                        time_factor = 1.0
                        if metric_name == "temperature":
                            # 模拟昼夜温差
                            time_factor = 1.0 + 0.3 * (12 - abs(hour - 14)) / 6
                        elif metric_name == "light":
                            # 模拟光照日变化
                            time_factor = max(0.1, (12 - abs(hour - 12)) / 6)

                        value = config["base"] * time_factor + random.uniform(
                            -config["amplitude"], config["amplitude"]
                        )
                        value = round(max(0, value), 2)

                        # 写入 sensor_data 表
                        data = SensorData(
                            device_id=sensor.id,
                            metric_name=metric_name,
                            value=value,
                            unit=config["unit"],
                            time=now_str,
                            plot_id=sensor.plot_id,
                        )
                        db.add(data)

                        # 检查告警规则
                        await self._check_alerts(
                            db, alert_rules, sensor, metric_name, value, now_str
                        )

                await db.commit()
            except Exception:
                await db.rollback()
                raise

    def _get_sensor_metrics(self, sensor_code: str) -> list:
        """根据传感器编码获取其采集的指标类型。"""
        for suffix, metrics in self.SENSOR_TYPE_METRICS.items():
            if suffix in sensor_code:
                return metrics
        return ["temperature", "humidity"]  # 默认

    async def _get_alert_rules(self, db: AsyncSession) -> list:
        """获取所有活跃告警规则。"""
        result = await db.execute(
            select(AlertRule).where(AlertRule.is_active == True)
        )
        return result.scalars().all()

    async def _check_alerts(
        self,
        db: AsyncSession,
        rules: list,
        sensor: Device,
        metric_name: str,
        value: float,
        time_str: str,
    ):
        """检查告警规则是否触发。"""
        for rule in rules:
            if rule.metric_name != metric_name:
                continue
            # 如果规则指定了设备，检查是否匹配
            if rule.device_id and rule.device_id != sensor.id:
                continue
            # 如果规则指定了地块，检查是否匹配
            if rule.plot_id and rule.plot_id != sensor.plot_id:
                continue

            triggered = False
            if rule.operator == "gt" and value > rule.threshold_value:
                triggered = True
            elif rule.operator == "lt" and value < rule.threshold_value:
                triggered = True
            elif rule.operator == "gte" and value >= rule.threshold_value:
                triggered = True
            elif rule.operator == "lte" and value <= rule.threshold_value:
                triggered = True
            elif rule.operator == "eq" and abs(value - rule.threshold_value) < 0.01:
                triggered = True

            if triggered:
                alert = Alert(
                    title=f"[{rule.level.upper()}] {rule.name}",
                    level=rule.level,
                    status="triggered",
                    device_id=sensor.id,
                    plot_id=sensor.plot_id,
                    rule_id=rule.id,
                    metric_name=metric_name,
                    metric_value=value,
                    threshold_value=rule.threshold_value,
                    description=f"{sensor.name}: {metric_name}={value}, 阈值={rule.threshold_value}, {rule.description}",
                )
                db.add(alert)

    async def generate_control_records(self):
        """周期性生成模拟控制记录（灌溉、通风等）。"""
        async with async_session_factory() as db:
            try:
                result = await db.execute(
                    select(Device).where(
                        Device.device_type == "controller",
                        Device.is_active == True,
                    )
                )
                controllers = result.scalars().all()

                if not controllers:
                    return

                now = datetime.now()

                for ctrl in controllers:
                    # 每 5 分钟随机决定是否生成控制记录
                    if random.random() > 0.3:
                        continue

                    # 灌溉记录
                    irrigation = IrrigationRecord(
                        plot_id=ctrl.plot_id or "",
                        device_id=ctrl.id,
                        start_time=(now - timedelta(minutes=random.randint(10, 60))).isoformat(),
                        end_time=now.isoformat(),
                        water_amount=round(random.uniform(10, 100), 1),
                        method=random.choice(["drip", "sprinkler", "flood"]),
                        notes=f"自动灌溉 - {ctrl.name}",
                    )
                    db.add(irrigation)

                    # 通风记录（部分控制器）
                    if random.random() > 0.5:
                        ventilation = VentilationRecord(
                            plot_id=ctrl.plot_id or "",
                            device_id=ctrl.id,
                            start_time=(now - timedelta(minutes=random.randint(5, 30))).isoformat(),
                            end_time=now.isoformat(),
                            fan_speed=round(random.uniform(1, 5), 1),
                            notes=f"自动通风 - {ctrl.name}",
                        )
                        db.add(ventilation)

                await db.commit()
            except Exception:
                await db.rollback()
                raise


# 全局单例
data_generator = SensorDataGenerator()
