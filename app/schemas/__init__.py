"""
文件名：__init__.py
文件路径：app/schemas/__init__.py
功能描述：Pydantic模式模块统一导出和管理
主要功能：
- 统一导出所有Pydantic模式类
- 提供模式访问的统一入口
- 模块化管理输入输出数据结构
使用说明：
- 导入：from app.schemas import UserCreate, ProductRead, OrderCreate
- 或：from app.schemas.user import UserCreate
- 基类：from app.schemas.base import BaseSchema
依赖模块：
- app.schemas.base: 基础模式配置
- app.schemas.user: 用户相关模式
- app.schemas.product: 商品相关模式
- app.schemas.order: 订单相关模式
- app.schemas.payment: 支付相关模式
"""

# 导入基础模式
from .base import (
    BaseSchema, 
    TimestampSchema,
    PaginationParams,
    SortParams,
    ApiResponse,
    PaginatedResponse,
    ErrorResponse
)

# 导入用户相关模式
from .user import (
    UserRegister,
    UserLogin,
    UserCreate,
    UserUpdate,
    UserChangePassword,
    UserRead,
    UserProfile,
    UserPublic,
    Token,
    TokenRefresh,
    TokenData,
    UserStats
)

# 导入商品相关模式
from .product import (
    CategoryCreate,
    CategoryUpdate,
    CategoryRead,
    CategoryTreeRead,
    CategoryStats,
    ProductCreate,
    ProductUpdate,
    ProductStockUpdate,
    ProductRead,
    ProductDetail,
    ProductSearch,
    ProductStats,
    ProductBatch,
    ProductImport
)

# 导入订单相关模式
from .order import (
    OrderItemCreate,
    OrderItemRead,
    OrderCreate,
    OrderUpdate,
    OrderStatusUpdate,
    OrderRead,
    OrderDetail,
    OrderSearch,
    OrderStats,
    CartItemAdd,
    CartItemUpdate,
    CartItemRead,
    CartSummary,
    CartValidation,
    CartMerge,
    OrderBatch,
    OrderExport
)

# 导入支付相关模式
from .payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentStatusUpdate,
    PaymentRead,
    PaymentDetail,
    PaymentSearch,
    RefundCreate,
    RefundUpdate,
    RefundStatusUpdate,
    RefundRead,
    RefundDetail,
    PaymentCallback,
    WechatPaymentCallback,
    AlipayCallback,
    PaymentStats,
    PaymentTrend,
    PaymentAnalysis,
    PaymentBatch,
    RefundBatch
)

# 统一导出所有模式（按模块分组）
__all__ = [
    # 基础模式
    'BaseSchema',
    'TimestampSchema', 
    'PaginationParams',
    'SortParams',
    'ApiResponse',
    'PaginatedResponse',
    'ErrorResponse',
    
    # 用户模式
    'UserRegister',
    'UserLogin',
    'UserCreate',
    'UserUpdate',
    'UserChangePassword',
    'UserRead',
    'UserProfile',
    'UserPublic',
    'Token',
    'TokenRefresh',
    'TokenData',
    'UserStats',
    
    # 商品模式
    'CategoryCreate',
    'CategoryUpdate',
    'CategoryRead',
    'CategoryTreeRead',
    'CategoryStats',
    'ProductCreate',
    'ProductUpdate',
    'ProductStockUpdate',
    'ProductRead',
    'ProductDetail',
    'ProductSearch',
    'ProductStats',
    'ProductBatch',
    'ProductImport',
    
    # 订单模式
    'OrderItemCreate',
    'OrderItemRead',
    'OrderCreate',
    'OrderUpdate',
    'OrderStatusUpdate',
    'OrderRead',
    'OrderDetail',
    'OrderSearch',
    'OrderStats',
    'CartItemAdd',
    'CartItemUpdate',
    'CartItemRead',
    'CartSummary',
    'CartValidation',
    'CartMerge',
    'OrderBatch',
    'OrderExport',
    
    # 支付模式
    'PaymentCreate',
    'PaymentUpdate',
    'PaymentStatusUpdate',
    'PaymentRead',
    'PaymentDetail',
    'PaymentSearch',
    'RefundCreate',
    'RefundUpdate',
    'RefundStatusUpdate',
    'RefundRead',
    'RefundDetail',
    'PaymentCallback',
    'WechatPaymentCallback',
    'AlipayCallback',
    'PaymentStats',
    'PaymentTrend',
    'PaymentAnalysis',
    'PaymentBatch',
    'RefundBatch'
]


# 模式版本信息
SCHEMA_VERSION = "1.0.0"

# 模式模块映射
SCHEMA_MODULES = {
    'user': 'app.schemas.user',
    'product': 'app.schemas.product', 
    'order': 'app.schemas.order',
    'payment': 'app.schemas.payment',
    'base': 'app.schemas.base'
}