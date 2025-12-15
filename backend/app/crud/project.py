from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.project import Project
from app.models.episode import Episode, EpisodeStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectStats

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    async def get_with_episodes(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[Project]:
        """获取项目及其所有剧集"""
        result = await db.execute(
            select(Project)
            .options(selectinload(Project.episodes))
            .where(Project.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi_with_stats(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Project]:
        """获取项目列表（包含基本统计）"""
        result = await db.execute(
            select(Project)
            .offset(skip)
            .limit(limit)
            .order_by(Project.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_stats(self, db: AsyncSession, *, project_id: int) -> ProjectStats:
        """获取项目统计信息"""
        # 统计各种状态的剧集数量
        status_counts = await db.execute(
            select(Episode.status, func.count(Episode.id))
            .where(Episode.project_id == project_id)
            .group_by(Episode.status)
        )
        status_counts_dict = dict(status_counts.all())
        
        # 计算总视频时长
        total_duration = await db.execute(
            select(func.sum(Episode.video_duration))
            .where(
                Episode.project_id == project_id,
                Episode.video_duration.isnot(None)
            )
        )
        
        return ProjectStats(
            total_episodes=sum(status_counts_dict.values()),
            completed_episodes=status_counts_dict.get(EpisodeStatus.COMPLETED.value, 0),
            processing_episodes=sum(
                status_counts_dict.get(status.value, 0) 
                for status in [
                    EpisodeStatus.GENERATING_SCRIPT,
                    EpisodeStatus.GENERATING_IMAGES,
                    EpisodeStatus.GENERATING_AUDIO,
                    EpisodeStatus.ADDING_SUBTITLES,
                    EpisodeStatus.COMPOSING_VIDEO
                ]
            ),
            failed_episodes=status_counts_dict.get(EpisodeStatus.FAILED.value, 0),
            total_video_duration=total_duration.scalar()
        )
    
    async def update_status(
        self, 
        db: AsyncSession, 
        *, 
        project_id: int, 
        status: str
    ) -> Optional[Project]:
        """更新项目状态"""
        project = await self.get(db, id=project_id)
        if project:
            project.status = status
            db.add(project)
            await db.commit()
            await db.refresh(project)
        return project

project = CRUDProject(Project)