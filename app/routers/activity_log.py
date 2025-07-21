from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..models.activity_log import ActivityLog as ActivityLogModel
from ..schemas.log import ActivityLog as ActivityLogSchema
from ..database import get_db

router = APIRouter(prefix="/logs/activity", tags=["Activity Logs"])

@router.get("/", response_model=List[ActivityLogSchema])
async def get_activity_logs(skip: int = 0, limit: int = 200, db: AsyncSession = Depends(get_db)):
    """Mengambil daftar log aktivitas, diurutkan dari yang terbaru."""
    query = select(ActivityLogModel).order_by(ActivityLogModel.id.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()