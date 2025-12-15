from fastapi import APIRouter
from app.api.v1.endpoints import projects, episodes, logs

api_router = APIRouter()
api_router.include_router(projects.router)
api_router.include_router(episodes.router)
api_router.include_router(logs.router)