import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import PestControlRecord, User
from datetime import datetime

router = APIRouter(prefix="/pest-control", tags=["病虫害防治"])


@router.get("/records")
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    plot_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """除害记录列表"""
    conditions = []
    if plot_id:
        conditions.append(PestControlRecord.plot_id == plot_id)

    count_query = select(func.count(PestControlRecord.id))
    if conditions:
        count_query = count_query.where(*conditions)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = select(PestControlRecord)
    if conditions:
        query = query.where(*conditions)
    result = await db.execute(
        query.order_by(desc(PestControlRecord.apply_time))
        .offset((page - 1) * page_size).limit(page_size)
    )
    records = result.scalars().all()

    items = []
    for r in records:
        items.append({
            "id": r.id,
            "plot_id": r.plot_id,
            "pesticide_name": r.pesticide_name,
            "amount": r.amount,
            "method": r.method,
            "apply_time": r.apply_time,
            "target_pest": r.target_pest,
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
    pesticide_name: str = Query(...),
    amount: float = Query(...),
    method: str = Query(None),
    target_pest: str = Query(None),
    notes: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建除害记录"""
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    record = PestControlRecord(
        id=uuid.uuid4().hex,
        plot_id=plot_id,
        pesticide_name=pesticide_name,
        amount=amount,
        method=method,
        apply_time=now_str,
        target_pest=target_pest,
        operator_id=current_user.id,
        notes=notes,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "code": 200,
        "message": "除害记录已创建",
        "data": {
            "id": record.id,
            "plot_id": record.plot_id,
            "pesticide_name": record.pesticide_name,
            "amount": record.amount,
            "method": record.method,
            "apply_time": record.apply_time,
            "target_pest": record.target_pest,
            "operator_id": record.operator_id,
            "notes": record.notes,
        }
    }


@router.post("/detection")
async def report_detection(
    plot_id: str = Query(...),
    pest_type: str = Query(..., description="虫害类型"),
    severity: str = Query("low", description="严重程度: low/medium/high"),
    count: int = Query(0, description="检测到的数量"),
    notes: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上报虫情检测结果"""
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "code": 200,
        "message": "虫情检测已上报",
        "data": {
            "plot_id": plot_id,
            "pest_type": pest_type,
            "severity": severity,
            "count": count,
            "detection_time": now_str,
            "reported_by": current_user.id,
            "notes": notes,
        }
    }


@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """除害统计"""
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")

    result = await db.execute(
        select(func.count(PestControlRecord.id)).where(
            PestControlRecord.apply_time >= today_str
        )
    )
    today_count = result.scalar() or 0

    result = await db.execute(
        select(func.coalesce(func.sum(PestControlRecord.amount), 0)).where(
            PestControlRecord.apply_time >= today_str
        )
    )
    today_amount = result.scalar() or 0

    result = await db.execute(select(func.count(PestControlRecord.id)))
    total_count = result.scalar() or 0

    result = await db.execute(
        select(PestControlRecord.target_pest, func.count(PestControlRecord.id))
        .group_by(PestControlRecord.target_pest)
    )
    by_pest = [{"target": target, "count": cnt} for target, cnt in result.all()]

    return {
        "code": 200,
        "message": "success",
        "data": {
            "todayCount": today_count,
            "todayAmount": today_amount,
            "totalCount": total_count,
            "byPest": by_pest,
        }
    }
