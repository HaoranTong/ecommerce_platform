"""
文件名：router.py
文件路径：app/modules/shopping_cart/router.py
功能描述：购物车模块的FastAPI路由定义
主要功能：
- 购物车API端点定义：6个核心CRUD操作
- 请求参数验证和错误处理
- 统一响应格式处理
- 用户认证和权限校验
使用说明：
- 导入：from app.modules.shopping_cart.router import router
- 在main.py中注册：app.include_router(router, tags=["购物车"])
- API端点：/shopping-cart/ (完整模块名前缀，统一在main.py设置API版本前缀)
依赖模块：
- fastapi: Web框架和路由装饰器
- app.modules.shopping_cart.service: 业务逻辑服务层
- app.modules.shopping_cart.schemas: 请求响应模型
- app.modules.shopping_cart.dependencies: 依赖注入组件
创建时间：2025-09-16
最后修改：2025-09-16
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any
import logging

from .service import CartService
from .schemas import (
    AddItemRequest, 
    UpdateQuantityRequest, 
    BatchDeleteRequest,
    CartResponse,
    SuccessResponse,
    CartUpdateResponse
)
from .dependencies import (
    get_cart_service, 
    get_user_id_from_token, 
    validate_cart_business_rules
)

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器，不设置前缀，在main.py中统一设置
router = APIRouter(tags=["购物车"])


@router.post("/shopping-cart/items", 
             response_model=CartResponse,
             status_code=status.HTTP_200_OK,
             summary="添加商品到购物车",
             description="将指定的商品添加到当前用户的购物车中，如果商品已存在则增加数量")
async def add_item_to_cart(
    request: AddItemRequest,
    user_id: int = Depends(get_user_id_from_token),
    cart_service: CartService = Depends(get_cart_service)
) -> CartResponse:
    """
    添加商品到购物车
    
    **业务规则：**
    - 用户必须已登录
    - 商品必须处于上架状态
    - 库存必须充足
    - 购物车商品种类不超过50个
    - 单个商品数量不超过999个
    
    **请求示例：**
    ```json
    {
        "sku_id": 12345,
        "quantity": 2
    }
    ```
    
    **响应示例：**
    ```json
    {
        "cart_id": 123,
        "total_items": 3,
        "total_quantity": 5,
        "total_amount": 299.99,
        "items": [...],
        "updated_at": "2025-09-16T10:30:00Z"
    }
    ```
    """
    try:
        logger.info(f"添加商品到购物车: user_id={user_id}, sku_id={request.sku_id}, quantity={request.quantity}")
        
        # 验证业务规则
        validate_cart_business_rules(0, request.quantity)  # 商品种类数在service层验证
        
        # 调用业务服务
        cart_response = await cart_service.add_item(user_id, request)
        
        logger.info(f"成功添加商品到购物车: user_id={user_id}, cart_id={cart_response.cart_id}")
        return cart_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加商品到购物车异常: user_id={user_id}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加商品失败"
        )


@router.get("/shopping-cart/cart", 
            response_model=CartResponse,
            summary="获取购物车内容", 
            description="获取当前用户购物车的完整内容，包括商品详情和价格计算")
async def get_cart(
    user_id: int = Depends(get_user_id_from_token),
    cart_service: CartService = Depends(get_cart_service)
) -> CartResponse:
    """
    获取购物车内容
    
    **功能说明：**
    - 返回当前用户购物车的完整信息
    - 包含商品详情、价格、库存状态
    - 自动计算购物车总价和商品数量
    - 优先从缓存读取，提升响应速度
    
    **响应示例：**
    ```json
    {
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
                "unit_price": 99.99,
                "quantity": 2,
                "subtotal": 199.98,
                "stock_status": "in_stock",
                "available_stock": 100
            }
        ]
    }
    ```
    """
    try:
        logger.info(f"获取购物车: user_id={user_id}")
        
        cart_response = await cart_service.get_cart(user_id)
        
        logger.info(f"成功获取购物车: user_id={user_id}, total_items={cart_response.total_items}")
        return cart_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取购物车异常: user_id={user_id}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取购物车失败"
        )


@router.put("/shopping-cart/items/{item_id}", 
            response_model=CartResponse,
            summary="更新商品数量",
            description="更新购物车中指定商品的数量")
async def update_item_quantity(
    item_id: int,
    request: UpdateQuantityRequest,
    user_id: int = Depends(get_user_id_from_token),
    cart_service: CartService = Depends(get_cart_service)
) -> CartResponse:
    """
    更新购物车商品数量
    
    **业务规则：**
    - 商品项必须属于当前用户
    - 新数量必须在1-999之间
    - 库存必须充足
    - 自动重新计算价格
    
    **路径参数：**
    - item_id: 购物车商品项ID
    
    **请求示例：**
    ```json
    {
        "quantity": 5
    }
    ```
    """
    try:
        logger.info(f"更新商品数量: user_id={user_id}, item_id={item_id}, quantity={request.quantity}")
        
        # 验证数量范围
        validate_cart_business_rules(0, request.quantity)
        
        # 调用业务服务
        cart_response = await cart_service.update_quantity(user_id, item_id, request.quantity)
        
        logger.info(f"成功更新商品数量: user_id={user_id}, item_id={item_id}")
        return cart_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新商品数量异常: user_id={user_id}, item_id={item_id}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新商品数量失败"
        )


@router.delete("/shopping-cart/items/{item_id}",
               response_model=SuccessResponse,
               summary="删除单个商品",
               description="从购物车删除指定的商品项")
async def delete_cart_item(
    item_id: int,
    user_id: int = Depends(get_user_id_from_token),
    cart_service: CartService = Depends(get_cart_service)
) -> SuccessResponse:
    """
    删除购物车商品项
    
    **功能说明：**
    - 从购物车中移除指定商品项
    - 自动重新计算购物车总价
    - 清理相关缓存数据
    
    **路径参数：**
    - item_id: 要删除的商品项ID
    """
    try:
        logger.info(f"删除购物车商品: user_id={user_id}, item_id={item_id}")
        
        success = await cart_service.delete_item(user_id, item_id)
        
        if success:
            logger.info(f"成功删除购物车商品: user_id={user_id}, item_id={item_id}")
            return SuccessResponse(message="商品已从购物车中删除")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商品项不存在"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除购物车商品异常: user_id={user_id}, item_id={item_id}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除商品失败"
        )


@router.delete("/shopping-cart/items",
               response_model=SuccessResponse, 
               summary="批量删除商品",
               description="批量删除购物车中的多个商品项")
async def batch_delete_items(
    request: BatchDeleteRequest,
    user_id: int = Depends(get_user_id_from_token),
    cart_service: CartService = Depends(get_cart_service)
) -> SuccessResponse:
    """
    批量删除购物车商品
    
    **功能说明：**
    - 一次性删除多个购物车商品项
    - 提升用户操作效率
    - 事务性操作，保证数据一致性
    
    **请求示例：**
    ```json
    {
        "item_ids": [123, 456, 789]
    }
    ```
    """
    try:
        logger.info(f"批量删除购物车商品: user_id={user_id}, item_ids={request.item_ids}")
        
        success = await cart_service.batch_delete_items(user_id, request.item_ids)
        
        if success:
            logger.info(f"成功批量删除购物车商品: user_id={user_id}, count={len(request.item_ids)}")
            return SuccessResponse(message=f"已删除{len(request.item_ids)}个商品")
        else:
            return SuccessResponse(message="未找到要删除的商品")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除购物车商品异常: user_id={user_id}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量删除商品失败"
        )


@router.delete("/shopping-cart/cart",
               response_model=SuccessResponse,
               summary="清空购物车", 
               description="清空当前用户的整个购物车")
async def clear_cart(
    user_id: int = Depends(get_user_id_from_token),
    cart_service: CartService = Depends(get_cart_service)
) -> SuccessResponse:
    """
    清空购物车
    
    **功能说明：**
    - 删除购物车中的所有商品项
    - 保留购物车主记录
    - 清理所有相关缓存
    
    **注意事项：**
    - 此操作不可撤销
    - 建议在前端添加确认对话框
    """
    try:
        logger.info(f"清空购物车: user_id={user_id}")
        
        success = await cart_service.clear_cart(user_id)
        
        if success:
            logger.info(f"成功清空购物车: user_id={user_id}")
            return SuccessResponse(message="购物车已清空")
        else:
            return SuccessResponse(message="购物车已为空")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清空购物车异常: user_id={user_id}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清空购物车失败"
        )


# ==================== 健康检查端点 ====================

@router.get("/shopping-cart/health",
            summary="购物车服务健康检查",
            description="检查购物车服务的运行状态",
            include_in_schema=False)  # 不在API文档中显示
async def health_check() -> Dict[str, Any]:
    """
    购物车服务健康检查
    
    返回服务运行状态信息
    """
    return {
        "status": "healthy",
        "service": "shopping-cart",
        "version": "1.0.0",
        "timestamp": "2025-09-16T10:30:00Z"
    }
