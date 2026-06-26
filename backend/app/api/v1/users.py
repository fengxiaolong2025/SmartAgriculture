import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.dependencies import get_db, get_current_user
from app.models import User
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """用户列表"""
    conditions = [User.is_deleted == False]
    if role:
        conditions.append(User.role == role)

    count_query = select(func.count(User.id)).where(*conditions)
    result = await db.execute(count_query)
    total = result.scalar() or 0

    result = await db.execute(
        select(User).where(*conditions).order_by(desc(User.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    )
    users = result.scalars().all()

    items = []
    for u in users:
        items.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "phone": u.phone,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "last_login_at": str(u.last_login_at) if u.last_login_at else None,
            "created_at": str(u.created_at) if u.created_at else None,
        })

    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    }


@router.post("/")
async def create_user(
    username: str = Query(...),
    password: str = Query(...),
    email: str = Query(None),
    phone: str = Query(None),
    full_name: str = Query(None),
    role: str = Query("viewer"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建用户"""
    result = await db.execute(
        select(User).where(User.username == username, User.is_deleted == False)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {"code": 400, "message": "用户名已存在", "data": None}

    user = User(
        id=uuid.uuid4().hex,
        username=username,
        hashed_password=hash_password(password),
        email=email,
        phone=phone,
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "code": 200,
        "message": "用户已创建",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "full_name": user.full_name,
            "role": user.role,
        }
    }


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """用户详情"""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        return {"code": 404, "message": "用户不存在", "data": None}

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "last_login_at": str(user.last_login_at) if user.last_login_at else None,
            "created_at": str(user.created_at) if user.created_at else None,
            "updated_at": str(user.updated_at) if user.updated_at else None,
        }
    }


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    email: str = Query(None),
    phone: str = Query(None),
    full_name: str = Query(None),
    role: str = Query(None),
    is_active: bool = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新用户"""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        return {"code": 404, "message": "用户不存在", "data": None}

    updates = {"email": email, "phone": phone, "full_name": full_name, "role": role, "is_active": is_active}
    for key, value in updates.items():
        if value is not None:
            setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return {
        "code": 200,
        "message": "用户已更新",
        "data": {"id": user.id, "username": user.username}
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除用户（软删除）"""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        return {"code": 404, "message": "用户不存在", "data": None}

    user.is_deleted = True
    await db.commit()
    return {"code": 200, "message": "用户已删除", "data": None}


@router.put("/{user_id}/password")
async def change_password(
    user_id: str,
    old_password: str = Query(...),
    new_password: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修改密码"""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        return {"code": 404, "message": "用户不存在", "data": None}

    from app.core.security import verify_password
    if not verify_password(old_password, user.hashed_password):
        return {"code": 400, "message": "原密码错误", "data": None}

    user.hashed_password = hash_password(new_password)
    await db.commit()

    return {"code": 200, "message": "密码已修改", "data": None}
