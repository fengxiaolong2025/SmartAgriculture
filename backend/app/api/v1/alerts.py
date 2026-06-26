from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import Alert, User
from datetime import datetime

router = APIRouter(prefix="/alerts", tags=["告警管理"])


@router.get("/")
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    level: str = Query(None, description="告警级别: critical/major/minor/info"),
    status: str = Query(None, description="告警状态: triggered/acknowledged/handled/closed"),
    plot_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """告警列表，支持分页和筛选"""
    conditions = []
    if level:
        conditions.append(Alert.level == level)
    if status:
        conditions.append(Alert.status == status)
    if plot_id:
        conditions.append(Alert.plot_id == plot_id)

    base_query = select(Alert)
    if conditions:
        base_query = base_query.where(*conditions)

    count_query = select(func.count(Alert.id))
    if conditions:
        count_query = count_query.where(*conditions)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    result = await db.execute(
        base_query.order_by(desc(Alert.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    )
    alerts = result.scalars().all()

    items = []
    for a in alerts:
        items.append({
            "id": a.id,
            "title": a.title,
            "level": a.level,
            "status": a.status,
            "device_id": a.device_id,
            "plot_id": a.plot_id,
            "rule_id": a.rule_id,
            "metric_name": a.metric_name,
            "metric_value": a.metric_value,
            "threshold_value": a.threshold_value,
            "description": a.description,
            "acknowledged_by": a.acknowledged_by,
            "acknowledged_at": a.acknowledged_at,
            "handled_by": a.handled_by,
            "handled_at": a.handled_at,
            "created_at": str(a.created_at) if a.created_at else None,
            "updated_at": str(a.updated_at) if a.updated_at else None,
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


@router.get("/latest")
async def get_latest_alerts(db: AsyncSession = Depends(get_db)):
    """最新20条告警"""
    result = await db.execute(
        select(Alert).order_by(desc(Alert.created_at)).limit(20)
    )
    alerts = result.scalars().all()
    items = []
    for a in alerts:
        items.append({
            "id": a.id,
            "title": a.title,
            "level": a.level,
            "status": a.status,
            "device_id": a.device_id,
            "plot_id": a.plot_id,
            "rule_id": a.rule_id,
            "metric_name": a.metric_name,
            "metric_value": a.metric_value,
            "threshold_value": a.threshold_value,
            "description": a.description,
            "acknowledged_by": a.acknowledged_by,
            "acknowledged_at": a.acknowledged_at,
            "handled_by": a.handled_by,
            "handled_at": a.handled_at,
            "created_at": str(a.created_at) if a.created_at else None,
            "updated_at": str(a.updated_at) if a.updated_at else None,
        })
    return {"code": 200, "message": "success", "data": items}


@router.get("/statistics")
async def get_alert_statistics(db: AsyncSession = Depends(get_db)):
    """告警统计 - 各级别数量"""
    result = await db.execute(
        select(Alert.level, func.count(Alert.id)).group_by(Alert.level)
    )
    rows = result.all()
    stats = {"critical": 0, "major": 0, "minor": 0, "info": 0}
    for level, count in rows:
        if level in stats:
            stats[level] = count
    # 总告警数
    result = await db.execute(select(func.count(Alert.id)))
    total = result.scalar() or 0
    return {"code": 200, "message": "success", "data": {"total": total, "byLevel": stats}}


@router.get("/{alert_id}")
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    """告警详情"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    a = result.scalar_one_or_none()
    if not a:
        return {"code": 404, "message": "告警不存在", "data": None}
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": a.id,
            "title": a.title,
            "level": a.level,
            "status": a.status,
            "device_id": a.device_id,
            "plot_id": a.plot_id,
            "rule_id": a.rule_id,
            "metric_name": a.metric_name,
            "metric_value": a.metric_value,
            "threshold_value": a.threshold_value,
            "description": a.description,
            "acknowledged_by": a.acknowledged_by,
            "acknowledged_at": a.acknowledged_at,
            "handled_by": a.handled_by,
            "handled_at": a.handled_at,
            "created_at": str(a.created_at) if a.created_at else None,
            "updated_at": str(a.updated_at) if a.updated_at else None,
        }
    }


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """确认告警"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"code": 404, "message": "告警不存在", "data": None}
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    alert.status = "acknowledged"
    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = now_str
    await db.commit()
    await db.refresh(alert)
    return {"code": 200, "message": "告警已确认", "data": {"id": alert.id, "status": alert.status}}


@router.post("/{alert_id}/handle")
async def handle_alert(
    alert_id: str,
    handle_remark: str = Query(""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """处理告警"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"code": 404, "message": "告警不存在", "data": None}
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    alert.status = "handled"
    alert.handled_by = current_user.id
    alert.handled_at = now_str
    if handle_remark:
        existing = alert.description or ""
        alert.description = existing + f"\n[处理备注] {handle_remark}"
    await db.commit()
    await db.refresh(alert)
    return {"code": 200, "message": "告警已处理", "data": {"id": alert.id, "status": alert.status}}


@router.post("/{alert_id}/close")
async def close_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """关闭告警"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"code": 404, "message": "告警不存在", "data": None}
    alert.status = "closed"
    await db.commit()
    await db.refresh(alert)
    return {"code": 200, "message": "告警已关闭", "data": {"id": alert.id, "status": alert.status}}
