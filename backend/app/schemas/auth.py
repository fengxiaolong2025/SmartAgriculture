from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求。"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """刷新令牌请求。"""
    refresh_token: str = Field(...)


class TokenResponse(BaseModel):
    """令牌响应。"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
