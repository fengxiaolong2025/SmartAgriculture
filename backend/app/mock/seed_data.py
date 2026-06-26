"""
种子数据模块 - 初始化系统基础数据。
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password
from app.models.user import User
from app.models.plot import Plot
from app.models.crop import Crop
from app.models.device import Device
from app.models.alert_rule import AlertRule


async def seed_users(db: AsyncSession) -> dict:
    """创建默认用户。返回 {username: user} 映射。"""
    users = {}

    # 检查是否已存在
    result = await db.execute(select(User).where(User.username == "admin"))
    if result.scalar_one_or_none():
        return users

    user_data = [
        {"username": "admin", "password": "Admin@123456", "role": "super_admin",
         "full_name": "系统管理员", "email": "admin@agri.com"},
        {"username": "operator", "password": "Operator@123", "role": "operator",
         "full_name": "操作员", "email": "operator@agri.com"},
        {"username": "viewer", "password": "Viewer@123", "role": "viewer",
         "full_name": "访客", "email": "viewer@agri.com"},
    ]

    for ud in user_data:
        user = User(
            username=ud["username"],
            hashed_password=hash_password(ud["password"]),
            role=ud["role"],
            full_name=ud["full_name"],
            email=ud["email"],
        )
        db.add(user)
        users[ud["username"]] = user

    await db.flush()
    return users


async def seed_crops(db: AsyncSession) -> dict:
    """创建默认作物。返回 {name: crop} 映射。"""
    result = await db.execute(select(Crop).limit(1))
    if result.scalar_one_or_none():
        return {}

    crops_data = [
        {"name": "水稻", "variety": "南粳9108", "category": "粮食作物",
         "growth_cycle_days": 150, "optimal_temp_min": 20, "optimal_temp_max": 35,
         "optimal_humidity_min": 60, "optimal_humidity_max": 90,
         "optimal_soil_moisture_min": 60, "optimal_soil_moisture_max": 90},
        {"name": "番茄", "variety": "金棚一号", "category": "蔬菜",
         "growth_cycle_days": 120, "optimal_temp_min": 18, "optimal_temp_max": 30,
         "optimal_humidity_min": 50, "optimal_humidity_max": 80,
         "optimal_soil_moisture_min": 60, "optimal_soil_moisture_max": 80},
        {"name": "黄瓜", "variety": "津春4号", "category": "蔬菜",
         "growth_cycle_days": 90, "optimal_temp_min": 20, "optimal_temp_max": 32,
         "optimal_humidity_min": 60, "optimal_humidity_max": 85,
         "optimal_soil_moisture_min": 65, "optimal_soil_moisture_max": 85},
        {"name": "苹果", "variety": "红富士", "category": "水果",
         "growth_cycle_days": 200, "optimal_temp_min": 15, "optimal_temp_max": 28,
         "optimal_humidity_min": 50, "optimal_humidity_max": 75,
         "optimal_soil_moisture_min": 50, "optimal_soil_moisture_max": 75},
        {"name": "小麦", "variety": "济麦22", "category": "粮食作物",
         "growth_cycle_days": 240, "optimal_temp_min": 10, "optimal_temp_max": 25,
         "optimal_humidity_min": 40, "optimal_humidity_max": 70,
         "optimal_soil_moisture_min": 50, "optimal_soil_moisture_max": 75},
    ]

    crops = {}
    for cd in crops_data:
        crop = Crop(**cd)
        db.add(crop)
        crops[cd["name"]] = crop

    await db.flush()
    return crops


async def seed_plots(db: AsyncSession, crops: dict) -> list:
    """创建默认地块，关联作物。"""
    result = await db.execute(select(Plot).limit(1))
    if result.scalar_one_or_none():
        return []

    crop_list = list(crops.values())
    plots_data = [
        {"name": "A区1号棚", "code": "A1", "area": 2.5, "location": "园区A区东侧",
         "crop_name": "番茄", "planting_date": "2026-03-15"},
        {"name": "A区2号棚", "code": "A2", "area": 2.0, "location": "园区A区西侧",
         "crop_name": "黄瓜", "planting_date": "2026-04-01"},
        {"name": "B区1号田", "code": "B1", "area": 10.0, "location": "园区B区南侧",
         "crop_name": "水稻", "planting_date": "2026-05-10"},
        {"name": "B区2号田", "code": "B2", "area": 8.0, "location": "园区B区北侧",
         "crop_name": "小麦", "planting_date": "2025-10-20"},
        {"name": "C区1号园", "code": "C1", "area": 5.0, "location": "园区C区",
         "crop_name": "苹果", "planting_date": "2024-03-01"},
        {"name": "C区2号园", "code": "C2", "area": 3.0, "location": "园区C区",
         "crop_name": "苹果", "planting_date": "2025-03-01"},
        {"name": "D区1号棚", "code": "D1", "area": 1.5, "location": "园区D区东侧",
         "crop_name": "番茄", "planting_date": "2026-03-20"},
        {"name": "D区2号棚", "code": "D2", "area": 1.8, "location": "园区D区西侧",
         "crop_name": "黄瓜", "planting_date": "2026-04-15"},
    ]

    plots = []
    for pd in plots_data:
        crop = crops.get(pd.pop("crop_name"))
        plot = Plot(
            crop_id=crop.id if crop else None,
            planting_date=pd.pop("planting_date"),
            **pd,
        )
        db.add(plot)
        plots.append(plot)

    await db.flush()
    return plots


async def seed_devices(db: AsyncSession, plots: list) -> dict:
    """创建设备。返回 {"sensors": [...], "controllers": [...]}。"""
    result = await db.execute(select(Device).limit(1))
    if result.scalar_one_or_none():
        return {}

    sensors = []
    controllers = []

    sensor_types = ["temperature", "humidity", "soil_moisture", "light", "co2", "soil_ph"]
    plot_codes = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]

    # 为每个地块创建 2-3 个传感器
    for i, plot in enumerate(plots):
        plot_code = plot_codes[i]
        # 温湿度传感器
        s1 = Device(
            name=f"{plot_code}-温湿度传感器",
            code=f"SENSOR-{plot_code}-TH",
            device_type="sensor",
            model="SHT30",
            manufacturer="Sensirion",
            plot_id=plot.id,
        )
        db.add(s1)
        sensors.append(s1)

        # 土壤传感器
        s2 = Device(
            name=f"{plot_code}-土壤传感器",
            code=f"SENSOR-{plot_code}-SOIL",
            device_type="sensor",
            model="YL-69",
            manufacturer="Generic",
            plot_id=plot.id,
        )
        db.add(s2)
        sensors.append(s2)

        # 部分地块添加光照/CO2传感器
        if i < 4:
            s3 = Device(
                name=f"{plot_code}-光照CO2传感器",
                code=f"SENSOR-{plot_code}-LC",
                device_type="sensor",
                model="BH1750/MH-Z19",
                manufacturer="Generic",
                plot_id=plot.id,
            )
            db.add(s3)
            sensors.append(s3)

    # 为每个地块创建 1 个控制器
    for i, plot in enumerate(plots):
        plot_code = plot_codes[i]
        c = Device(
            name=f"{plot_code}-灌溉控制器",
            code=f"CTRL-{plot_code}-IRR",
            device_type="controller",
            model="IRR-C200",
            manufacturer="AgriTech",
            plot_id=plot.id,
        )
        db.add(c)
        controllers.append(c)

    await db.flush()
    return {"sensors": sensors, "controllers": controllers}


async def seed_alert_rules(db: AsyncSession, devices: dict) -> None:
    """创建默认告警规则。"""
    result = await db.execute(select(AlertRule).limit(1))
    if result.scalar_one_or_none():
        return

    rules = [
        {"name": "温度过高告警", "metric_name": "temperature", "operator": "gt",
         "threshold_value": 35.0, "level": "critical", "description": "温度超过35°C触发严重告警"},
        {"name": "温度过低告警", "metric_name": "temperature", "operator": "lt",
         "threshold_value": 5.0, "level": "major", "description": "温度低于5°C触发告警"},
        {"name": "湿度过低告警", "metric_name": "humidity", "operator": "lt",
         "threshold_value": 30.0, "level": "major", "description": "湿度低于30%触发告警"},
        {"name": "湿度过高告警", "metric_name": "humidity", "operator": "gt",
         "threshold_value": 95.0, "level": "minor", "description": "湿度超过95%触发告警"},
        {"name": "土壤湿度过低告警", "metric_name": "soil_moisture", "operator": "lt",
         "threshold_value": 20.0, "level": "major", "description": "土壤湿度低于20%触发告警"},
        {"name": "CO2浓度过高告警", "metric_name": "co2", "operator": "gt",
         "threshold_value": 2000.0, "level": "minor", "description": "CO2浓度超过2000ppm"},
        {"name": "光照强度过低告警", "metric_name": "light", "operator": "lt",
         "threshold_value": 500.0, "level": "info", "description": "光照强度低于500lux"},
    ]

    for rule in rules:
        alert_rule = AlertRule(**rule)
        db.add(alert_rule)

    await db.flush()


async def run_seed(db: AsyncSession) -> None:
    """执行所有种子数据初始化。"""
    users = await seed_users(db)
    crops = await seed_crops(db)
    plots = await seed_plots(db, crops)
    devices = await seed_devices(db, plots)
    await seed_alert_rules(db, devices)
    await db.commit()
