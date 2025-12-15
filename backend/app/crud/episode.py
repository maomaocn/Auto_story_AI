from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.episode import Episode, EpisodeStatus
from app.models.taskLog import TaskLog
from app.schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeStatusUpdate

class CRUDEpisode(CRUDBase[Episode, EpisodeCreate, EpisodeUpdate]):
    async def get_with_logs(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[Episode]:
        """获取剧集及其所有任务日志"""
        result = await db.execute(
            select(Episode)
            .options(selectinload(Episode.task_logs))
            .where(Episode.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_project(
        self, 
        db: AsyncSession, 
        *, 
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Episode]:
        """获取项目的所有剧集"""
        result = await db.execute(
            select(Episode)
            .options(selectinload(Episode.task_logs))
            .where(Episode.project_id == project_id)
            .order_by(Episode.episode_number.asc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_status(
        self,
        db: AsyncSession,
        *,
        episode_id: int,
        status_update: EpisodeStatusUpdate
    ) -> Optional[Episode]:
        """更新剧集状态和进度"""
        episode = await self.get(db, id=episode_id)
        if episode:
            episode.status = status_update.status
            if status_update.progress is not None:
                episode.progress = status_update.progress
            db.add(episode)
            await db.commit()
            await db.refresh(episode)
        return episode
    
    async def get_processing_episodes(
        self, 
        db: AsyncSession
    ) -> List[Episode]:
        """获取所有正在处理的剧集"""
        processing_statuses = [
            EpisodeStatus.GENERATING_SCRIPT,
            EpisodeStatus.GENERATING_IMAGES,
            EpisodeStatus.GENERATING_AUDIO,
            EpisodeStatus.ADDING_SUBTITLES,
            EpisodeStatus.COMPOSING_VIDEO
        ]
        
        result = await db.execute(
            select(Episode)
            .where(Episode.status.in_([status.value for status in processing_statuses]))
            .order_by(Episode.updated_at.asc())
        )
        return result.scalars().all()
    
    async def search(
        self,
        db: AsyncSession,
        *,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        title: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Episode]:
        """搜索剧集"""
        query = select(Episode)
        
        conditions = []
        if project_id:
            conditions.append(Episode.project_id == project_id)
        if status:
            conditions.append(Episode.status == status)
        if title:
            conditions.append(Episode.title.contains(title))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit).order_by(Episode.id.desc())
        result = await db.execute(query)
        return result.scalars().all()

episode = CRUDEpisode(Episode)