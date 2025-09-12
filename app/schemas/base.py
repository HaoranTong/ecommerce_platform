"""
文件名：base.py
文件路径：app/schemas/base.py
功能描述：Pydantic基础模式和公共响应模型定义
主要功能：
- 公共基础模式类
- 标准API响应格式
- 通用分页和排序模式
使用说明：
- 导入：from app.schemas.base import BaseSchema, PaginationParams
- 继承：class YourSchema(BaseSchema)
依赖模块：
- pydantic: 数据验证和序列化
- typing: 类型注解支持
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class BaseSchema(BaseModel):
    """基础模式类"""
    class Config:
        from_attributes = True
        # 允许使用ORM模式
        arbitrary_types_allowed = True


class TimestampSchema(BaseSchema):
    """包含时间戳的基础模式"""
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """分页参数模式"""
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(100, ge=1, le=500, description="每页记录数")


class SortParams(BaseModel):
    """排序参数模式"""
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: Optional[str] = Field("desc", regex="^(asc|desc)$", description="排序方向")


class ApiResponse(BaseSchema):
    """标准API响应格式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class PaginatedResponse(ApiResponse):
    """分页响应格式"""
    data: List[Any]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseSchema):
    """错误响应格式"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None