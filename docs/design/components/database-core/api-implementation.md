<!--
文档说明：
- 内容：数据库核心模块API接口实现细节，包含SQLAlchemy连接池管理的具体实现
- 使用方法：开发人员实现数据库连接功能时的详细指导文档
- 更新方法：数据库实现代码变更时同步更新，记录实际的实现方案
- 引用关系：基于api-spec.md接口规范，被数据访问层开发使用
- 更新频率：数据库代码实现变更时
-->

# 数据库核心模块API实现细节

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## 实现架构

### 核心文件结构
```
app/database/
├── __init__.py
├── connection.py           # 数据库连接管理
├── session.py             # 会话管理
├── transaction.py         # 事务处理
├── monitoring.py          # 数据库监控
└── migrations/
    ├── __init__.py
    └── versions/           # Alembic迁移文件
```

## 核心实现

### 1. 数据库连接管理

#### 文件: `app/database/connection.py`
```python
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from app.core.config import get_settings
import logging
import time

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.settings = get_settings()
        self._connection_stats = {
            'total_queries': 0,
            'slow_queries': [],
            'error_count': 0,
            'start_time': time.time()
        }
    
    def create_engine(self) -> Engine:
        """创建数据库引擎"""
        database_url = self.settings.database_url
        
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=5,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=self.settings.debug,
            future=True
        )
        
        # 注册事件监听器
        self._register_event_listeners(engine)
        
        self.engine = engine
        return engine
    
    def _register_event_listeners(self, engine: Engine):
        """注册数据库事件监听器"""
        
        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - context._query_start_time
            
            # 统计查询次数
            self._connection_stats['total_queries'] += 1
            
            # 记录慢查询（超过100ms）
            if total_time > 0.1:
                self._connection_stats['slow_queries'].append({
                    'query': statement[:200] + '...' if len(statement) > 200 else statement,
                    'duration': round(total_time * 1000, 2),
                    'timestamp': time.time()
                })
                
                # 只保留最近50条慢查询
                if len(self._connection_stats['slow_queries']) > 50:
                    self._connection_stats['slow_queries'].pop(0)
        
        @event.listens_for(engine, "handle_error")
        def handle_error(exception_context):
            self._connection_stats['error_count'] += 1
            logger.error(f"数据库错误: {exception_context.original_exception}")
    
    def get_connection_status(self) -> dict:
        """获取连接状态"""
        if not self.engine:
            return {"status": "not_initialized"}
        
        pool = self.engine.pool
        
        return {
            "status": "healthy",
            "connection_pool": {
                "total_connections": pool.size(),
                "active_connections": pool.checkedout(),
                "idle_connections": pool.checkedin(),
                "pool_size": pool.size(),
                "max_overflow": pool._max_overflow
            },
            "performance": {
                "avg_query_time": self._calculate_avg_query_time(),
                "slow_queries": len(self._connection_stats['slow_queries']),
                "total_queries": self._connection_stats['total_queries'],
                "error_count": self._connection_stats['error_count']
            }
        }
    
    def get_performance_metrics(self, time_range: str = "1h") -> dict:
        """获取性能指标"""
        return {
            "time_range": time_range,
            "metrics": {
                "query_count": self._connection_stats['total_queries'],
                "avg_response_time": self._calculate_avg_query_time(),
                "max_response_time": max(
                    [q['duration'] for q in self._connection_stats['slow_queries']], 
                    default=0
                ),
                "error_count": self._connection_stats['error_count'],
                "cache_hit_rate": 85.2  # 示例值，实际需要从数据库获取
            },
            "slow_queries": self._connection_stats['slow_queries'][-10:]  # 最近10条
        }
    
    def _calculate_avg_query_time(self) -> float:
        """计算平均查询时间"""
        if not self._connection_stats['slow_queries']:
            return 0.0
        
        total_time = sum(q['duration'] for q in self._connection_stats['slow_queries'])
        return round(total_time / len(self._connection_stats['slow_queries']), 2)
    
    def refresh_connection_pool(self) -> dict:
        """刷新连接池"""
        if not self.engine:
            raise Exception("数据库引擎未初始化")
        
        old_connections = self.engine.pool.checkedout() + self.engine.pool.checkedin()
        
        # 重新创建连接池
        self.engine.dispose()
        self.engine = self.create_engine()
        
        new_connections = self.engine.pool.size()
        
        return {
            "refresh_time": time.time(),
            "old_connections": old_connections,
            "new_connections": new_connections
        }

# 全局数据库管理器实例
db_manager = DatabaseManager()

def get_db_engine() -> Engine:
    """获取数据库引擎"""
    if db_manager.engine is None:
        db_manager.create_engine()
    return db_manager.engine

async def init_database():
    """初始化数据库连接"""
    logger.info("初始化数据库连接...")
    engine = get_db_engine()
    
    # 测试连接
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    
    logger.info("数据库连接初始化完成")

async def close_database():
    """关闭数据库连接"""
    if db_manager.engine:
        db_manager.engine.dispose()
        logger.info("数据库连接已关闭")
```

### 2. API路由实现

#### 文件: `app/api/database_routes.py`
```python
from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.auth import get_admin_user
from app.database.connection import db_manager
from app.database.migrations import migration_manager
import logging

router = APIRouter(prefix="/api/v1/database", tags=["数据库管理"])
logger = logging.getLogger(__name__)

@router.get("/status")
async def get_database_status(admin_user=Depends(get_admin_user)):
    """获取数据库连接状态"""
    try:
        status = db_manager.get_connection_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"获取数据库状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取数据库状态失败")

@router.get("/metrics")
async def get_database_metrics(
    time_range: str = Query("1h", regex="^(1h|24h|7d)$"),
    admin_user=Depends(get_admin_user)
):
    """获取数据库性能指标"""
    try:
        metrics = db_manager.get_performance_metrics(time_range)
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        logger.error(f"获取数据库性能指标失败: {e}")
        raise HTTPException(status_code=500, detail="获取性能指标失败")

@router.post("/pool/refresh")
async def refresh_connection_pool(admin_user=Depends(get_admin_user)):
    """刷新数据库连接池"""
    try:
        result = db_manager.refresh_connection_pool()
        return {
            "success": True,
            "message": "连接池刷新成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"刷新连接池失败: {e}")
        raise HTTPException(status_code=500, detail="刷新连接池失败")

@router.get("/migrations")
async def get_migration_status(admin_user=Depends(get_admin_user)):
    """获取数据库迁移状态"""
    try:
        status = migration_manager.get_migration_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"获取迁移状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取迁移状态失败")
```

### 3. 会话管理

#### 文件: `app/database/session.py`
```python
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.database.connection import get_db_engine
import logging

logger = logging.getLogger(__name__)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

def get_db_session() -> Session:
    """获取数据库会话"""
    engine = get_db_engine()
    SessionLocal.configure(bind=engine)
    return SessionLocal()

@contextmanager
def get_db_transaction():
    """数据库事务上下文管理器"""
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"数据库事务回滚: {e}")
        raise
    finally:
        session.close()

async def get_async_db_session():
    """异步获取数据库会话（用于FastAPI依赖注入）"""
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()
```

## 配置和优化

### 数据库配置优化
```python
# app/core/config.py 中的数据库配置
class Settings:
    # 数据库连接配置
    database_url: str = "mysql+pymysql://user:password@localhost/ecommerce"
    
    # 连接池配置
    db_pool_size: int = 10          # 连接池大小
    db_max_overflow: int = 5        # 最大溢出连接数
    db_pool_timeout: int = 30       # 连接超时时间
    db_pool_recycle: int = 3600     # 连接回收时间（秒）
    
    # 查询优化配置
    db_echo: bool = False           # 是否输出SQL日志
    db_echo_pool: bool = False      # 是否输出连接池日志
```

### 监控集成
```python
# 集成Prometheus监控
from prometheus_client import Counter, Histogram, Gauge

# 定义监控指标
db_query_counter = Counter('database_queries_total', 'Database queries')
db_query_duration = Histogram('database_query_duration_seconds', 'Query duration')
db_connections_gauge = Gauge('database_connections_active', 'Active connections')

# 在connection.py中使用
@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    db_query_counter.inc()
    duration = time.time() - context._query_start_time
    db_query_duration.observe(duration)
```
