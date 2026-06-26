import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import AlertRule, User

router = APIRouter(prefix="/alert-rules", tags=["告警规则"])


@router.get("/")
async def list_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """规则列表"""
    count_result = await db.execute(select(func.count(AlertRule.id)))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(AlertRule).order_by(desc(AlertRule.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    )
    rules = result.scalars().all()

    items = []
    for r in rules:
        items.append({
            "id": r.id,
            "name": r.name,
            "metric_name": r.metric_name,
            "operator": r.operator,
            "threshold_value": r.threshold_value,
            "level": r.level,
            "device_id": r.device_id,
            "plot_id": r.plot_id,
            "is_active": r.is_active,
            "description": r.description,
            "created_at": str(r.created_at) if r.created_at else None,
            "updated_at": str(r.updated_at) if r.updated_at else None,
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
async def create_rule(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建规则（需要请求体，这里简化处理）"""
    return {"code": 400, "message": "请提供规则参数", "data": None}


@router.get("/{rule_id}")
async def get_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    """规则详情"""
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        return {"code": 404, "message": "规则不存在", "data": None}
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": rule.id,
            "name": rule.name,
            "metric_name": rule.metric_name,
            "operator": rule.operator,
            "threshold_value": rule.threshold_value,
            "level": rule.level,
            "device_id": rule.device_id,
            "plot_id": rule.plot_id,
            "is_active": rule.is_active,
            "description": rule.description,
            "created_at": str(rule.created_at) if rule.created_at else None,
            "updated_at": str(rule.updated_at) if rule.updated_at else None,
        }
    }


@router.put("/{rule_id}")
async def update_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新规则"""
    return {"code": 200, "message": "请提供更新参数", "data": None}


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除规则"""
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        return {"code": 404, "message": "规则不存在", "data": None}
    await db.delete(rule)
    await db.commit()
    return {"code": 200, "message": "规则已删除", "data": None}


@router.put("/{rule_id}/toggle")
async def toggle_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """启用/禁用规则"""
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        return {"code": 404, "message": "规则不存在", "data": None}
    rule.is_active = not rule.is_active
    await db.commit()
    await db.refresh(rule)
    return {
        "code": 200,
        "message": f"规则已{'启用' if rule.is_active else '禁用'}",
        "data": {"id": rule.id, "is_active": rule.is_active}
    }
