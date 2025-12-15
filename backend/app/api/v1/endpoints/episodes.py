from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import episode as crud_episode, task_log as crud_task_log
from app.schemas.episode import (
    EpisodeCreate,
    EpisodeUpdate,
    EpisodeRead,
    EpisodeSimple,
    EpisodeStatusUpdate,
    EpisodeGenerateRequest,
)
from app.schemas.task_log import TaskLogCreate
from app.services.pipeline_service import VideoPipeline

router = APIRouter(prefix="/episodes", tags=["episodes"])

@router.post("/", response_model=EpisodeRead, status_code=status.HTTP_201_CREATED)
async def create_episode(
    *,
    db: AsyncSession = Depends(get_db),
    episode_in: EpisodeCreate,
):
    """
    创建新剧集
    """
    # 检查剧集序号是否已存在
    existing_episodes = await crud_episode.get_by_project(
        db=db, project_id=episode_in.project_id
    )
    
    for existing in existing_episodes:
        if existing.episode_number == episode_in.episode_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Episode number {episode_in.episode_number} already exists for this project"
            )
    
    episode = await crud_episode.create(db=db, obj_in=episode_in)
    
    # 创建初始任务日志
    initial_log = TaskLogCreate(
        episode_id=episode.id,
        task_type="episode_created",
        status="completed",
        message="Episode created successfully"
    )
    await crud_task_log.create(db=db, obj_in=initial_log)
    
    # 获取完整的剧集信息（包含日志）
    return await crud_episode.get_with_logs(db=db, id=episode.id)

@router.get("/", response_model=List[EpisodeSimple])
async def read_episodes(
    db: AsyncSession = Depends(get_db),
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    获取剧集列表（支持筛选）
    """
    episodes = await crud_episode.search(
        db=db,
        project_id=project_id,
        status=status,
        title=title,
        skip=skip,
        limit=limit
    )
    return episodes

@router.get("/{episode_id}", response_model=EpisodeRead)
async def read_episode(
    *,
    db: AsyncSession = Depends(get_db),
    episode_id: int,
):
    """
    根据ID获取剧集详情（包含任务日志）
    """
    episode = await crud_episode.get_with_logs(db=db, id=episode_id)
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    return episode

@router.put("/{episode_id}", response_model=EpisodeRead)
async def update_episode(
    *,
    db: AsyncSession = Depends(get_db),
    episode_id: int,
    episode_in: EpisodeUpdate,
):
    """
    更新剧集信息
    """
    episode = await crud_episode.get(db=db, id=episode_id)
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    episode = await crud_episode.update(
        db=db, db_obj=episode, obj_in=episode_in
    )
    
    # 记录更新日志
    update_log = TaskLogCreate(
        episode_id=episode.id,
        task_type="episode_updated",
        status="completed",
        message="Episode information updated"
    )
    await crud_task_log.create(db=db, obj_in=update_log)
    
    return await crud_episode.get_with_logs(db=db, id=episode.id)

@router.patch("/{episode_id}/status", response_model=EpisodeRead)
async def update_episode_status(
    *,
    db: AsyncSession = Depends(get_db),
    episode_id: int,
    status_update: EpisodeStatusUpdate,
):
    """
    更新剧集状态
    """
    episode = await crud_episode.update_status(
        db=db, episode_id=episode_id, status_update=status_update
    )
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    # 记录状态变更日志
    status_log = TaskLogCreate(
        episode_id=episode.id,
        task_type="status_update",
        status="completed",
        message=f"Episode status updated to {status_update.status}"
    )
    await crud_task_log.create(db=db, obj_in=status_log)
    
    return await crud_episode.get_with_logs(db=db, id=episode.id)

@router.post("/{episode_id}/generate", response_model=EpisodeRead)
async def generate_video(
    *,
    db: AsyncSession = Depends(get_db),
    episode_id: int,
    background_tasks: BackgroundTasks,
    generate_request: EpisodeGenerateRequest = None,
):
    """
    开始生成视频
    """
    if generate_request is None:
        generate_request = EpisodeGenerateRequest()
    
    episode = await crud_episode.get(db=db, id=episode_id)
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    # 如果已经完成且不要求重新生成
    if episode.is_completed and not generate_request.regenerate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Episode already completed. Use regenerate=True to regenerate."
        )
    
    # 如果正在处理中
    if episode.is_processing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Episode is already being processed"
        )
    
    # 更新状态为开始生成脚本
    await crud_episode.update_status(
        db=db,
        episode_id=episode_id,
        status_update=EpisodeStatusUpdate(
            status="generating_script",
            progress=0,
            message="Starting video generation pipeline"
        )
    )
    
    # 记录开始日志
    start_log = TaskLogCreate(
        episode_id=episode_id,
        task_type="pipeline_started",
        status="processing",
        message="Video generation pipeline started"
    )
    await crud_task_log.create(db=db, obj_in=start_log)
    
    # 启动后台任务
    from app.services.task_service import process_video_generation
    background_tasks.add_task(process_video_generation, db, episode_id, generate_request.regenerate)
    
    # 返回当前状态
    return await crud_episode.get_with_logs(db=db, id=episode_id)

@router.get("/project/{project_id}", response_model=List[EpisodeRead])
async def read_episodes_by_project(
    *,
    db: AsyncSession = Depends(get_db),
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    获取项目的所有剧集
    """
    episodes = await crud_episode.get_by_project(
        db=db, project_id=project_id, skip=skip, limit=limit
    )
    return episodes