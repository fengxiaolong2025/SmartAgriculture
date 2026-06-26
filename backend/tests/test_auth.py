"""
认证 API 测试。
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_db):
    """测试登录成功。"""
    from app.core.security import hash_password
    from app.models.user import User

    # 创建测试用户
    user = User(
        username="testlogin",
        hashed_password=hash_password("Test@123"),
        role="operator",
    )
    test_db.add(user)
    await test_db.commit()

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "testlogin", "password": "Test@123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["user"]["username"] == "testlogin"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient, test_db):
    """测试登录密码错误。"""
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        username="testwrong",
        hashed_password=hash_password("Test@123"),
        role="viewer",
    )
    test_db.add(user)
    await test_db.commit()

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "testwrong", "password": "WrongPassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == 401


@pytest.mark.asyncio
async def test_login_user_not_found(async_client: AsyncClient):
    """测试登录用户不存在。"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "Test@123"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(async_client: AsyncClient, test_db):
    """测试刷新 token。"""
    from app.core.security import hash_password, create_refresh_token
    from app.models.user import User

    user = User(
        username="testrefresh",
        hashed_password=hash_password("Test@123"),
        role="viewer",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    refresh_token = create_refresh_token({"sub": user.id, "username": user.username, "role": user.role})

    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient):
    """测试未授权访问。"""
    response = await async_client.get("/api/v1/auth/me")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == 401


@pytest.mark.asyncio
async def test_get_me_with_token(async_client: AsyncClient, auth_headers: dict):
    """测试带 token 获取当前用户信息。"""
    response = await async_client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "testuser"
    assert data["data"]["role"] == "super_admin"


@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient, auth_headers: dict):
    """测试登出。"""
    response = await async_client.post("/api/v1/auth/logout", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
