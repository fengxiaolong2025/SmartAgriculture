from typing import List

from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.user import User

# 角色层级：数值越大权限越高
ROLE_HIERARCHY = {
    "super_admin": 100,
    "admin": 80,
    "operator": 50,
    "viewer": 10,
}


def require_role(*roles: str):
    """
    RBAC 权限检查依赖。
    使用方式: @router.get("/admin-only", dependencies=[Depends(require_role("admin", "super_admin"))])
    或作为 FastAPI 的 Security 依赖。
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 403, "message": f"Requires one of roles: {roles}", "data": None},
            )
        return current_user

    return role_checker


def require_min_role(min_role: str):
    """
    基于角色层级的最低权限检查。
    min_role: 最低要求的角色名。
    """
    min_level = ROLE_HIERARCHY.get(min_role, 0)

    async def role_checker(current_user: User = Depends(get_current_user)):
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)
        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 403, "message": f"Requires at least {min_role} role", "data": None},
            )
        return current_user

    return role_checker
