"""
Redis连接和缓存管理模块
"""
import os
import json
import redis.asyncio as redis
from typing import Optional, Dict, Any, List
from fastapi import HTTPException

# Redis配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Redis连接池
redis_pool: Optional[redis.Redis] = None

async def get_redis_connection() -> redis.Redis:
    """获取Redis连接"""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_pool

async def close_redis_connection():
    """关闭Redis连接"""
    global redis_pool
    if redis_pool:
        await redis_pool.aclose()
        redis_pool = None

class RedisCartManager:
    """Redis购物车管理器"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def _get_redis(self) -> redis.Redis:
        """获取Redis连接"""
        if self.redis is None:
            self.redis = await get_redis_connection()
        return self.redis
    
    def _get_cart_key(self, user_id: int) -> str:
        """生成购物车Redis key"""
        return f"cart:user:{user_id}"
    
    def _get_cart_item_key(self, user_id: int, product_id: int) -> str:
        """生成购物车商品Redis key"""
        return f"cart:user:{user_id}:product:{product_id}"
    
    async def add_item(self, user_id: int, product_id: int, quantity: int) -> bool:
        """添加商品到购物车"""
        try:
            redis = await self._get_redis()
            cart_key = self._get_cart_key(user_id)
            item_key = self._get_cart_item_key(user_id, product_id)
            
            # 检查商品是否已存在
            existing_quantity = await redis.hget(cart_key, str(product_id))
            if existing_quantity:
                # 如果已存在，增加数量
                new_quantity = int(existing_quantity) + quantity
            else:
                new_quantity = quantity
            
            # 存储到Redis
            await redis.hset(cart_key, str(product_id), new_quantity)
            
            # 设置过期时间（7天）
            await redis.expire(cart_key, 7 * 24 * 3600)
            
            return True
        except Exception as e:
            print(f"Error adding item to cart: {e}")
            return False
    
    async def update_item_quantity(self, user_id: int, product_id: int, quantity: int) -> bool:
        """更新购物车商品数量"""
        try:
            redis = await self._get_redis()
            cart_key = self._get_cart_key(user_id)
            
            if quantity <= 0:
                # 如果数量为0或负数，删除该商品
                await redis.hdel(cart_key, str(product_id))
            else:
                await redis.hset(cart_key, str(product_id), quantity)
            
            return True
        except Exception as e:
            print(f"Error updating cart item: {e}")
            return False
    
    async def remove_item(self, user_id: int, product_id: int) -> bool:
        """从购物车移除商品"""
        try:
            redis = await self._get_redis()
            cart_key = self._get_cart_key(user_id)
            
            result = await redis.hdel(cart_key, str(product_id))
            return result > 0
        except Exception as e:
            print(f"Error removing item from cart: {e}")
            return False
    
    async def get_cart_items(self, user_id: int) -> Dict[str, int]:
        """获取购物车所有商品"""
        try:
            redis = await self._get_redis()
            cart_key = self._get_cart_key(user_id)
            
            items = await redis.hgetall(cart_key)
            # 将值转换为整数
            return {product_id: int(quantity) for product_id, quantity in items.items()}
        except Exception as e:
            print(f"Error getting cart items: {e}")
            return {}
    
    async def get_item_quantity(self, user_id: int, product_id: int) -> int:
        """获取购物车中特定商品的数量"""
        try:
            redis = await self._get_redis()
            cart_key = self._get_cart_key(user_id)
            
            quantity = await redis.hget(cart_key, str(product_id))
            return int(quantity) if quantity else 0
        except Exception as e:
            print(f"Error getting item quantity: {e}")
            return 0
    
    async def clear_cart(self, user_id: int) -> bool:
        """清空购物车"""
        try:
            redis = await self._get_redis()
            cart_key = self._get_cart_key(user_id)
            
            await redis.delete(cart_key)
            return True
        except Exception as e:
            print(f"Error clearing cart: {e}")
            return False
    
    async def get_cart_count(self, user_id: int) -> int:
        """获取购物车商品种类数量"""
        try:
            redis = await self._get_redis()
            cart_key = self._get_cart_key(user_id)
            
            count = await redis.hlen(cart_key)
            return count
        except Exception as e:
            print(f"Error getting cart count: {e}")
            return 0
    
    async def get_cart_total_quantity(self, user_id: int) -> int:
        """获取购物车商品总数量"""
        try:
            items = await self.get_cart_items(user_id)
            return sum(items.values())
        except Exception as e:
            print(f"Error getting cart total quantity: {e}")
            return 0

# 全局购物车管理器实例
cart_manager = RedisCartManager()
