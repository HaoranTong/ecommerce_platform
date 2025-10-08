"""
异步工具函数模块

功能描述：提供同步函数到异步函数的转换工具，解决在async context中调用同步数据库操作的阻塞问题

核心问题：
- FastAPI的async endpoint期望所有操作都是非阻塞的
- SQLAlchemy同步ORM的db.query()是阻塞调用
- 在async context中调用阻塞IO会阻塞整个事件循环

解决方案：
- 使用 asyncio.run_in_executor 将同步数据库操作放到线程池执行
- 避免阻塞事件循环，保持async的并发优势

使用场景：
- Service层需要在async方法中调用同步Repository方法
- Router层async endpoint调用同步业务逻辑

技术说明：
- run_in_executor使用默认ThreadPoolExecutor（线程池）
- 线程池大小由Python自动管理（默认：min(32, os.cpu_count() + 4)）
- 每个同步调用在独立线程中执行，不阻塞事件循环

性能考虑：
- 线程切换有小开销，但远好于阻塞事件循环
- 适合中等并发场景（<1000 req/s）
- 高并发场景建议升级为全async（AsyncSession + aiomysql）

使用示例：
    # Service层调用同步Repository
    from app.core.async_utils import run_in_thread
    
    async def login_user(db: Session, username: str):
        # 同步数据库操作通过线程池执行
        user = await run_in_thread(
            UserRepository.get_by_username, 
            db, username
        )
        
        # Redis操作仍是真正的async
        await VerificationCodeService.verify_code(...)
        
        return user

依赖模块：
- asyncio: 事件循环和线程池管理
- functools: 装饰器工具
- typing: 类型注解
"""

import asyncio
from functools import wraps, partial
from typing import Any, Callable, TypeVar

T = TypeVar('T')


async def run_in_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    在线程池中运行同步函数，避免阻塞事件循环
    
    此函数将同步的阻塞操作（如数据库查询）放到线程池中执行，
    使async endpoint不会阻塞事件循环，保持异步并发能力。
    
    Args:
        func: 要执行的同步函数
        *args: 位置参数
        **kwargs: 关键字参数
    
    Returns:
        函数执行结果
    
    Example:
        >>> async def get_user(db: Session, user_id: int):
        ...     # 同步Repository方法通过线程池执行
        ...     user = await run_in_thread(UserRepository.get_by_id, db, user_id)
        ...     return user
    
    Note:
        - 使用默认线程池（ThreadPoolExecutor）
        - 线程池大小由Python自动管理
        - 适合IO密集型操作（数据库查询）
        - 不适合CPU密集型操作（应使用ProcessPoolExecutor）
    """
    loop = asyncio.get_event_loop()
    
    # 如果有kwargs，使用partial包装函数
    if kwargs:
        func = partial(func, **kwargs)
        return await loop.run_in_executor(None, func, *args)
    else:
        return await loop.run_in_executor(None, func, *args)


def sync_to_async(func: Callable[..., T]) -> Callable[..., Any]:
    """
    装饰器：将同步函数包装为async函数（通过线程池执行）
    
    此装饰器可以将Repository层的同步方法包装为async方法，
    使其可以在Service层的async方法中安全调用。
    
    Args:
        func: 要包装的同步函数
    
    Returns:
        包装后的async函数
    
    Example:
        >>> class UserRepository:
        ...     @staticmethod
        ...     @sync_to_async
        ...     def get_by_id(db: Session, user_id: int) -> User:
        ...         return db.query(User).filter(User.id == user_id).first()
        ...
        >>> # 现在可以在async context中调用
        >>> async def service_method(db: Session):
        ...     user = await UserRepository.get_by_id(db, 1)  # 不阻塞事件循环
    
    Note:
        - 推荐在Repository层使用此装饰器
        - 被装饰的方法会在线程池中执行
        - 原函数签名保持不变（除了变成async）
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        return await run_in_thread(func, *args, **kwargs)
    return wrapper


class AsyncDBMixin:
    """
    异步数据库操作Mixin类（可选）
    
    为Repository类提供async包装方法，统一管理同步到异步的转换。
    
    使用方式：
        class UserRepository(AsyncDBMixin):
            @staticmethod
            def _get_by_id_sync(db: Session, user_id: int):
                return db.query(User).filter(User.id == user_id).first()
            
            # 自动生成async包装
            get_by_id = AsyncDBMixin.wrap_sync(_get_by_id_sync)
    """
    
    @staticmethod
    def wrap_sync(func: Callable[..., T]) -> Callable[..., Any]:
        """
        包装同步方法为async方法
        
        Args:
            func: 同步方法
        
        Returns:
            async方法
        """
        return sync_to_async(func)


# 便捷函数别名
async_wrap = sync_to_async  # 更简短的别名
run_sync = run_in_thread    # 更直观的名称


__all__ = [
    'run_in_thread',
    'sync_to_async',
    'AsyncDBMixin',
    'async_wrap',
    'run_sync',
]
