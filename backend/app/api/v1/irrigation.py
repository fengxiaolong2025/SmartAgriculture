import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import IrrigationRecord, User
from datetime import datetime

router = APIRouter(prefix="/irrigation", tags=["灌溉管理"])


@router.get("/records")
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    plot_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """灌溉记录列表"""
    conditions = []
    if plot_id:
        conditions.append(IrrigationRecord.plot_id == plot_id)

    count_query = select(func.count(IrrigationRecord.id))
    if conditions:
        count_query = count_query.where(*conditions)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = select(IrrigationRecord)
    if conditions:
        query = query.where(*conditions)
    result = await db.execute(
        query.order_by(desc(IrrigationRecord.start_time))
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
            "water_amount": r.water_amount,
            "method": r.method,
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
async def control_irrigation(
    plot_id: str = Query(...),
    action: str = Query(..., description="start/stop"),
    duration: int = Query(0, description="灌溉时长（分钟）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """手动控制灌溉"""
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if action == "start":
        record = IrrigationRecord(
            id=uuid.uuid4().hex,
            plot_id=plot_id,
            start_time=now_str,
            method="manual",
            operator_id=current_user.id,
            notes=f"手动启动灌溉, 计划时长{duration}分钟",
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return {
            "code": 200,
            "message": "灌溉已启动",
            "data": {
                "id": record.id,
                "plot_id": plot_id,
                "action": "start",
                "start_time": now_str,
                "duration": duration,
            }
        }
    elif action == "stop":
        # 查找最近一条未结束的灌溉记录
        result = await db.execute(
            select(IrrigationRecord).where(
                IrrigationRecord.plot_id == plot_id,
                IrrigationRecord.end_time == None
            ).order_by(desc(IrrigationRecord.start_time)).limit(1)
        )
        record = result.scalar_one_or_none()
        if record:
            record.end_time = now_str
            # 计算水量
            start_dt = datetime.strptime(record.start_time, "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.utcnow() - start_dt).total_seconds() / 60
            record.water_amount = round(elapsed * 10, 2)  # 假设 10L/分钟
            await db.commit()
            await db.refresh(record)
            return {
                "code": 200,
                "message": "灌溉已停止",
                "data": {
                    "id": record.id,
                    "plot_id": plot_id,
                    "action": "stop",
                    "end_time": now_str,
                    "water_amount": record.water_amount,
                }
            }
        else:
            return {"code": 200, "message": "没有正在进行的灌溉", "data": {"action": "stop"}}

    return {"code": 400, "message": "无效的操作", "data": None}


@router.get("/status")
async def get_irrigation_status(db: AsyncSession = Depends(get_db)):
    """当前灌溉状态"""
    result = await db.execute(
        select(IrrigationRecord).where(IrrigationRecord.end_time == None)
        .order_by(desc(IrrigationRecord.start_time))
    )
    active = result.scalars().all()
    data = []
    for r in active:
        data.append({
            "id": r.id,
            "plot_id": r.plot_id,
            "start_time": r.start_time,
            "method": r.method,
            "is_active": True,
        })
    return {"code": 200, "message": "success", "data": data}


@router.get("/statistics")
async def get_irrigation_statistics(db: AsyncSession = Depends(get_db)):
    """灌溉统计"""
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")

    result = await db.execute(
        select(func.coalesce(func.sum(IrrigationRecord.water_amount), 0)).where(
            IrrigationRecord.start_time >= today_str
        )
    )
    today_total = result.scalar() or 0

    result = await db.execute(
        select(func.count(IrrigationRecord.id)).where(
            IrrigationRecord.start_time >= today_str
        )
    )
    today_count = result.scalar() or 0

    result = await db.execute(
        select(func.coalesce(func.sum(IrrigationRecord.water_amount), 0))
    )
    total_water = result.scalar() or 0

    result = await db.execute(select(func.count(IrrigationRecord.id)))
    total_count = result.scalar() or 0

    return {
        "code": 200,
        "message": "success",
        "data": {
            "todayWater": today_total,
            "todayCount": today_count,
            "totalWater": total_water,
            "totalCount": total_count,
        }
    }
