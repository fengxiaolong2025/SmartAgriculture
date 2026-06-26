import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from app.dependencies import get_db
from app.models import SensorData
from datetime import datetime

router = APIRouter(prefix="/data-ingest", tags=["数据采集"])


class SensorDataPoint(BaseModel):
    device_id: str
    metric_name: str
    value: float
    unit: str = ""
    time: Optional[str] = None
    plot_id: Optional[str] = None


class BatchIngestRequest(BaseModel):
    data: List[SensorDataPoint]


@router.post("/single")
async def ingest_single(data: SensorDataPoint, db: AsyncSession = Depends(get_db)):
    """单条数据上报"""
    if not data.time:
        data.time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    record = SensorData(
        id=uuid.uuid4().hex,
        device_id=data.device_id,
        metric_name=data.metric_name,
        value=data.value,
        unit=data.unit,
        time=data.time,
        plot_id=data.plot_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "code": 200,
        "message": "数据已接收",
        "data": {
            "id": record.id,
            "device_id": record.device_id,
            "metric_name": record.metric_name,
            "value": record.value,
            "time": record.time,
        }
    }


@router.post("/batch")
async def ingest_batch(payload: BatchIngestRequest, db: AsyncSession = Depends(get_db)):
    """批量数据上报"""
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    records = []
    for item in payload.data:
        record = SensorData(
            id=uuid.uuid4().hex,
            device_id=item.device_id,
            metric_name=item.metric_name,
            value=item.value,
            unit=item.unit,
            time=item.time or now_str,
            plot_id=item.plot_id,
        )
        records.append(record)

    db.add_all(records)
    await db.commit()

    return {
        "code": 200,
        "message": f"已接收 {len(records)} 条数据",
        "data": {"count": len(records)}
    }
