from fastapi import APIRouter, Body

router = APIRouter(prefix = "/auth", tags = ["Auth"])

@router.post("/login", tags=["Auth"])
async def login():
    return {"message": "Login Successful"}


@router.post("/signup", tags=["Auth"])
async def signup(name:str):
    return {"message": f"Signup Successful, {name}"}