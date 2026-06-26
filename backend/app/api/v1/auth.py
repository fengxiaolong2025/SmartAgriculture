from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=dict)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户名密码登录，返回 access_token 和 refresh_token。"""
    result = await db.execute(
        select(User).where(User.username == request.username, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "message": "用户名或密码错误", "data": None},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "message": "账户已被禁用", "data": None},
        )

    # 更新最后登录时间
    user.last_login_at = datetime.now()
    await db.flush()

    token_data = {"sub": user.id, "username": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "full_name": user.full_name,
            },
        },
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(request: RefreshRequest):
    """使用 refresh_token 刷新 access_token。"""
    payload = decode_token(request.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 401, "message": "Invalid or expired refresh token", "data": None},
        )

    user_id = payload.get("sub")
    token_data = {
        "sub": user_id,
        "username": payload.get("username"),
        "role": payload.get("role"),
    }
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        },
    }


@router.post("/logout", response_model=dict)
async def logout(current_user: User = Depends(get_current_user)):
    """登出（客户端需要清除本地 token）。"""
    return {
        "code": 200,
        "message": "Logged out successfully",
        "data": None,
    }


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息。"""
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "phone": current_user.phone,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "last_login_at": str(current_user.last_login_at) if current_user.last_login_at else None,
            "created_at": str(current_user.created_at) if current_user.created_at else None,
        },
    }
