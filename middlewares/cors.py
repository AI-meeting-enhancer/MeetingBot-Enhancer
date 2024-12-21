from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

origins = os.getenv("CORS", "").split(",")
print("cors:", origins)

def apply_cors_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app