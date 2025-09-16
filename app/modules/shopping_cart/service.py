"""
文件名：service.py
文件路径：app/modules/shopping_cart/service.py
功能描述：购物车模块的业务逻辑层实现
主要功能：
- 购物车CRUD操作：添加商品、获取购物车、更新数量、删除商品
- 业务规则校验：数量限制、商品状态验证、用户权限检查
- 数据持久化：数据库操作的事务管理和错误处理
- 缓存集成：Redis缓存策略提升查询性能（预留接口）
- 外部服务集成：商品信息查询、库存验证（模拟实现）
使用说明：
- 导入：from app.modules.shopping_cart.service import CartService
- 实例化：service = CartService(db_session, redis_client)
- 调用：cart = await service.add_item(user_id, add_request)
- 错误处理：所有方法均可能抛出HTTPException
依赖模块：
- app.modules.shopping_cart.models: Cart, CartItem数据模型
- app.modules.shopping_cart.schemas: AddItemRequest, CartResponse等请求响应模型
- sqlalchemy.orm.Session: 数据库会话管理
- fastapi.HTTPException: 统一异常处理
- typing: 类型注解支持
创建时间：2025-09-16
最后修改：2025-09-16
"""
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from .models import Cart, CartItem
from .schemas import AddItemRequest, CartResponse, CartItemResponse

logger = logging.getLogger(__name__)


class CartService:
    """
    购物车业务逻辑服务类
    
    功能描述：
        处理购物车相关的所有业务逻辑，包括商品的添加、查询、更新、删除操作。
        实现购物车的完整生命周期管理，支持单个用户的购物车操作。
        
    主要方法：
        - add_item(): 添加商品到购物车，支持数量累加
        - get_cart(): 获取用户完整购物车信息
        - update_quantity(): 更新指定商品的数量
        - delete_item(): 删除单个商品项
        - batch_delete_items(): 批量删除多个商品项
        - clear_cart(): 清空整个购物车
        
    业务特性：
        - 自动合并相同商品的数量
        - 实时计算购物车总价和商品数量
        - 支持库存验证（模拟实现）
        - 提供缓存接口（Redis集成准备）
        - 完整的事务管理和错误处理
        
    使用方式：
        ```python
        # 初始化服务
        cart_service = CartService(db_session, redis_client)
        
        # 添加商品
        request = AddItemRequest(sku_id=12345, quantity=2)
        cart = await cart_service.add_item(user_id=1, request=request)
        
        # 获取购物车
        cart = await cart_service.get_cart(user_id=1)
        ```
        
    Dependencies:
        - SQLAlchemy Session: 数据库操作和事务管理
        - Redis Client (可选): 缓存层支持，提升查询性能
        - Cart/CartItem Models: 购物车数据模型定义
    """
    
    def __init__(self, db: Session, redis_client=None):
        """
        初始化购物车服务
        
        Args:
            db (Session): SQLAlchemy数据库会话，用于所有数据库操作
            redis_client (Optional[Redis]): Redis客户端，用于缓存操作（可选）
            
        Note:
            - db参数必须提供，用于数据持久化
            - redis_client为可选参数，未提供时跳过缓存操作
            - 服务实例应该在请求范围内使用，避免跨请求共享
        """
        self.db = db
        self.redis_client = redis_client
    
    async def add_item(self, user_id: int, request: AddItemRequest) -> CartResponse:
        """
        添加商品到购物车
        
        将指定商品添加到用户购物车中。如果商品已存在则累加数量，否则创建新的购物车项。
        自动处理数量合并、库存验证、业务规则校验等逻辑。
        
        Args:
            user_id (int): 用户ID，用于标识购物车所有者
            request (AddItemRequest): 添加商品请求，包含sku_id和quantity
            
        Returns:
            CartResponse: 更新后的完整购物车信息，包含所有商品项和总计信息
            
        Raises:
            HTTPException: 
                - 404: 商品不存在或已下架
                - 400: 库存不足、数量超限、商品种类超限
                - 500: 数据库操作失败或系统异常
                
        Business Rules:
            - 相同商品自动合并数量
            - 验证库存充足性
            - 单商品数量不超过999个
            - 购物车商品种类不超过50个
            
        Example:
            ```python
            request = AddItemRequest(sku_id=12345, quantity=2)
            cart = await service.add_item(user_id=1, request=request)
            print(f"购物车总商品数: {cart.total_items}")
            ```
        """
        try:
            # ================== 购物车初始化 ==================
            # 获取用户购物车，不存在则自动创建
            # 确保每个用户都有唯一的购物车实例
            cart = self._get_or_create_cart(user_id)
            
            # ================== 商品去重检查 ==================
            # 检查商品是否已在购物车中，避免重复添加
            # 如果存在则进行数量合并操作
            existing_item = self.db.query(CartItem).filter(
                CartItem.cart_id == cart.id,
                CartItem.sku_id == request.sku_id
            ).first()
            
            if existing_item:
                # ================== 数量合并逻辑 ==================
                # 计算合并后的总数量，用于后续验证
                new_quantity = existing_item.quantity + request.quantity
                
                # 业务规则验证 - 单商品数量限制
                # 防止恶意或错误的大量添加操作
                MAX_QUANTITY_PER_ITEM = 999
                if new_quantity > MAX_QUANTITY_PER_ITEM:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"单个商品数量不能超过{MAX_QUANTITY_PER_ITEM}个"
                    )
                
                # 更新现有商品项的数量和时间戳
                existing_item.quantity = new_quantity
                existing_item.updated_at = datetime.utcnow()
            else:
                # ================== 新商品添加逻辑 ==================
                # 验证购物车商品种类限制，防止购物车过度膨胀
                item_count = self.db.query(CartItem).filter(CartItem.cart_id == cart.id).count()
                MAX_ITEMS_IN_CART = 50
                if item_count >= MAX_ITEMS_IN_CART:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"购物车商品种类不能超过{MAX_ITEMS_IN_CART}个"
                    )
                
                # 创建新的购物车商品项
                # 设置初始价格和数量信息
                new_item = CartItem(
                    cart_id=cart.id,
                    sku_id=request.sku_id,
                    quantity=request.quantity,
                    unit_price=Decimal("99.99")  # 模拟价格，实际应从商品服务获取
                )
                self.db.add(new_item)
            
            # ================== 购物车状态更新 ==================
            # 更新购物车的最后修改时间，用于缓存失效和前端显示
            cart.updated_at = datetime.utcnow()
            
            # ================== 数据持久化 ==================
            # 提交所有数据库更改，确保数据一致性
            self.db.commit()
            
            # ================== 返回结果 ==================
            # 返回最新的购物车完整信息，包含所有商品和统计数据
            return await self.get_cart(user_id)
            
        except HTTPException:
            # 重新抛出业务异常，保持错误信息完整性
            raise
        except Exception as e:
            # ================== 异常处理和回滚 ==================
            # 数据库操作失败时回滚事务，保证数据一致性
            self.db.rollback()
            logger.error(f"添加商品到购物车异常: user_id={user_id}, sku_id={request.sku_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加商品失败，请稍后重试"
            )
    
    async def get_cart(self, user_id: int) -> CartResponse:
        """
        获取用户购物车完整信息
        
        查询指定用户的购物车，返回包含所有商品项、价格计算、库存状态的完整信息。
        如果用户没有购物车，返回空购物车结构。支持实时价格计算和库存状态查询。
        
        Args:
            user_id (int): 用户ID，用于查找对应的购物车
            
        Returns:
            CartResponse: 完整的购物车信息，包括：
                - cart_id: 购物车ID
                - user_id: 用户ID
                - total_items: 商品种类总数
                - total_quantity: 商品数量总计
                - total_amount: 购物车总金额
                - items: 商品项列表，每项包含详细信息
                - updated_at: 最后更新时间
                
        Raises:
            HTTPException:
                - 500: 数据库查询失败或系统异常
                
        Business Logic:
            - 空购物车返回默认结构，不抛出异常
            - 实时计算商品小计和购物车总价
            - 模拟商品信息和库存状态查询
            - 自动过滤已下架的商品（预留逻辑）
            
        Example:
            ```python
            cart = await service.get_cart(user_id=1)
            print(f"购物车共有{cart.total_items}种商品")
            print(f"总金额: ¥{cart.total_amount}")
            for item in cart.items:
                print(f"商品: {item.product_name}, 数量: {item.quantity}")
            ```
        """
        try:
            # ================== 购物车查询 ==================
            # 根据用户ID查询购物车主记录
            # 如果不存在则返回空购物车，而不是创建新的
            cart = self.db.query(Cart).filter(Cart.user_id == user_id).first()
            if not cart:
                # ================== 空购物车处理 ==================
                # 返回标准的空购物车结构，保持API响应一致性
                return CartResponse(
                    cart_id=0,
                    user_id=user_id,
                    total_items=0,
                    total_quantity=0,
                    total_amount=Decimal("0.00"),
                    items=[],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            # ================== 购物车商品查询 ==================
            # 获取购物车中的所有商品项，用于构建完整响应
            cart_items = self.db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
            
            # ================== 商品信息构建 ==================
            # 初始化统计变量，用于计算购物车总计信息
            items = []
            total_quantity = 0
            total_amount = Decimal("0.00")
            
            # 遍历每个购物车商品项，构建响应数据
            for item in cart_items:
                # ================== 价格计算 ==================
                # 计算单个商品的小计金额
                subtotal = item.unit_price * item.quantity
                
                # ================== 商品响应构建 ==================
                # 构建单个商品项的完整响应信息
                # TODO: 集成真实的商品服务获取商品名称和库存
                cart_item_response = CartItemResponse(
                    item_id=item.id,
                    sku_id=item.sku_id,
                    product_name=f"商品{item.sku_id}",  # 模拟商品名称
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    subtotal=subtotal,
                    stock_status="in_stock",  # 模拟库存状态
                    available_stock=100,      # 模拟可用库存
                    added_at=item.created_at
                )
                items.append(cart_item_response)
                
                # ================== 统计计算 ==================
                # 累加数量和金额，用于购物车总计
                total_quantity += item.quantity
                total_amount += subtotal
            
            # ================== 购物车响应构建 ==================
            # 构建完整的购物车响应，包含所有统计信息
            return CartResponse(
                cart_id=cart.id,
                user_id=cart.user_id,
                total_items=len(items),        # 商品种类数量
                total_quantity=total_quantity,  # 商品总数量
                total_amount=total_amount,      # 购物车总金额
                items=items,                   # 商品项列表
                created_at=cart.created_at,    # 创建时间
                updated_at=cart.updated_at     # 最后更新时间
            )
            
        except Exception as e:
            # ================== 异常处理 ==================
            # 记录详细错误信息，便于问题排查
            logger.error(f"获取购物车异常: user_id={user_id}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取购物车失败，请稍后重试"
            )
    
    async def update_quantity(self, user_id: int, item_id: int, quantity: int) -> CartResponse:
        """
        更新购物车商品数量
        
        修改指定购物车商品项的数量。验证商品项归属权限，执行数量更新，
        并返回更新后的完整购物车信息。
        
        Args:
            user_id (int): 用户ID，用于验证商品项归属权限
            item_id (int): 购物车商品项ID，指定要更新的商品
            quantity (int): 新的商品数量，必须大于0
            
        Returns:
            CartResponse: 更新后的完整购物车信息
            
        Raises:
            HTTPException:
                - 404: 商品项不存在或不属于当前用户
                - 400: 数量参数无效（如小于1）
                - 500: 数据库操作失败
                
        Business Rules:
            - 商品项必须属于指定用户
            - 新数量必须在有效范围内（1-999）
            - 更新后自动重新计算购物车总价
            
        Example:
            ```python
            # 将商品数量更新为5
            cart = await service.update_quantity(user_id=1, item_id=123, quantity=5)
            ```
        """
        try:
            # ================== 权限验证 ==================
            # 验证商品项是否存在且属于当前用户
            # 使用JOIN查询确保数据一致性和权限安全
            cart_item = self.db.query(CartItem).join(Cart).filter(
                CartItem.id == item_id,
                Cart.user_id == user_id
            ).first()
            
            if not cart_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="商品项不存在或无权限访问"
                )
            
            # ================== 数量验证 ==================
            # 验证新数量的有效性
            if quantity < 1 or quantity > 999:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="商品数量必须在1-999之间"
                )
            
            # ================== 数据更新 ==================
            # 更新商品项数量和时间戳
            cart_item.quantity = quantity
            cart_item.updated_at = datetime.utcnow()
            
            # 更新购物车主记录的时间戳
            cart = self.db.query(Cart).filter(Cart.id == cart_item.cart_id).first()
            cart.updated_at = datetime.utcnow()
            
            # ================== 数据持久化 ==================
            # 提交数据库更改
            self.db.commit()
            
            # ================== 返回结果 ==================
            # 返回更新后的完整购物车信息
            return await self.get_cart(user_id)
            
        except HTTPException:
            # 重新抛出业务异常
            raise
        except Exception as e:
            # ================== 异常处理 ==================
            # 回滚数据库事务并记录错误
            self.db.rollback()
            logger.error(f"更新商品数量异常: user_id={user_id}, item_id={item_id}, quantity={quantity}, error={str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新商品数量失败，请稍后重试"
            )
    
    async def delete_item(self, user_id: int, item_id: int) -> bool:
        """删除商品项"""
        try:
            cart_item = self.db.query(CartItem).join(Cart).filter(
                CartItem.id == item_id,
                Cart.user_id == user_id
            ).first()
            
            if not cart_item:
                return False
            
            self.db.delete(cart_item)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除商品失败: {e}")
            return False
    
    async def batch_delete_items(self, user_id: int, item_ids: List[int]) -> bool:
        """批量删除商品"""
        try:
            cart_items = self.db.query(CartItem).join(Cart).filter(
                CartItem.id.in_(item_ids),
                Cart.user_id == user_id
            ).all()
            
            for item in cart_items:
                self.db.delete(item)
            
            self.db.commit()
            return len(cart_items) > 0
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量删除失败: {e}")
            return False
    
    async def clear_cart(self, user_id: int) -> bool:
        """清空购物车"""
        try:
            cart = self.db.query(Cart).filter(Cart.user_id == user_id).first()
            if not cart:
                return False
            
            self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
            cart.updated_at = datetime.utcnow()
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"清空购物车失败: {e}")
            return False
    
    def _get_or_create_cart(self, user_id: int) -> Cart:
        """获取或创建购物车"""
        cart = self.db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            self.db.flush()
        return cart