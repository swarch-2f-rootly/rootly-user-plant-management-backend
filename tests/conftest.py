import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Global variables for lazy initialization
_engine = None
_SessionLocal = None

def get_test_engine():
    """Lazy initialization of database engine and session factory."""
    global _engine, _SessionLocal
    if _engine is None:
        TEST_DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://admin:admin123@db-user-plant-management-test:5432/user_plant_management_test_db"
        )
        # Debug output (hide password)
        safe_url = TEST_DATABASE_URL.split('@')[1] if '@' in TEST_DATABASE_URL else TEST_DATABASE_URL
        print(f"[TEST CONFIG] Connecting to database: {safe_url}")
        
        _engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=None)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine, class_=AsyncSession)
    
    return _engine, _SessionLocal

async def override_get_session():
    """Override for FastAPI dependency injection."""
    _, SessionLocal = get_test_engine()
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest.fixture(scope="session")
async def test_db():
    """Session-scoped fixture to set up and tear down test database."""
    engine, _ = get_test_engine()
    
    # Tables should already be created by alembic migrations
    # Just verify connection and cleanup at the end
    print("[TEST] Database fixture initialized")
    
    yield
    
    # Cleanup
    print("[TEST] Cleaning up test database")
    try:
        from src.adapters.repositories.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception as e:
        print(f"[TEST CLEANUP] Warning: Could not cleanup tables: {e}")
    finally:
        await engine.dispose()

@pytest.fixture(scope="function")
async def client(test_db):
    """Function-scoped fixture to create test client for each test."""
    from src.main import app
    from src.config.database import get_session
    from httpx import ASGITransport
    
    # Override the database session dependency
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    # Clean up overrides after test
    app.dependency_overrides.clear()
