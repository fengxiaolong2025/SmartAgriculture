import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import VentilationRecord, User
from datetime import datetime

router = APIRouter(prefix="/ventilation", tags=["通风管理"])


@router.get("/records")
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    plot_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """通风记录列表"""
    conditions = []
    if plot_id:
        conditions.append(VentilationRecord.plot_id == plot_id)

    count_query = select(func.count(VentilationRecord.id))
    if conditions:
        count_query = count_query.where(*conditions)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = select(VentilationRecord)
    if conditions:
        query = query.where(*conditions)
    result = await db.execute(
        query.order_by(desc(VentilationRecord.start_time))
        .offset((page - 1) * page_size).limit(page_size)
    )
    records = result.scalars().all()

    items = []
    for r in records:
        items.append({
            "id": r.id,
            "plot_id": r.plot_id,
            "device_id": r.device_id,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "fan_speed": r.fan_speed,
            "operator_id": r.operator_id,
            "notes": r.notes,
            "created_at": str(r.created_at) if r.created_at else None,
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


@router.post("/control")
async def control_ventilation(
    plot_id: str = Query(...),
    action: str = Query(..., description="start/stop"),
    fan_speed: int = Query(1, description="风扇速度档位"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """控制通风设备"""
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if action == "start":
        record = VentilationRecord(
            id=uuid.uuid4().hex,
            plot_id=plot_id,
            start_time=now_str,
            fan_speed=float(fan_speed),
            operator_id=current_user.id,
            notes=f"手动启动通风, 风速档位{fan_speed}",
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return {
            "code": 200,
            "message": "通风已启动",
            "data": {
                "id": record.id,
                "plot_id": plot_id,
                "action": "start",
                "start_time": now_str,
                "fan_speed": fan_speed,
            }
        }
    elif action == "stop":
        result = await db.execute(
            select(VentilationRecord).where(
                VentilationRecord.plot_id == plot_id,
                VentilationRecord.end_time == None
            ).order_by(desc(VentilationRecord.start_time)).limit(1)
        )
        record = result.scalar_one_or_none()
        if record:
            record.end_time = now_str
            await db.commit()
            await db.refresh(record)
            return {
                "code": 200,
                "message": "通风已停止",
                "data": {
                    "id": record.id,
                    "plot_id": plot_id,
                    "action": "stop",
                    "end_time": now_str,
                }
            }
        else:
            return {"code": 200, "message": "没有正在进行的通风", "data": {"action": "stop"}}

    return {"code": 400, "message": "无效的操作", "data": None}


@router.get("/status")
async def get_ventilation_status(db: AsyncSession = Depends(get_db)):
    """当前通风状态"""
    result = await db.execute(
        select(VentilationRecord).where(VentilationRecord.end_time == None)
        .order_by(desc(VentilationRecord.start_time))
    )
    active = result.scalars().all()
    data = []
    for r in active:
        data.append({
            "id": r.id,
            "plot_id": r.plot_id,
            "device_id": r.device_id,
            "start_time": r.start_time,
            "fan_speed": r.fan_speed,
            "is_active": True,
        })
    return {"code": 200, "message": "success", "data": data}


@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """通风统计"""
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")

    result = await db.execute(
        select(func.count(VentilationRecord.id)).where(
            VentilationRecord.start_time >= today_str
        )
    )
    today_count = result.scalar() or 0

    result = await db.execute(select(func.count(VentilationRecord.id)))
    total_count = result.scalar() or 0

    # 总通风时长（估算）
    result = await db.execute(
        select(VentilationRecord).where(
            VentilationRecord.start_time >= today_str,
            VentilationRecord.end_time != None
        )
    )
    today_records = result.scalars().all()
    total_minutes = 0
    for r in today_records:
        try:
            start_dt = datetime.strptime(r.start_time, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(r.end_time, "%Y-%m-%d %H:%M:%S")
            total_minutes += (end_dt - start_dt).total_seconds() / 60
        except (ValueError, TypeError):
            pass

    return {
        "code": 200,
        "message": "success",
        "data": {
            "todayCount": today_count,
            "todayMinutes": round(total_minutes, 1),
            "totalCount": total_count,
        }
    }
