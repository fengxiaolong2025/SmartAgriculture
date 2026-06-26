import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import Device, SensorData, User
from app.schemas.device import DeviceCreate, DeviceUpdate
from datetime import datetime

router = APIRouter(prefix="/devices", tags=["设备管理"])


@router.get("/")
async def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    device_type: str = Query(None),
    status: str = Query(None),
    plot_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """设备列表"""
    conditions = [Device.is_active == True]
    if device_type:
        conditions.append(Device.device_type == device_type)
    if status:
        conditions.append(Device.status == status)
    if plot_id:
        conditions.append(Device.plot_id == plot_id)

    count_query = select(func.count(Device.id)).where(*conditions)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    result = await db.execute(
        select(Device).where(*conditions).order_by(desc(Device.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    )
    devices = result.scalars().all()

    items = []
    for d in devices:
        items.append({
            "id": d.id,
            "name": d.name,
            "code": d.code,
            "device_type": d.device_type,
            "model": d.model,
            "manufacturer": d.manufacturer,
            "plot_id": d.plot_id,
            "status": d.status,
            "is_active": d.is_active,
            "description": d.description,
            "created_at": str(d.created_at) if d.created_at else None,
            "updated_at": str(d.updated_at) if d.updated_at else None,
        })

    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    }


@router.post("/")
async def create_device(
    payload: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """注册设备"""
    # 检查 code 唯一性
    result = await db.execute(select(Device).where(Device.code == payload.code))
    existing = result.scalar_one_or_none()
    if existing:
        return {"code": 400, "message": "设备编码已存在", "data": None}

    device = Device(
        id=uuid.uuid4().hex,
        name=payload.name,
        code=payload.code,
        device_type=payload.device_type,
        model=payload.model,
        manufacturer=payload.manufacturer,
        plot_id=payload.plot_id,
        status=payload.status,
        is_active=payload.is_active,
        description=payload.description,
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)

    return {
        "code": 200,
        "message": "设备注册成功",
        "data": {
            "id": device.id,
            "name": device.name,
            "code": device.code,
            "device_type": device.device_type,
            "model": device.model,
            "manufacturer": device.manufacturer,
            "plot_id": device.plot_id,
            "status": device.status,
            "is_active": device.is_active,
            "description": device.description,
            "created_at": str(device.created_at) if device.created_at else None,
        }
    }


@router.get("/{device_id}")
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)):
    """设备详情"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        return {"code": 404, "message": "设备不存在", "data": None}
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": device.id,
            "name": device.name,
            "code": device.code,
            "device_type": device.device_type,
            "model": device.model,
            "manufacturer": device.manufacturer,
            "plot_id": device.plot_id,
            "status": device.status,
            "is_active": device.is_active,
            "description": device.description,
            "created_at": str(device.created_at) if device.created_at else None,
            "updated_at": str(device.updated_at) if device.updated_at else None,
        }
    }


@router.put("/{device_id}")
async def update_device(
    device_id: str,
    payload: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新设备"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        return {"code": 404, "message": "设备不存在", "data": None}

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(device, key, value)

    await db.commit()
    await db.refresh(device)

    return {
        "code": 200,
        "message": "设备更新成功",
        "data": {
            "id": device.id,
            "name": device.name,
            "code": device.code,
            "device_type": device.device_type,
            "model": device.model,
            "manufacturer": device.manufacturer,
            "plot_id": device.plot_id,
            "status": device.status,
            "is_active": device.is_active,
            "description": device.description,
            "updated_at": str(device.updated_at) if device.updated_at else None,
        }
    }


@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除设备（软删除）"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        return {"code": 404, "message": "设备不存在", "data": None}
    device.is_active = False
    await db.commit()
    return {"code": 200, "message": "设备已删除", "data": None}


@router.post("/{device_id}/command")
async def send_device_command(
    device_id: str,
    command: str = Query(..., description="控制指令: on/off"),
    params: str = Query("{}", description="额外参数 JSON"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """下发控制指令"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        return {"code": 404, "message": "设备不存在", "data": None}
    if device.device_type not in ("controller", "actuator"):
        return {"code": 400, "message": "该设备不支持控制指令", "data": None}

    import json
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        params_dict = {}

    return {
        "code": 200,
        "message": f"指令 {command} 已下发",
        "data": {
            "device_id": device.id,
            "device_name": device.name,
            "command": command,
            "params": params_dict,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }
    }


@router.get("/{device_id}/telemetry/latest")
async def get_device_telemetry_latest(device_id: str, db: AsyncSession = Depends(get_db)):
    """获取最新遥测数据"""
    result = await db.execute(
        select(SensorData).where(SensorData.device_id == device_id)
        .order_by(desc(SensorData.time)).limit(10)
    )
    rows = result.scalars().all()
    telemetry = {}
    for r in rows:
        if r.metric_name not in telemetry:
            telemetry[r.metric_name] = {"value": r.value, "unit": r.unit, "time": r.time}
    return {"code": 200, "message": "success", "data": telemetry}


@router.get("/{device_id}/telemetry/history")
async def get_device_telemetry_history(
    device_id: str,
    start: str = Query(None, description="开始时间"),
    end: str = Query(None, description="结束时间"),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """历史遥测数据"""
    conditions = [SensorData.device_id == device_id]
    if start:
        conditions.append(SensorData.time >= start)
    if end:
        conditions.append(SensorData.time <= end)

    result = await db.execute(
        select(SensorData).where(*conditions).order_by(desc(SensorData.time)).limit(limit)
    )
    rows = result.scalars().all()
    data = []
    for r in rows:
        data.append({
            "id": r.id,
            "metric_name": r.metric_name,
            "value": r.value,
            "unit": r.unit,
            "time": r.time,
            "plot_id": r.plot_id,
        })
    return {"code": 200, "message": "success", "data": data}
