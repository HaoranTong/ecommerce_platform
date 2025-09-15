"""
文件名：__init__.py
文件路径：app/modules/inventory_management/__init__.py
功能描述：库存管理模块包初始化文件

主要功能：
- 定义库存管理模块的对外接口
- 导出模块核心组件供其他模块使用
- 管理模块内部依赖关系

使用说明：
- 导入模块：from app.modules import inventory_management
- 导入路由：from app.modules.inventory_management import router
- 导入服务：from app.modules.inventory_management import service

导出组件：
- router: FastAPI路由组件
- service: 业务逻辑服务
- models: 数据模型
- schemas: API数据模型

创建时间：2025-09-15
最后修改：2025-09-15
"""

from .router import router
from .service import InventoryService
from . import models, schemas

__all__ = [
    "router",
    "InventoryService", 
    "models",
    "schemas"
]