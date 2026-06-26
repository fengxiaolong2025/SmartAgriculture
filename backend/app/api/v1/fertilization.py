import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import FertilizationRecord, User
from datetime import datetime

router = APIRouter(prefix="/fertilization", tags=["施肥管理"])


@router.get("/records")
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    plot_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """施肥记录列表"""
    conditions = []
    if plot_id:
        conditions.append(FertilizationRecord.plot_id == plot_id)

    count_query = select(func.count(FertilizationRecord.id))
    if conditions:
        count_query = count_query.where(*conditions)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = select(FertilizationRecord)
    if conditions:
        query = query.where(*conditions)
    result = await db.execute(
        query.order_by(desc(FertilizationRecord.apply_time))
        .offset((page - 1) * page_size).limit(page_size)
    )
    records = result.scalars().all()

    items = []
    for r in records:
        items.append({
            "id": r.id,
            "plot_id": r.plot_id,
            "device_id": r.device_id,
            "fertilizer_name": r.fertilizer_name,
            "amount": r.amount,
            "method": r.method,
            "apply_time": r.apply_time,
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


@router.post("/records")
async def create_record(
    plot_id: str = Query(...),
    fertilizer_name: str = Query(...),
    amount: float = Query(...),
    method: str = Query(None),
    notes: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建施肥记录"""
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    record = FertilizationRecord(
        id=uuid.uuid4().hex,
        plot_id=plot_id,
        fertilizer_name=fertilizer_name,
        amount=amount,
        method=method,
        apply_time=now_str,
        operator_id=current_user.id,
        notes=notes,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "code": 200,
        "message": "施肥记录已创建",
        "data": {
            "id": record.id,
            "plot_id": record.plot_id,
            "fertilizer_name": record.fertilizer_name,
            "amount": record.amount,
            "method": record.method,
            "apply_time": record.apply_time,
            "operator_id": record.operator_id,
            "notes": record.notes,
        }
    }


@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """施肥统计"""
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")

    result = await db.execute(
        select(func.coalesce(func.sum(FertilizationRecord.amount), 0)).where(
            FertilizationRecord.apply_time >= today_str
        )
    )
    today_amount = result.scalar() or 0

    result = await db.execute(
        select(func.count(FertilizationRecord.id)).where(
            FertilizationRecord.apply_time >= today_str
        )
    )
    today_count = result.scalar() or 0

    result = await db.execute(
        select(func.coalesce(func.sum(FertilizationRecord.amount), 0))
    )
    total_amount = result.scalar() or 0

    result = await db.execute(select(func.count(FertilizationRecord.id)))
    total_count = result.scalar() or 0

    # 按肥料名称统计
    result = await db.execute(
        select(FertilizationRecord.fertilizer_name, func.sum(FertilizationRecord.amount))
        .group_by(FertilizationRecord.fertilizer_name)
    )
    by_type = [{"name": name, "total": float(total)} for name, total in result.all()]

    return {
        "code": 200,
        "message": "success",
        "data": {
            "todayAmount": today_amount,
            "todayCount": today_count,
            "totalAmount": total_amount,
            "totalCount": total_count,
            "byType": by_type,
        }
    }
