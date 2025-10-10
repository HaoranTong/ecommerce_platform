"""
文件名：exceptions.py
文件路径：app/modules/shopping_cart/exceptions.py
功能描述：购物车模块自定义异常和错误码定义
主要功能：
- CartErrorCode: 错误码枚举
- CartException: 购物车业务异常基类
- 具体业务异常：库存不足、数量超限等
使用说明：
- 导入：from .exceptions import CartException, StockInsufficientError
- 抛出：raise StockInsufficientError(sku_id=12345, available=5)
- 捕获：except CartException as e: ...
依赖模块：
- fastapi.HTTPException: FastAPI标准异常
创建时间：2025-10-10
设计决策：标准化错误处理，提供精确的业务错误码
"""

from enum import Enum
from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class CartErrorCode(str, Enum):
    """
    购物车模块错误码枚举

    遵循文档定义的CART_001~CART_009错误码标准
    """

    # 请求参数错误
    INVALID_PARAMETER = "CART_001"  # 请求参数验证失败

    # 业务规则错误
    STOCK_INSUFFICIENT = "CART_002"  # 商品库存不足
    CART_LIMIT_EXCEEDED = "CART_003"  # 购物车商品数量超限

    # 资源不存在错误
    ITEM_NOT_FOUND = "CART_004"  # 购物车商品项不存在
    PRODUCT_NOT_FOUND = "CART_005"  # 商品不存在或已下架

    # 冲突错误
    ITEM_ALREADY_EXISTS = "CART_006"  # 商品已在购物车中

    # 频率限制
    TOO_MANY_REQUESTS = "CART_007"  # 操作过于频繁

    # 系统错误
    CACHE_ERROR = "CART_008"  # 缓存服务异常
    DATABASE_ERROR = "CART_009"  # 数据库服务异常


class CartException(HTTPException):
    """
    购物车业务异常基类

    继承自FastAPI的HTTPException，保持与框架的兼容性。
    所有购物车模块的业务异常都应继承此类。

    Attributes:
        status_code: HTTP状态码
        error_code: 业务错误码（CART_XXX格式）
        message: 错误描述信息
        details: 错误详细信息字典
    """

    def __init__(
        self,
        status_code: int,
        error_code: CartErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化购物车业务异常

        Args:
            status_code: HTTP状态码（如400, 404, 500）
            error_code: 业务错误码枚举
            message: 错误描述信息
            details: 错误详细信息字典
        """
        self.error_code = error_code
        self.message = message
        self.details = details or {}

        # 构造FastAPI标准错误响应
        detail = {
            "code": error_code.value,
            "message": message,
            "details": self.details,
        }

        super().__init__(status_code=status_code, detail=detail)


# ==================== 具体业务异常类 ====================


class InvalidParameterError(CartException):
    """请求参数验证失败"""

    def __init__(self, message: str = "请求参数验证失败", details: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=CartErrorCode.INVALID_PARAMETER,
            message=message,
            details=details,
        )


class StockInsufficientError(CartException):
    """商品库存不足"""

    def __init__(
        self,
        sku_id: int,
        requested: int,
        available: int,
        message: str = "商品库存不足",
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=CartErrorCode.STOCK_INSUFFICIENT,
            message=message,
            details={
                "sku_id": sku_id,
                "requested_quantity": requested,
                "available_stock": available,
            },
        )


class CartLimitExceededError(CartException):
    """购物车商品数量超限"""

    def __init__(
        self,
        limit: int = 50,
        current: int = 0,
        message: str = "购物车商品种类不能超过50个",
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=CartErrorCode.CART_LIMIT_EXCEEDED,
            message=message,
            details={"max_items": limit, "current_items": current},
        )


class CartItemNotFoundError(CartException):
    """购物车商品项不存在"""

    def __init__(self, item_id: int, message: str = "购物车商品项不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=CartErrorCode.ITEM_NOT_FOUND,
            message=message,
            details={"item_id": item_id},
        )


class ProductNotFoundError(CartException):
    """商品不存在或已下架"""

    def __init__(self, sku_id: int, message: str = "商品不存在或已下架"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=CartErrorCode.PRODUCT_NOT_FOUND,
            message=message,
            details={"sku_id": sku_id},
        )


class ProductAlreadyInCartError(CartException):
    """商品已在购物车中"""

    def __init__(self, sku_id: int, message: str = "商品已在购物车中，请使用更新数量接口"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code=CartErrorCode.ITEM_ALREADY_EXISTS,
            message=message,
            details={"sku_id": sku_id},
        )


class TooManyRequestsError(CartException):
    """操作过于频繁"""

    def __init__(self, message: str = "操作过于频繁，请稍后重试"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=CartErrorCode.TOO_MANY_REQUESTS,
            message=message,
            details={},
        )


class CartCacheError(CartException):
    """缓存服务异常"""

    def __init__(self, message: str = "缓存服务异常"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=CartErrorCode.CACHE_ERROR,
            message=message,
            details={},
        )


class CartDatabaseError(CartException):
    """数据库服务异常"""

    def __init__(self, message: str = "数据库服务异常，请稍后重试"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=CartErrorCode.DATABASE_ERROR,
            message=message,
            details={},
        )


class QuantityExceededError(CartException):
    """商品数量超过限制"""

    def __init__(
        self,
        max_quantity: int = 999,
        current_quantity: int = 0,
        message: str = "单个商品数量不能超过999个",
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=CartErrorCode.INVALID_PARAMETER,
            message=message,
            details={
                "max_quantity_per_item": max_quantity,
                "current_quantity": current_quantity,
            },
        )
