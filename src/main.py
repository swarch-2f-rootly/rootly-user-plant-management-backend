# Punto de entrada principal para FastAPI

from fastapi import FastAPI
from src.adapters.handlers.device_handler import router as device_router

app = FastAPI(
    title="rootly User Plant Management",
    description="Microservice for managing users, plants, and microcontrollers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(device_router, prefix="/api/user/devices", tags=["devices"])
