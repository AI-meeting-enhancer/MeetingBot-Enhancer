from fastapi import APIRouter
from .videos import router as video_router

api_router = APIRouter(prefix = "/api/v1")

api_router.include_router(video_router)