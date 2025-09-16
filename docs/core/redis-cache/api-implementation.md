<!--
文档说明：
- 内容：Redis缓存模块API接口实现细节，包含缓存策略和Redis客户端管理的具体实现
- 使用方法：开发人员实现缓存功能时的详细指导文档
- 更新方法：缓存实现代码变更时同步更新，记录实际的实现方案
- 引用关系：基于api-spec.md接口规范，被缓存相关开发使用
- 更新频率：缓存代码实现变更时
-->

# Redis缓存模块API实现细节

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## 实现架构

### 核心文件结构
```
app/cache/
├── __init__.py
├── redis_client.py        # Redis客户端管理
├── cache_manager.py       # 缓存策略管理
├── serializers.py         # 数据序列化
└── strategies/
    ├── __init__.py
    ├── session_cache.py    # 会话缓存策略
    ├── product_cache.py    # 商品缓存策略
    └── cart_cache.py       # 购物车缓存策略
```

## 核心实现

### 1. Redis客户端管理

#### 文件: `app/cache/redis_client.py`
```python
import redis.asyncio as redis
from typing import Optional, Any, Dict
import json
import pickle
import time
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.settings = get_settings()
        self._stats = {
            'commands_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'start_time': time.time()
        }
    
    async def init_redis(self):
        """初始化Redis连接"""
        self.client = redis.Redis(
            host=self.settings.redis_host,
            port=self.settings.redis_port,
            password=self.settings.redis_password,
            db=self.settings.redis_db,
            decode_responses=False,  # 使用bytes以支持pickle
            max_connections=20,
            retry_on_timeout=True,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        
        # 测试连接
        await self.client.ping()
        logger.info("Redis连接初始化完成")
    
    async def close_redis(self):
        """关闭Redis连接"""
        if self.client:
            await self.client.close()
            logger.info("Redis连接已关闭")
    
    async def get(self, key: str, use_json: bool = True) -> Any:
        """获取缓存数据"""
        try:
            self._stats['commands_processed'] += 1
            
            data = await self.client.get(key)
            if data is None:
                self._stats['cache_misses'] += 1
                return None
            
            self._stats['cache_hits'] += 1
            
            if use_json:
                return json.loads(data)
            else:
                return pickle.loads(data)
                
        except Exception as e:
            logger.error(f"Redis GET 错误: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None, use_json: bool = True):
        """设置缓存数据"""
        try:
            self._stats['commands_processed'] += 1
            
            if use_json:
                data = json.dumps(value, ensure_ascii=False)
            else:
                data = pickle.dumps(value)
            
            await self.client.set(key, data, ex=expire)
            
        except Exception as e:
            logger.error(f"Redis SET 错误: {e}")
    
    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            self._stats['commands_processed'] += 1
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE 错误: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            result = await self.client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS 错误: {e}")
            return False
    
    async def expire(self, key: str, time: int) -> bool:
        """设置键过期时间"""
        try:
            result = await self.client.expire(key, time)
            return result
        except Exception as e:
            logger.error(f"Redis EXPIRE 错误: {e}")
            return False
    
    async def get_redis_info(self) -> Dict[str, Any]:
        """获取Redis服务器信息"""
        try:
            info = await self.client.info()
            return {
                "version": info.get('redis_version', 'unknown'),
                "uptime": info.get('uptime_in_seconds', 0),
                "connected_clients": info.get('connected_clients', 0),
                "memory_usage": f"{info.get('used_memory_human', '0B')}",
                "memory_peak": f"{info.get('used_memory_peak_human', '0B')}",
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0)
            }
        except Exception as e:
            logger.error(f"获取Redis信息错误: {e}")
            return {}
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        redis_info = await self.get_redis_info()
        
        # 计算命中率
        hits = redis_info.get('keyspace_hits', 0)
        misses = redis_info.get('keyspace_misses', 0)
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        # 获取键数量
        total_keys = 0
        try:
            info = await self.client.info('keyspace')
            for db_info in info.values():
                if isinstance(db_info, dict) and 'keys' in db_info:
                    total_keys += db_info['keys']
        except:
            pass
        
        return {
            "hit_rate": round(hit_rate, 2),
            "total_keys": total_keys,
            "expired_keys": 0,  # Redis不直接提供此信息
            "commands_processed": self._stats['commands_processed'],
            "local_hits": self._stats['cache_hits'],
            "local_misses": self._stats['cache_misses']
        }
    
    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的所有键"""
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.client.delete(*keys)
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"删除模式键错误: {e}")
            return 0

# 全局Redis管理器实例
redis_manager = RedisManager()

async def get_redis_client() -> redis.Redis:
    """获取Redis客户端"""
    if redis_manager.client is None:
        await redis_manager.init_redis()
    return redis_manager.client

async def init_redis():
    """初始化Redis连接"""
    await redis_manager.init_redis()

async def close_redis():
    """关闭Redis连接"""
    await redis_manager.close_redis()
```

### 2. 缓存策略管理

#### 文件: `app/cache/cache_manager.py`
```python
from typing import Any, Optional, Callable
import hashlib
import json
from app.cache.redis_client import redis_manager

class CacheManager:
    def __init__(self):
        self.default_expire = 3600  # 1小时
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 创建唯一的键标识
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_hash = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    async def cached(self, key: str, func: Callable, expire: Optional[int] = None, force_refresh: bool = False) -> Any:
        """通用缓存装饰器逻辑"""
        if not force_refresh:
            # 先尝试从缓存获取
            cached_data = await redis_manager.get(key)
            if cached_data is not None:
                return cached_data
        
        # 缓存未命中，执行函数并缓存结果
        result = await func() if callable(func) else func
        
        if result is not None:
            await redis_manager.set(key, result, expire or self.default_expire)
        
        return result
    
    async def invalidate(self, pattern: str) -> int:
        """删除缓存"""
        return await redis_manager.delete_pattern(pattern)
    
    async def warmup_cache(self, modules: list) -> dict:
        """缓存预热"""
        warmed_keys = 0
        start_time = time.time()
        
        for module in modules:
            if module == "products":
                warmed_keys += await self._warmup_products()
            elif module == "categories":
                warmed_keys += await self._warmup_categories()
        
        duration = time.time() - start_time
        
        return {
            "warmed_keys": warmed_keys,
            "duration": f"{duration:.1f}s",
            "modules": modules
        }
    
    async def _warmup_products(self) -> int:
        """预热商品缓存"""
        # 这里实现商品缓存预热逻辑
        # 例如：预加载热门商品、分类等
        return 50  # 示例返回值
    
    async def _warmup_categories(self) -> int:
        """预热分类缓存"""
        # 这里实现分类缓存预热逻辑
        return 30  # 示例返回值

# 全局缓存管理器实例
cache_manager = CacheManager()
```

### 3. API路由实现

#### 文件: `app/api/cache_routes.py`
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.core.auth import get_admin_user
from app.cache.redis_client import redis_manager
from app.cache.cache_manager import cache_manager

router = APIRouter(prefix="/api/v1/cache", tags=["缓存管理"])

class ClearCacheRequest(BaseModel):
    pattern: str
    confirm: bool

class WarmupCacheRequest(BaseModel):
    modules: List[str]
    force: bool = False

@router.get("/status")
async def get_cache_status(admin_user=Depends(get_admin_user)):
    """获取缓存状态"""
    try:
        redis_info = await redis_manager.get_redis_info()
        cache_stats = await redis_manager.get_cache_stats()
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "redis_info": redis_info,
                "cache_stats": cache_stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存状态失败: {str(e)}")

@router.get("/metrics")
async def get_cache_metrics(
    time_range: str = "1h",
    admin_user=Depends(get_admin_user)
):
    """获取缓存性能指标"""
    try:
        redis_info = await redis_manager.get_redis_info()
        cache_stats = await redis_manager.get_cache_stats()
        
        # 模拟键分布统计（实际实现需要遍历Redis键）
        key_distribution = {
            "user_sessions": 450,
            "shopping_carts": 320,
            "product_cache": 280,
            "other": 200
        }
        
        return {
            "success": True,
            "data": {
                "time_range": time_range,
                "performance": {
                    "commands_processed": cache_stats["commands_processed"],
                    "hit_rate": cache_stats["hit_rate"],
                    "miss_rate": round(100 - cache_stats["hit_rate"], 2),
                    "avg_response_time": 0.5,  # 示例值
                    "peak_memory": redis_info.get("memory_peak", "0B")
                },
                "key_distribution": key_distribution
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存指标失败: {str(e)}")

@router.delete("/keys")
async def clear_cache(
    request: ClearCacheRequest,
    admin_user=Depends(get_admin_user)
):
    """清除缓存"""
    if not request.confirm:
        raise HTTPException(status_code=400, detail="必须确认清除操作")
    
    try:
        deleted_keys = await redis_manager.delete_pattern(request.pattern)
        
        return {
            "success": True,
            "message": "缓存清除成功",
            "data": {
                "deleted_keys": deleted_keys,
                "pattern": request.pattern
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")

@router.post("/warmup")
async def warmup_cache(
    request: WarmupCacheRequest,
    admin_user=Depends(get_admin_user)
):
    """缓存预热"""
    try:
        result = await cache_manager.warmup_cache(request.modules)
        
        return {
            "success": True,
            "message": "缓存预热完成",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"缓存预热失败: {str(e)}")
```

## 缓存策略

### 会话缓存策略
```python
# app/cache/strategies/session_cache.py
class SessionCacheStrategy:
    def __init__(self):
        self.prefix = "session"
        self.expire = 86400  # 24小时
    
    async def get_user_session(self, session_id: str):
        """获取用户会话"""
        key = f"{self.prefix}:{session_id}"
        return await redis_manager.get(key)
    
    async def set_user_session(self, session_id: str, session_data: dict):
        """设置用户会话"""
        key = f"{self.prefix}:{session_id}"
        await redis_manager.set(key, session_data, self.expire)
```

### 购物车缓存策略
```python
# app/cache/strategies/cart_cache.py
class CartCacheStrategy:
    def __init__(self):
        self.prefix = "cart"
        self.expire = 604800  # 7天
    
    async def get_user_cart(self, user_id: int):
        """获取用户购物车"""
        key = f"{self.prefix}:user:{user_id}"
        return await redis_manager.get(key)
    
    async def set_user_cart(self, user_id: int, cart_data: dict):
        """设置用户购物车"""
        key = f"{self.prefix}:user:{user_id}"
        await redis_manager.set(key, cart_data, self.expire)
```