import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import time

from app.crud import episode as crud_episode, task_log as crud_task_log
from app.schemas.episode import EpisodeStatusUpdate
from app.schemas.task_log import TaskLogCreate
from app.services.pipeline_service import VideoPipeline

async def process_video_generation(
    db: AsyncSession,
    episode_id: int,
    regenerate: bool = False
) -> None:
    """
    处理视频生成的异步任务
    """
    start_time = time.time()
    
    try:
        # 创建pipeline实例
        pipeline = VideoPipeline(db, episode_id)
        
        # 运行pipeline
        success = await pipeline.run()
        
        execution_time = int((time.time() - start_time) * 1000)  # 毫秒
        
        if success:
            # 记录成功日志
            success_log = TaskLogCreate(
                episode_id=episode_id,
                task_type="pipeline_completed",
                status="completed",
                message="Video generation completed successfully",
                details={
                    "execution_time_ms": execution_time,
                    "regenerate": regenerate
                },
                execution_time=execution_time
            )
        else:
            # 记录失败日志
            error_log = TaskLogCreate(
                episode_id=episode_id,
                task_type="pipeline_failed",
                status="failed",
                message="Video generation failed",
                details={
                    "execution_time_ms": execution_time,
                    "regenerate": regenerate
                },
                execution_time=execution_time
            )
            await crud_task_log.create(db=db, obj_in=error_log)
    
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        
        # 记录异常日志
        error_log = TaskLogCreate(
            episode_id=episode_id,
            task_type="pipeline_error",
            status="failed",
            message=f"Unexpected error: {str(e)}",
            details={
                "execution_time_ms": execution_time,
                "regenerate": regenerate,
                "error_type": type(e).__name__
            },
            execution_time=execution_time
        )
        await crud_task_log.create(db=db, obj_in=error_log)
        
        # 更新剧集状态为失败
        await crud_episode.update_status(
            db=db,
            episode_id=episode_id,
            status_update=EpisodeStatusUpdate(
                status="failed",
                progress=0,
                message=f"Generation failed: {str(e)}"
            )
        )