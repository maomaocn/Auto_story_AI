from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import project as crud_project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectSimple,
    ProjectStats,
)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    *,
    db: AsyncSession = Depends(get_db),
    project_in: ProjectCreate,
):
    """
    创建新项目
    """
    # 检查项目名是否已存在
    # 这里可以添加重复检查逻辑
    
    project = await crud_project.create(db=db, obj_in=project_in)
    return project

@router.get("/", response_model=List[ProjectSimple])
async def read_projects(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    获取项目列表
    """
    projects = await crud_project.get_multi_with_stats(
        db=db, skip=skip, limit=limit
    )
    return projects

@router.get("/{project_id}", response_model=ProjectRead)
async def read_project(
    *,
    db: AsyncSession = Depends(get_db),
    project_id: int,
):
    """
    根据ID获取项目详情（包含剧集）
    """
    project = await crud_project.get_with_episodes(db=db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    *,
    db: AsyncSession = Depends(get_db),
    project_id: int,
    project_in: ProjectUpdate,
):
    """
    更新项目信息
    """
    project = await crud_project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = await crud_project.update(
        db=db, db_obj=project, obj_in=project_in
    )
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    *,
    db: AsyncSession = Depends(get_db),
    project_id: int,
):
    """
    删除项目（级联删除所有相关剧集）
    """
    project = await crud_project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await crud_project.remove(db=db, id=project_id)
    return None

@router.get("/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(
    *,
    db: AsyncSession = Depends(get_db),
    project_id: int,
):
    """
    获取项目统计信息
    """
    project = await crud_project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    stats = await crud_project.get_stats(db=db, project_id=project_id)
    return stats