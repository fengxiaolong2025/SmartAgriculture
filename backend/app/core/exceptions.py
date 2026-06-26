from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    """应用基础异常。"""

    def __init__(self, message: str = "Internal server error", code: int = 500):
        self.message = message
        self.code = code


class NotFoundException(AppException):
    """资源未找到异常。"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, code=404)


class UnauthorizedException(AppException):
    """未授权异常。"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, code=401)


class ForbiddenException(AppException):
    """禁止访问异常。"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, code=403)


class BadRequestException(AppException):
    """请求参数错误异常。"""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, code=400)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"code": 422, "message": "Validation error", "data": {"errors": errors}},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": 500, "message": "Internal server error", "data": None},
    )
