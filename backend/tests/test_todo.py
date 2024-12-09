from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_db

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers(client):
    """创建测试用户并返回认证头"""
    # 注册用户
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    # 登录获取token
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_todo_authenticated(client, auth_headers):
    """测试已认证用户创建待办事项"""
    response = client.post(
        "/todos/",
        json={"title": "买牛奶", "completed": False},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "买牛奶"
    assert data["completed"] == False
    assert "owner_id" in data

def test_create_todo_unauthenticated(client):
    """测试未认证用户创建待办事项"""
    response = client.post(
        "/todos/",
        json={"title": "买牛奶", "completed": False}
    )
    assert response.status_code == 401

def test_create_todo(client, auth_headers):
    """测试创建待办事项"""
    response = client.post(
        "/todos/",
        json={"title": "买牛奶", "completed": False},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "买牛奶"
    assert data["completed"] == False
    assert "id" in data

def test_get_todo(client, auth_headers):
    """测试获取单个待办事项"""
    # 先创建一个待办事项
    create_response = client.post(
        "/todos/",
        json={"title": "买牛奶", "completed": False},
        headers=auth_headers
    )
    todo_id = create_response.json()["id"]
    
    # 获取该待办事项
    response = client.get(f"/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "买牛奶"
    assert data["completed"] == False

def test_get_todo_not_found(client, auth_headers):
    """测试获取不存在的待办事项"""
    response = client.get("/todos/999", headers=auth_headers)
    assert response.status_code == 404

def test_get_all_todos(client, auth_headers):
    """测试获取所有待办事项"""
    # 创建两个待办事项
    client.post(
        "/todos/",
        json={"title": "买牛奶", "completed": False},
        headers=auth_headers
    )
    client.post(
        "/todos/",
        json={"title": "买面包", "completed": True},
        headers=auth_headers
    )
    
    # 获取列表
    response = client.get("/todos/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["owner_id"] for item in data)

def test_update_todo(client, auth_headers):
    """测试更新待办事项"""
    # 先创建一个待办事项
    create_response = client.post(
        "/todos/",
        json={"title": "买牛奶", "completed": False},
        headers=auth_headers
    )
    todo_id = create_response.json()["id"]
    
    # 更新待办事项
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "买全脂牛奶", "completed": True},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "买全脂牛奶"
    assert data["completed"] == True

def test_update_todo_not_found(client, auth_headers):
    """测试更新不存在的待办事项"""
    response = client.put(
        "/todos/999",
        json={"title": "不存在", "completed": True},
        headers=auth_headers
    )
    assert response.status_code == 404

def test_delete_todo(client, auth_headers):
    """测试删除待办事项"""
    # 先创建一个待办事项
    create_response = client.post(
        "/todos/",
        json={"title": "买牛奶", "completed": False},
        headers=auth_headers
    )
    todo_id = create_response.json()["id"]
    
    # 删除待办事项
    response = client.delete(f"/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # 确认已被删除
    response = client.get(f"/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 404

def test_delete_todo_not_found(client, auth_headers):
    """测试删除不存在的待办事项"""
    response = client.delete("/todos/999", headers=auth_headers)
    assert response.status_code == 404
