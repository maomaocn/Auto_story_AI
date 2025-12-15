from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.taskLog import TaskLog
from app.schemas.task_log import TaskLogCreate, TaskLogBatchCreate

class CRUDTaskLog(CRUDBase[TaskLog, TaskLogCreate, dict]):
    async def get_by_episode(
        self, 
        db: AsyncSession, 
        *, 
        episode_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskLog]:
        """获取剧集的所有任务日志"""
        result = await db.execute(
            select(TaskLog)
            .where(TaskLog.episode_id == episode_id)
            .order_by(desc(TaskLog.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_latest_by_type(
        self,
        db: AsyncSession,
        *,
        episode_id: int,
        task_type: str
    ) -> Optional[TaskLog]:
        """获取指定任务类型的最新日志"""
        result = await db.execute(
            select(TaskLog)
            .where(
                TaskLog.episode_id == episode_id,
                TaskLog.task_type == task_type
            )
            .order_by(desc(TaskLog.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def create_batch(
        self,
        db: AsyncSession,
        *,
        batch_create: TaskLogBatchCreate
    ) -> List[TaskLog]:
        """批量创建任务日志"""
        logs = []
        for log_data in batch_create.logs:
            log_data_dict = log_data.model_dump(exclude_unset=True)
            log_data_dict["episode_id"] = batch_create.episode_id
            db_log = TaskLog(**log_data_dict)
            db.add(db_log)
            logs.append(db_log)
        
        await db.commit()
        
        # 刷新所有对象以获取生成的ID
        for log in logs:
            await db.refresh(log)
        
        return logs
    
    async def get_task_statistics(
        self,
        db: AsyncSession,
        *,
        episode_id: int
    ) -> dict:
        """获取任务统计信息"""
        from sqlalchemy import func
        
        result = await db.execute(
            select(
                TaskLog.task_type,
                func.count(TaskLog.id).label("total"),
                func.sum(
                    func.case(
                        (TaskLog.status == "completed", 1),
                        else_=0
                    )
                ).label("completed"),
                func.avg(TaskLog.execution_time).label("avg_time")
            )
            .where(TaskLog.episode_id == episode_id)
            .group_by(TaskLog.task_type)
        )
        
        stats = {}
        for row in result.all():
            stats[row.task_type] = {
                "total": row.total,
                "completed": row.completed or 0,
                "avg_time": row.avg_time or 0
            }
        
        return stats

task_log = CRUDTaskLog(TaskLog)