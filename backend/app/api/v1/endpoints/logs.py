from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import task_log as crud_task_log
from app.schemas.task_log import TaskLogRead, TaskLogCreate, TaskLogBatchCreate

router = APIRouter(prefix="/logs", tags=["task_logs"])

@router.get("/episode/{episode_id}", response_model=List[TaskLogRead])
async def read_episode_logs(
    *,
    db: AsyncSession = Depends(get_db),
    episode_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    获取剧集的任务日志
    """
    logs = await crud_task_log.get_by_episode(
        db=db, episode_id=episode_id, skip=skip, limit=limit
    )
    return logs

@router.post("/", response_model=TaskLogRead, status_code=status.HTTP_201_CREATED)
async def create_task_log(
    *,
    db: AsyncSession = Depends(get_db),
    log_in: TaskLogCreate,
):
    """
    创建任务日志
    """
    log = await crud_task_log.create(db=db, obj_in=log_in)
    return log

@router.post("/batch", response_model=List[TaskLogRead], status_code=status.HTTP_201_CREATED)
async def create_task_log_batch(
    *,
    db: AsyncSession = Depends(get_db),
    batch_in: TaskLogBatchCreate,
):
    """
    批量创建任务日志
    """
    logs = await crud_task_log.create_batch(db=db, batch_create=batch_in)
    return logs

@router.get("/episode/{episode_id}/statistics")
async def get_task_statistics(
    *,
    db: AsyncSession = Depends(get_db),
    episode_id: int,
):
    """
    获取任务统计信息
    """
    stats = await crud_task_log.get_task_statistics(db=db, episode_id=episode_id)
    return stats