from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix = "/users",
    tags = ["users"],
)

@router.get("/")
async def get_videos():
    return {"message": "This is a test"}