from fastapi import FastAPI
from fastapi.responses import JSONResponse
from middlewares.cors import apply_cors_middleware
from auth.router import router as auth_router  
from routers import api_router

def create_app()-> FastAPI:
    app = FastAPI()
    
    # Middlewares
    app = apply_cors_middleware(app)
    
    # Configuring routers
    app.include_router(api_router)
    app.include_router(auth_router)
    return app