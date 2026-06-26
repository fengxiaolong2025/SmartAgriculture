"""
测试 fixtures 配置。
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.dependencies import get_db

# 测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_agri_mgmt.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """创建测试数据库会话。"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_client(test_db: AsyncSession):
    """创建异步 HTTP 测试客户端。"""
    from app.main import app

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_headers(async_client: AsyncClient, test_db: AsyncSession):
    """获取认证请求头（创建测试用户并登录）。"""
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        username="testuser",
        hashed_password=hash_password("Test@123"),
        role="super_admin",
        full_name="Test User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Test@123"},
    )
    data = response.json()
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
