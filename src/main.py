from fastapi import FastAPI
from src.adapters.api.routers import plants, devices
from alembic.config import Config
from alembic import command
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
def run_migrations():
    """Run Alembic migrations automatically on startup"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run Alembic migrations automatically on startup
    try:
        run_migrations()
        print("✅ Database migrations completed successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise e  # Fail startup if migrations fail
    yield

app = FastAPI(
    title="Rootly User Plant Management Service",
    description="Service for managing user plants, physical devices, and their associations.",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:3000,http://localhost:8080,http://localhost:8000,http://localhost:8001,http://localhost:8002,http://localhost:8003,*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plants.router)
app.include_router(plants.user_router)
app.include_router(devices.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
