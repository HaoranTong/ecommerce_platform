"""
文件名：schemas.py
文件路径：app/modules/shopping_cart/schemas.py
功能描述：购物车模块的Pydantic数据传输对象
主要功能：
- 请求模型：AddItemRequest, UpdateQuantityRequest, BatchDeleteRequest
- 响应模型：CartResponse, CartItemResponse, SuccessResponse
- 数据验证：输入参数验证，业务规则检查
使用说明：
- 导入：from app.modules.shopping_cart.schemas import CartResponse, AddItemRequest
- API接口：用于FastAPI请求响应模型定义
依赖模块：
- pydantic: 数据验证框架
- typing: 类型提示支持
创建时间：2025-09-16
最后修改：2025-09-16
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum


class StockStatus(str, Enum):
    """库存状态枚举"""
    IN_STOCK = "in_stock"          # 有库存
    LOW_STOCK = "low_stock"        # 库存不足
    OUT_OF_STOCK = "out_of_stock"  # 无库存


# ==================== 请求模型 ====================

class AddItemRequest(BaseModel):
    """添加商品到购物车请求模型"""
    sku_id: int = Field(..., gt=0, description="商品SKU ID")
    quantity: int = Field(..., ge=1, le=999, description="商品数量")
    
    class Config:
        schema_extra = {
            "example": {
                "sku_id": 12345,
                "quantity": 2
            }
        }


class UpdateQuantityRequest(BaseModel):
    """更新商品数量请求模型"""
    quantity: int = Field(..., ge=1, le=999, description="新的商品数量")
    
    class Config:
        schema_extra = {
            "example": {
                "quantity": 5
            }
        }


class BatchDeleteRequest(BaseModel):
    """批量删除商品请求模型"""
    item_ids: List[int] = Field(..., min_length=1, description="要删除的商品项ID列表")
    
    @field_validator('item_ids')
    @classmethod
    def validate_item_ids(cls, v):
        if not all(item_id > 0 for item_id in v):
            raise ValueError('所有商品项ID必须大于0')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "item_ids": [123, 456, 789]
            }
        }


# ==================== 响应模型 ====================

class CartItemResponse(BaseModel):
    """购物车商品项响应模型"""
    item_id: int = Field(..., description="商品项ID")
    sku_id: int = Field(..., description="商品SKU ID")
    product_name: str = Field(..., description="商品名称")
    product_image: Optional[str] = Field(None, description="商品图片URL")
    unit_price: Decimal = Field(..., description="商品单价")
    quantity: int = Field(..., description="商品数量")
    subtotal: Decimal = Field(..., description="小计金额")
    stock_status: StockStatus = Field(..., description="库存状态")
    available_stock: Optional[int] = Field(None, description="可用库存数量")
    added_at: datetime = Field(..., description="添加时间")
    
    class Config:
        orm_mode = True
        use_enum_values = True
        schema_extra = {
            "example": {
                "item_id": 456,
                "sku_id": 12345,
                "product_name": "iPhone 15 Pro",
                "product_image": "https://cdn.example.com/iphone15.jpg",
                "unit_price": 99.99,
                "quantity": 2,
                "subtotal": 199.98,
                "stock_status": "in_stock",
                "available_stock": 100,
                "added_at": "2025-09-16T10:30:00Z"
            }
        }


class CartResponse(BaseModel):
    """购物车响应模型"""
    cart_id: int = Field(..., description="购物车ID")
    user_id: int = Field(..., description="用户ID")
    total_items: int = Field(..., description="商品种类数量")
    total_quantity: int = Field(..., description="商品总数量")
    total_amount: Decimal = Field(..., description="购物车总金额")
    items: List[CartItemResponse] = Field(..., description="购物车商品项列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "cart_id": 123,
                "user_id": 789,
                "total_items": 2,
                "total_quantity": 4,
                "total_amount": 399.98,
                "items": [
                    {
                        "item_id": 456,
                        "sku_id": 12345,
                        "product_name": "iPhone 15 Pro",
                        "product_image": "https://cdn.example.com/iphone15.jpg",
                        "unit_price": 99.99,
                        "quantity": 2,
                        "subtotal": 199.98,
                        "stock_status": "in_stock",
                        "available_stock": 100,
                        "added_at": "2025-09-16T10:30:00Z"
                    }
                ],
                "created_at": "2025-09-16T10:30:00Z",
                "updated_at": "2025-09-16T11:00:00Z"
            }
        }


class SuccessResponse(BaseModel):
    """成功操作响应模型"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "商品已从购物车中删除"
            }
        }


class UpdatedItemResponse(BaseModel):
    """更新商品项响应模型"""
    item_id: int = Field(..., description="商品项ID")
    sku_id: int = Field(..., description="商品SKU ID")
    quantity: int = Field(..., description="更新后数量")
    subtotal: Decimal = Field(..., description="更新后小计")
    
    class Config:
        schema_extra = {
            "example": {
                "item_id": 456,
                "sku_id": 12345,
                "quantity": 5,
                "subtotal": 499.95
            }
        }


class CartUpdateResponse(BaseModel):
    """购物车更新响应模型"""
    cart_id: int = Field(..., description="购物车ID")
    total_items: int = Field(..., description="商品种类数量")
    total_quantity: int = Field(..., description="商品总数量")
    total_amount: Decimal = Field(..., description="购物车总金额")
    updated_item: Optional[UpdatedItemResponse] = Field(None, description="更新的商品项")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "cart_id": 123,
                "total_items": 2,
                "total_quantity": 6,
                "total_amount": 499.95,
                "updated_item": {
                    "item_id": 456,
                    "sku_id": 12345,
                    "quantity": 5,
                    "subtotal": 499.95
                },
                "updated_at": "2025-09-16T11:30:00Z"
            }
        }


# ==================== 错误响应模型 ====================

class ErrorDetail(BaseModel):
    """错误详情模型"""
    sku_id: Optional[int] = Field(None, description="相关商品SKU ID")
    item_id: Optional[int] = Field(None, description="相关商品项ID")
    requested_quantity: Optional[int] = Field(None, description="请求数量")
    available_stock: Optional[int] = Field(None, description="可用库存")
    adjusted_quantity: Optional[int] = Field(None, description="调整后数量")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="操作是否成功")
    error: "ErrorInfo" = Field(..., description="错误信息")
    timestamp: datetime = Field(..., description="错误发生时间")
    request_id: Optional[str] = Field(None, description="请求ID")


class ErrorInfo(BaseModel):
    """错误信息模型"""
    code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    details: Optional[ErrorDetail] = Field(None, description="错误详情")
    
    class Config:
        schema_extra = {
            "example": {
                "code": "CART_002",
                "message": "商品库存不足",
                "details": {
                    "sku_id": 12345,
                    "requested_quantity": 10,
                    "available_stock": 5
                }
            }
        }
