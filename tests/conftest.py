import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.config.database import get_session
from src.adapters.repositories.models import Base
import os

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:admin123@postgres-user-plant:5432/rootly"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=None)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_session():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="session")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def client(test_db):
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
