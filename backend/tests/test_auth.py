from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_db
from src import models, auth

@pytest.fixture(scope="function")
def engine():
    """为每个测试创建一个新的数据库引擎"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    return engine

@pytest.fixture(scope="function")
def session_factory(engine):
    """为每个测试创建一个新的会话工厂"""
    Base.metadata.create_all(bind=engine)
    yield sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def override_get_db(session_factory):
    """为每个测试创建一个新的数据库会话"""
    def _override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()
    return _override_get_db

@pytest.fixture(scope="function")
def client(override_get_db):
    """为每个测试创建一个新的测试客户端"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_register_user(client):
    """测试用户注册"""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data

def test_register_duplicate_username(client):
    """测试注册重复用户名"""
    # 先注册一个用户
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    # 尝试注册相同用户名
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "anotherpassword"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success(client):
    """测试登录成功"""
    # 先注册用户
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    # 登录
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword",
            "grant_type": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    """测试密码错误"""
    # 先注册用户
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    # 使用错误密码登录
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword",
            "grant_type": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_nonexistent_user(client):
    """测试登录不存在的用户"""
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent",
            "password": "testpassword",
            "grant_type": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"] 