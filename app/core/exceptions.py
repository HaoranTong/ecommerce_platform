"""
核心异常定义 —— 业务层服务异常基类
"""
from fastapi import HTTPException, status


class ServiceException(HTTPException):
    """业务服务异常，包含 HTTP 状态码与错误详情"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)
