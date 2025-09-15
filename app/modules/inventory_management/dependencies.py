"""
文件名：dependencies.py
文件路径：app/modules/inventory_management/dependencies.py
功能描述：库存管理模块的依赖注入定义

主要功能：
- 定义库存管理模块的依赖注入组件
- 提供服务层实例化和缓存
- 管理模块间的依赖关系

使用说明：
- 导入：from app.modules.inventory_management.dependencies import get_inventory_service
- FastAPI依赖：inventory_service: InventoryService = Depends(get_inventory_service)
- 自动注入：依赖会自动注入到API路由中

依赖模块：
- app.modules.inventory_management.service.InventoryService: 库存服务类
- app.core.database: 数据库会话管理
- fastapi.Depends: FastAPI依赖注入装饰器

创建时间：2025-09-15
最后修改：2025-09-15
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from .service import InventoryService


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """
    获取库存管理服务实例
    
    Args:
        db (Session): 数据库会话实例
        
    Returns:
        InventoryService: 库存管理服务实例
        
    Note:
        此依赖会在每次API调用时创建新的服务实例
        服务实例会自动注入数据库会话
    """
    return InventoryService(db)
