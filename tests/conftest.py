import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from sqlalchemy import text
from app.database import engine


# Usamos SQLite en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def seed_data(db_session):
    # Limpia tablas y vuelve a aplicar seed
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM user_microcontrollers"))
        conn.execute(text("DELETE FROM microcontrollers"))
        conn.execute(text("DELETE FROM plants"))
    # Reejecuta upgrade de Alembic seed
    from alembic.command import upgrade
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    upgrade(alembic_cfg, "head")
    yield

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# Sobrescribimos la dependencia get_db de FastAPI
app.dependency_overrides[get_db] = lambda: TestingSessionLocal()

@pytest.fixture
def client():
    return TestClient(app)

# Fixture para usuario simulado en auth
@pytest.fixture
def token_user_owner(monkeypatch):
    def fake_current_user():
        return {"user_id": "user-1", "roles": []}
    from app import auth
    monkeypatch.setattr(auth, "get_current_user", lambda: {"user_id": "user-1", "roles": []})
    return {"Authorization": "Bearer faketoken"}
