<!--
文档说明：
- 内容：应用核心模块API接口实现细节，包含具体的代码实现方案和技术细节
- 使用方法：开发人员实现应用核心功能时的详细指导文档
- 更新方法：代码实现变更时同步更新，记录实际的实现方案
- 引用关系：基于api-spec.md接口规范，被开发团队使用
- 更新频率：代码实现变更时
-->

# 应用核心模块API实现细节

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## 实现架构

### 核心文件结构
```
app/
├── main.py                 # FastAPI应用入口
├── core/
│   ├── __init__.py
│   ├── app_factory.py      # 应用工厂模式
│   ├── lifespan.py         # 生命周期管理
│   └── health_check.py     # 健康检查实现
├── api/
│   └── system_routes.py    # 系统级API路由
└── middleware/
    └── health_middleware.py # 健康检查中间件
```

## API实现细节

### 1. 健康检查实现

#### 文件: `app/core/health_check.py`
```python
from typing import Dict, Any
import time
import psutil
from sqlalchemy import text
from app.database.connection import get_db_engine
from app.cache.redis_client import get_redis_client

class HealthChecker:
    def __init__(self):
        self.start_time = time.time()
    
    async def check_application_health(self) -> Dict[str, Any]:
        """应用整体健康检查"""
        checks = {
            "database": await self._check_database(),
            "redis": await self._check_redis(),
            "external_services": await self._check_external_services()
        }
        
        overall_status = "healthy" if all(
            check == "healthy" for check in checks.values()
        ) else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "uptime": int(time.time() - self.start_time),
            "checks": checks
        }
    
    async def _check_database(self) -> str:
        """检查数据库连接"""
        try:
            engine = get_db_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return "healthy" if result.fetchone() else "unhealthy"
        except Exception:
            return "unhealthy"
    
    async def _check_redis(self) -> str:
        """检查Redis连接"""
        try:
            redis_client = get_redis_client()
            await redis_client.ping()
            return "healthy"
        except Exception:
            return "unhealthy"
    
    async def _check_external_services(self) -> str:
        """检查外部服务"""
        # 检查支付服务、短信服务等外部依赖
        return "healthy"  # 简化实现

    async def get_detailed_health(self) -> Dict[str, Any]:
        """获取详细健康状态"""
        db_stats = await self._get_database_stats()
        redis_stats = await self._get_redis_stats()
        system_stats = self._get_system_stats()
        
        return {
            "status": "healthy",
            "components": {
                "database": db_stats,
                "redis": redis_stats,
                "system": system_stats
            }
        }
    
    async def _get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            engine = get_db_engine()
            pool = engine.pool
            
            # 测量响应时间
            start_time = time.time()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time": round(response_time, 2),
                "connection_pool": {
                    "active": pool.checkedout(),
                    "idle": pool.checkedin(),
                    "max": pool.size()
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _get_redis_stats(self) -> Dict[str, Any]:
        """获取Redis统计信息"""
        try:
            redis_client = get_redis_client()
            
            # 测量响应时间
            start_time = time.time()
            await redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            # 获取内存使用情况
            info = await redis_client.info('memory')
            memory_usage = info.get('used_memory_human', 'unknown')
            
            return {
                "status": "healthy",
                "response_time": round(response_time, 2),
                "memory_usage": memory_usage
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        disk_usage = psutil.disk_usage('/')
        memory = psutil.virtual_memory()
        
        return {
            "disk_space": {
                "status": "healthy" if disk_usage.percent < 90 else "warning",
                "available": f"{100 - disk_usage.percent:.1f}%",
                "used": f"{disk_usage.percent:.1f}%"
            },
            "memory": {
                "status": "healthy" if memory.percent < 85 else "warning",
                "available": f"{100 - memory.percent:.1f}%",
                "used": f"{memory.percent:.1f}%"
            }
        }
```

#### 文件: `app/api/system_routes.py`
```python
from fastapi import APIRouter, HTTPException, Depends
from app.core.health_check import HealthChecker
from app.core.auth import get_admin_user
from app.core.config import get_app_info

router = APIRouter(prefix="/api", tags=["系统管理"])
health_checker = HealthChecker()

@router.get("/health")
async def health_check():
    """应用健康检查"""
    health_data = await health_checker.check_application_health()
    
    status_code = 200 if health_data["status"] == "healthy" else 503
    
    return {
        "success": health_data["status"] == "healthy",
        "data": health_data
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """详细健康检查"""
    detailed_health = await health_checker.get_detailed_health()
    
    return {
        "success": True,
        "data": detailed_health
    }

@router.get("/info")
async def application_info():
    """获取应用信息"""
    app_info = get_app_info()
    
    return {
        "success": True,
        "data": app_info
    }

@router.get("/routes")
async def list_routes(app: FastAPI = Depends(get_current_app)):
    """获取路由信息（仅开发环境）"""
    if not get_settings().debug:
        raise HTTPException(status_code=404, detail="Not found")
    
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "module": getattr(route, 'tags', ['unknown'])[0] if route.tags else 'unknown'
            })
    
    return {
        "success": True,
        "data": {
            "total_routes": len(routes),
            "routes": routes
        }
    }

@router.post("/admin/restart")
async def restart_application(admin_user=Depends(get_admin_user)):
    """重启应用（管理员权限）"""
    # 这里实现应用重启逻辑
    # 在生产环境中通常通过信号量或外部工具实现
    
    import signal
    import os
    
    # 发送重启信号
    os.kill(os.getpid(), signal.SIGUSR1)
    
    return {
        "success": True,
        "message": "应用重启指令已发送",
        "data": {
            "restart_time": time.time()
        }
    }

@router.post("/admin/reload-config")
async def reload_configuration(admin_user=Depends(get_admin_user)):
    """重新加载配置（管理员权限）"""
    from app.core.config import reload_settings
    
    changed_configs = reload_settings()
    
    return {
        "success": True,
        "message": "配置重载成功",
        "data": {
            "reload_time": time.time(),
            "changed_configs": changed_configs
        }
    }
```

### 2. 应用生命周期管理

#### 文件: `app/core/lifespan.py`
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.connection import init_database, close_database
from app.cache.redis_client import init_redis, close_redis
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()
    
    # 启动时执行
    logger.info("应用正在启动...")
    
    try:
        # 初始化数据库连接
        await init_database()
        logger.info("数据库连接初始化完成")
        
        # 初始化Redis连接
        await init_redis()
        logger.info("Redis连接初始化完成")
        
        # 在开发环境中创建数据库表
        if settings.environment == "development":
            from app.database.models import create_tables
            await create_tables()
            logger.info("开发环境：数据库表创建完成")
        
        logger.info("应用启动完成")
        
        yield  # 应用运行期间
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise
    
    finally:
        # 关闭时执行
        logger.info("应用正在关闭...")
        
        try:
            await close_redis()
            logger.info("Redis连接已关闭")
            
            await close_database()
            logger.info("数据库连接已关闭")
            
        except Exception as e:
            logger.error(f"应用关闭时出错: {e}")
        
        logger.info("应用关闭完成")
```

### 3. 应用工厂模式

#### 文件: `app/core/app_factory.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.lifespan import lifespan
from app.core.config import get_settings
from app.middleware.health_middleware import HealthCheckMiddleware
import logging

def create_application() -> FastAPI:
    """创建FastAPI应用实例"""
    settings = get_settings()
    
    # 创建FastAPI应用
    app = FastAPI(
        title="电商平台API",
        description="支持农产品销售的电商平台",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加健康检查中间件
    app.add_middleware(HealthCheckMiddleware)
    
    # 注册路由
    _register_routes(app)
    
    # 配置日志
    _configure_logging(settings)
    
    return app

def _register_routes(app: FastAPI):
    """注册所有路由模块"""
    from app.api.system_routes import router as system_router
    from app.api.user_routes import router as user_router
    from app.api.product_routes import router as product_router
    from app.api.cart_routes import router as cart_router
    from app.api.order_routes import router as order_router
    
    # 系统路由
    app.include_router(system_router)
    
    # 业务路由
    app.include_router(user_router, prefix="/api/v1")
    app.include_router(product_router, prefix="/api/v1")
    app.include_router(cart_router, prefix="/api/v1")
    app.include_router(order_router, prefix="/api/v1")

def _configure_logging(settings):
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO if settings.debug else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
```

## 部署配置

### Docker配置
```dockerfile
# 健康检查配置
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# 优雅关闭配置
STOPSIGNAL SIGTERM
```

### Kubernetes配置
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ecommerce-api
spec:
  selector:
    app: ecommerce-api
  ports:
  - port: 8000
    targetPort: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecommerce-api
  template:
    metadata:
      labels:
        app: ecommerce-api
    spec:
      containers:
      - name: api
        image: ecommerce-api:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 监控集成

### Prometheus指标
```python
# 在health_check.py中添加指标收集
from prometheus_client import Counter, Histogram, Gauge

# 定义指标
health_check_counter = Counter('health_check_total', 'Health check requests')
health_check_duration = Histogram('health_check_duration_seconds', 'Health check duration')
database_connections = Gauge('database_connections_active', 'Active database connections')

class HealthChecker:
    @health_check_duration.time()
    async def check_application_health(self):
        health_check_counter.inc()
        # ... 原有实现
```

### 日志结构化
```python
# 使用结构化日志
import structlog

logger = structlog.get_logger()

# 在health_check.py中使用
logger.info("health_check_completed", 
           status=overall_status, 
           response_time=response_time,
           timestamp=time.time())
```
