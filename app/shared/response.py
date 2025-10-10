"""
文件名：response.py
文件路径：app/shared/response.py
功能描述：统一API响应格式定义
主要功能：
- ApiResponse: 标准API响应模型
- success_response(): 成功响应包装函数
- error_response(): 错误响应包装函数
使用说明：
- 导入：from app.shared.response import success_response, ApiResponse
- 成功：return success_response(data=cart, message="操作成功")
- 错误：raise业务异常，由异常处理器自动包装
依赖模块：
- pydantic: 数据验证框架
- typing: 类型提示支持
创建时间：2025-10-10
设计决策：实施统一响应格式，提升API一致性
"""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

# 泛型类型变量，用于响应数据类型约束
T = TypeVar("T")


class ErrorDetail(BaseModel):
    """错误详情模型"""

    code: str = Field(..., description="业务错误码")
    message: str = Field(..., description="错误描述信息")
    details: Optional[dict] = Field(None, description="错误详细信息")


class ApiResponse(BaseModel, Generic[T]):
    """
    统一API响应格式

    遵循RESTful API设计最佳实践，提供一致的响应结构。

    Attributes:
        success: 操作是否成功
        data: 响应数据（泛型），成功时必填
        error: 错误信息，失败时必填
        message: 提示消息
        timestamp: 响应时间戳（ISO 8601格式）
        request_id: 请求追踪ID，用于日志关联

    Examples:
        成功响应：
        ```json
        {
            "success": true,
            "data": {"cart_id": 123, ...},
            "message": "操作成功",
            "timestamp": "2025-10-10T10:00:00Z",
            "request_id": "req_abc123"
        }
        ```

        错误响应：
        ```json
        {
            "success": false,
            "error": {
                "code": "CART_002",
                "message": "商品库存不足",
                "details": {"sku_id": 12345}
            },
            "message": "操作失败",
            "timestamp": "2025-10-10T10:00:00Z",
            "request_id": "req_abc123"
        }
        ```
    """

    success: bool = Field(..., description="操作是否成功")
    data: Optional[T] = Field(None, description="响应数据，成功时包含")
    error: Optional[ErrorDetail] = Field(None, description="错误信息，失败时包含")
    message: str = Field(default="", description="提示消息")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="响应时间戳（ISO 8601格式）",
    )
    request_id: str = Field(
        default_factory=lambda: f"req_{uuid4().hex[:12]}",
        description="请求追踪ID",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "data": {"cart_id": 123, "total_items": 3},
                    "message": "操作成功",
                    "timestamp": "2025-10-10T10:00:00Z",
                    "request_id": "req_abc123def456",
                }
            ]
        }
    }


def success_response(
    data: Any,
    message: str = "操作成功",
    request_id: Optional[str] = None,
) -> ApiResponse:
    """
    创建成功响应

    Args:
        data: 响应数据，可以是任何可序列化对象
        message: 成功提示消息，默认"操作成功"
        request_id: 可选的请求ID，未提供时自动生成

    Returns:
        ApiResponse: 标准成功响应对象

    Example:
        ```python
        cart = await service.get_cart(user_id)
        return success_response(
            data=cart,
            message="获取购物车成功"
        )
        ```
    """
    response = ApiResponse(
        success=True,
        data=data,
        message=message,
    )

    if request_id:
        response.request_id = request_id

    return response


def error_response(
    code: str,
    message: str,
    details: Optional[dict] = None,
    request_id: Optional[str] = None,
) -> ApiResponse:
    """
    创建错误响应

    Args:
        code: 业务错误码（如CART_001）
        message: 错误描述信息
        details: 错误详细信息字典
        request_id: 可选的请求ID，未提供时自动生成

    Returns:
        ApiResponse: 标准错误响应对象

    Example:
        ```python
        return error_response(
            code="CART_002",
            message="商品库存不足",
            details={"sku_id": 12345, "available": 5}
        )
        ```
    """
    response = ApiResponse(
        success=False,
        error=ErrorDetail(code=code, message=message, details=details),
        message="操作失败",
    )

    if request_id:
        response.request_id = request_id

    return response
