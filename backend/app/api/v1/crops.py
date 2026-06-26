import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import Crop, User

router = APIRouter(prefix="/crops", tags=["作物管理"])


@router.get("/")
async def list_crops(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """作物列表"""
    conditions = []
    if category:
        conditions.append(Crop.category == category)

    count_query = select(func.count(Crop.id))
    if conditions:
        count_query = count_query.where(*conditions)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = select(Crop)
    if conditions:
        query = query.where(*conditions)
    result = await db.execute(
        query.order_by(desc(Crop.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    )
    crops = result.scalars().all()

    items = []
    for c in crops:
        items.append({
            "id": c.id,
            "name": c.name,
            "variety": c.variety,
            "category": c.category,
            "growth_cycle_days": c.growth_cycle_days,
            "optimal_temp_min": c.optimal_temp_min,
            "optimal_temp_max": c.optimal_temp_max,
            "optimal_humidity_min": c.optimal_humidity_min,
            "optimal_humidity_max": c.optimal_humidity_max,
            "optimal_soil_moisture_min": c.optimal_soil_moisture_min,
            "optimal_soil_moisture_max": c.optimal_soil_moisture_max,
            "description": c.description,
            "created_at": str(c.created_at) if c.created_at else None,
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
async def create_crop(
    name: str = Query(...),
    variety: str = Query(None),
    category: str = Query(None),
    growth_cycle_days: int = Query(None),
    optimal_temp_min: float = Query(None),
    optimal_temp_max: float = Query(None),
    optimal_humidity_min: float = Query(None),
    optimal_humidity_max: float = Query(None),
    description: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加作物"""
    crop = Crop(
        id=uuid.uuid4().hex,
        name=name,
        variety=variety,
        category=category,
        growth_cycle_days=growth_cycle_days,
        optimal_temp_min=optimal_temp_min,
        optimal_temp_max=optimal_temp_max,
        optimal_humidity_min=optimal_humidity_min,
        optimal_humidity_max=optimal_humidity_max,
        description=description,
    )
    db.add(crop)
    await db.commit()
    await db.refresh(crop)

    return {
        "code": 200,
        "message": "作物已添加",
        "data": {
            "id": crop.id,
            "name": crop.name,
            "variety": crop.variety,
            "category": crop.category,
            "growth_cycle_days": crop.growth_cycle_days,
        }
    }


@router.get("/{crop_id}")
async def get_crop(crop_id: str, db: AsyncSession = Depends(get_db)):
    """作物详情"""
    result = await db.execute(select(Crop).where(Crop.id == crop_id))
    crop = result.scalar_one_or_none()
    if not crop:
        return {"code": 404, "message": "作物不存在", "data": None}
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": crop.id,
            "name": crop.name,
            "variety": crop.variety,
            "category": crop.category,
            "growth_cycle_days": crop.growth_cycle_days,
            "optimal_temp_min": crop.optimal_temp_min,
            "optimal_temp_max": crop.optimal_temp_max,
            "optimal_humidity_min": crop.optimal_humidity_min,
            "optimal_humidity_max": crop.optimal_humidity_max,
            "optimal_soil_moisture_min": crop.optimal_soil_moisture_min,
            "optimal_soil_moisture_max": crop.optimal_soil_moisture_max,
            "description": crop.description,
            "created_at": str(crop.created_at) if crop.created_at else None,
            "updated_at": str(crop.updated_at) if crop.updated_at else None,
        }
    }


@router.put("/{crop_id}")
async def update_crop(
    crop_id: str,
    name: str = Query(None),
    variety: str = Query(None),
    category: str = Query(None),
    growth_cycle_days: int = Query(None),
    optimal_temp_min: float = Query(None),
    optimal_temp_max: float = Query(None),
    optimal_humidity_min: float = Query(None),
    optimal_humidity_max: float = Query(None),
    description: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新作物"""
    result = await db.execute(select(Crop).where(Crop.id == crop_id))
    crop = result.scalar_one_or_none()
    if not crop:
        return {"code": 404, "message": "作物不存在", "data": None}

    updates = {
        "name": name, "variety": variety, "category": category,
        "growth_cycle_days": growth_cycle_days, "optimal_temp_min": optimal_temp_min,
        "optimal_temp_max": optimal_temp_max, "optimal_humidity_min": optimal_humidity_min,
        "optimal_humidity_max": optimal_humidity_max, "description": description,
    }
    for key, value in updates.items():
        if value is not None:
            setattr(crop, key, value)

    await db.commit()
    await db.refresh(crop)

    return {"code": 200, "message": "作物已更新", "data": {"id": crop.id, "name": crop.name}}


@router.delete("/{crop_id}")
async def delete_crop(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除作物"""
    result = await db.execute(select(Crop).where(Crop.id == crop_id))
    crop = result.scalar_one_or_none()
    if not crop:
        return {"code": 404, "message": "作物不存在", "data": None}
    await db.delete(crop)
    await db.commit()
    return {"code": 200, "message": "作物已删除", "data": None}
