import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import HarvestRecord, Crop, Plot, User
from datetime import datetime

router = APIRouter(prefix="/harvest", tags=["采收管理"])


@router.get("/records")
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    plot_id: str = Query(None),
    crop_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """采收记录列表"""
    conditions = []
    if plot_id:
        conditions.append(HarvestRecord.plot_id == plot_id)
    if crop_id:
        conditions.append(HarvestRecord.crop_id == crop_id)

    count_query = select(func.count(HarvestRecord.id))
    if conditions:
        count_query = count_query.where(*conditions)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = select(HarvestRecord)
    if conditions:
        query = query.where(*conditions)
    result = await db.execute(
        query.order_by(desc(HarvestRecord.harvest_time))
        .offset((page - 1) * page_size).limit(page_size)
    )
    records = result.scalars().all()

    items = []
    for r in records:
        items.append({
            "id": r.id,
            "plot_id": r.plot_id,
            "crop_id": r.crop_id,
            "harvest_time": r.harvest_time,
            "yield_amount": r.yield_amount,
            "quality_grade": r.quality_grade,
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
    yield_amount: float = Query(...),
    harvest_time: str = Query(None),
    quality_grade: str = Query(None),
    notes: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建采收记录"""
    if not harvest_time:
        harvest_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # 查找地块关联的作物
    result = await db.execute(select(Plot).where(Plot.id == plot_id))
    plot = result.scalar_one_or_none()
    crop_id = plot.crop_id if plot else None

    record = HarvestRecord(
        id=uuid.uuid4().hex,
        plot_id=plot_id,
        crop_id=crop_id,
        harvest_time=harvest_time,
        yield_amount=yield_amount,
        quality_grade=quality_grade,
        operator_id=current_user.id,
        notes=notes,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "code": 200,
        "message": "采收记录已创建",
        "data": {
            "id": record.id,
            "plot_id": record.plot_id,
            "crop_id": record.crop_id,
            "harvest_time": record.harvest_time,
            "yield_amount": record.yield_amount,
            "quality_grade": record.quality_grade,
            "operator_id": record.operator_id,
            "notes": record.notes,
        }
    }


@router.get("/predictions")
async def get_predictions(db: AsyncSession = Depends(get_db)):
    """成熟度预测列表"""
    now = datetime.utcnow()
    result = await db.execute(select(Crop).limit(20))
    crops = result.scalars().all()

    predictions = []
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
        predictions.append({
            "crop_id": crop.id,
            "crop_name": crop.name,
            "variety": crop.variety,
            "plot_name": plot.name if plot else None,
            "planting_date": plot.planting_date if plot else None,
            "growth_cycle_days": growth_cycle,
            "days_planted": days_planted,
            "days_remaining": days_remaining,
            "progress": progress,
            "status": "成熟" if progress >= 100 else ("接近成熟" if progress >= 80 else "生长期"),
        })
    return {"code": 200, "message": "success", "data": predictions}


@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """采收统计"""
    result = await db.execute(
        select(func.coalesce(func.sum(HarvestRecord.yield_amount), 0))
    )
    total_yield = result.scalar() or 0

    result = await db.execute(select(func.count(HarvestRecord.id)))
    total_count = result.scalar() or 0

    # 按质量等级统计
    result = await db.execute(
        select(HarvestRecord.quality_grade, func.count(HarvestRecord.id), func.sum(HarvestRecord.yield_amount))
        .group_by(HarvestRecord.quality_grade)
    )
    by_quality = []
    for grade, count, amount in result.all():
        by_quality.append({
            "grade": grade,
            "count": count,
            "totalYield": float(amount or 0),
        })

    # 按月产量
    result = await db.execute(
        select(HarvestRecord.harvest_time, HarvestRecord.yield_amount)
        .order_by(desc(HarvestRecord.harvest_time)).limit(12)
    )
    monthly = []
    for time_str, amount in result.all():
        if time_str:
            monthly.append({
                "month": time_str[:7],
                "yield": float(amount or 0),
            })

    return {
        "code": 200,
        "message": "success",
        "data": {
            "totalYield": total_yield,
            "totalCount": total_count,
            "byQuality": by_quality,
            "monthly": monthly,
        }
    }
