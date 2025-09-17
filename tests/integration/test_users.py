import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.modules.user_auth.models import User

# use in-memory sqlite for fast tests
SQLITE_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def setup_module(module):
    # create tables
    Base.metadata.create_all(bind=engine)


def override_get_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# create tables before TestClient instantiation (avoid race with TestClient server)
Base.metadata.create_all(bind=engine)

app.dependency_overrides[get_db] = override_get_session
client = TestClient(app)


def test_create_and_list_user():
    r = client.post('/api/v1/user-auth/users', json={'username': 'testu', 'email': 'testu@example.com'})
    assert r.status_code == 201
    data = r.json()
    assert data['username'] == 'testu'
    r2 = client.get('/api/v1/user-auth/users')
    assert r2.status_code == 200
    users = r2.json()
    assert any(u['username'] == 'testu' for u in users)
