from fastapi import APIRouter

from app.api.v1.endpoints import tasks

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(tasks.router)