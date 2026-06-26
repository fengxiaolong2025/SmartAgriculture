import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import Plot, SensorData, User

router = APIRouter(prefix="/plots", tags=["地块管理"])


@router.get("/")
async def list_plots(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """地块列表"""
    result = await db.execute(select(func.count(Plot.id)))
    total = result.scalar() or 0

    result = await db.execute(
        select(Plot).order_by(desc(Plot.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    )
    plots = result.scalars().all()

    items = []
    for p in plots:
        items.append({
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "area": p.area,
            "location": p.location,
            "description": p.description,
            "crop_id": p.crop_id,
            "planting_date": p.planting_date,
            "created_at": str(p.created_at) if p.created_at else None,
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
async def create_plot(
    name: str = Query(...),
    code: str = Query(...),
    area: float = Query(None),
    location: str = Query(None),
    description: str = Query(None),
    crop_id: str = Query(None),
    planting_date: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建地块"""
    # 检查 code 唯一性
    result = await db.execute(select(Plot).where(Plot.code == code))
    existing = result.scalar_one_or_none()
    if existing:
        return {"code": 400, "message": "地块编码已存在", "data": None}

    plot = Plot(
        id=uuid.uuid4().hex,
        name=name,
        code=code,
        area=area,
        location=location,
        description=description,
        crop_id=crop_id,
        planting_date=planting_date,
    )
    db.add(plot)
    await db.commit()
    await db.refresh(plot)

    return {
        "code": 200,
        "message": "地块已创建",
        "data": {
            "id": plot.id,
            "name": plot.name,
            "code": plot.code,
            "area": plot.area,
            "location": plot.location,
            "crop_id": plot.crop_id,
            "planting_date": plot.planting_date,
        }
    }


@router.get("/{plot_id}")
async def get_plot(plot_id: str, db: AsyncSession = Depends(get_db)):
    """地块详情（含当前传感器数据）"""
    result = await db.execute(select(Plot).where(Plot.id == plot_id))
    plot = result.scalar_one_or_none()
    if not plot:
        return {"code": 404, "message": "地块不存在", "data": None}

    # 获取最新传感器数据
    result2 = await db.execute(
        select(SensorData).where(SensorData.plot_id == plot_id)
        .order_by(desc(SensorData.time)).limit(10)
    )
    sensor_rows = result2.scalars().all()
    sensors = {}
    for s in sensor_rows:
        if s.metric_name not in sensors:
            sensors[s.metric_name] = {"value": s.value, "unit": s.unit, "time": s.time}

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": plot.id,
            "name": plot.name,
            "code": plot.code,
            "area": plot.area,
            "location": plot.location,
            "description": plot.description,
            "crop_id": plot.crop_id,
            "planting_date": plot.planting_date,
            "sensors": sensors,
            "created_at": str(plot.created_at) if plot.created_at else None,
            "updated_at": str(plot.updated_at) if plot.updated_at else None,
        }
    }


@router.put("/{plot_id}")
async def update_plot(
    plot_id: str,
    name: str = Query(None),
    area: float = Query(None),
    location: str = Query(None),
    description: str = Query(None),
    crop_id: str = Query(None),
    planting_date: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新地块"""
    result = await db.execute(select(Plot).where(Plot.id == plot_id))
    plot = result.scalar_one_or_none()
    if not plot:
        return {"code": 404, "message": "地块不存在", "data": None}

    updates = {
        "name": name, "area": area, "location": location,
        "description": description, "crop_id": crop_id, "planting_date": planting_date,
    }
    for key, value in updates.items():
        if value is not None:
            setattr(plot, key, value)

    await db.commit()
    await db.refresh(plot)

    return {"code": 200, "message": "地块已更新", "data": {"id": plot.id, "name": plot.name}}


@router.delete("/{plot_id}")
async def delete_plot(
    plot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除地块"""
    result = await db.execute(select(Plot).where(Plot.id == plot_id))
    plot = result.scalar_one_or_none()
    if not plot:
        return {"code": 404, "message": "地块不存在", "data": None}
    await db.delete(plot)
    await db.commit()
    return {"code": 200, "message": "地块已删除", "data": None}
