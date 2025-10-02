"""
文件名：model_discovery.py  
文件路径：app/core/model_discovery.py
功能描述：动态模型发现和注册系统，支持烟雾测试的自动化表创建
主要功能：
- 自动扫描app/modules目录下的所有models.py文件
- 动态导入所有SQLAlchemy模型类
- 支持增量模块添加，无需修改核心代码
使用说明：
- 在应用启动时调用discover_and_register_models()
- 新增模块时无需修改此文件，自动发现
依赖模块：
- app.core.database: SQLAlchemy Base
"""

import importlib.util
import os
from pathlib import Path
from typing import List, Set

from app.core.database import Base


def discover_module_models() -> List[str]:
    """
    自动发现所有模块的models.py文件
    
    Returns:
        List[str]: 模块models的路径列表
    """
    module_models = []
    modules_dir = Path(__file__).parent.parent / "modules"
    
    if not modules_dir.exists():
        print(f"⚠️  模块目录不存在: {modules_dir}")
        return module_models
    
    # 扫描所有模块目录
    for module_path in modules_dir.iterdir():
        if module_path.is_dir() and not module_path.name.startswith('_'):
            models_file = module_path / "models.py"
            if models_file.exists():
                module_models.append(f"app.modules.{module_path.name}.models")
                print(f"🔍 发现模块models: {module_path.name}")
    
    return module_models


def import_models_dynamically(model_modules: List[str]) -> Set[str]:
    """
    动态导入所有模型模块
    
    Args:
        model_modules: 模块路径列表
        
    Returns:
        Set[str]: 成功导入的模块名称集合
    """
    imported_modules = set()
    
    for module_path in model_modules:
        try:
            # 动态导入模块
            module = importlib.import_module(module_path)
            module_name = module_path.split('.')[-2]  # 提取模块名
            imported_modules.add(module_name)
            print(f"✅ {module_name}模型导入完成")
            
        except ImportError as e:
            print(f"❌ 导入模块失败 {module_path}: {e}")
        except Exception as e:
            print(f"⚠️  模块导入异常 {module_path}: {e}")
    
    return imported_modules


def discover_and_register_models() -> tuple[int, List[str]]:
    """
    发现并注册所有模型，返回统计信息
    
    Returns:
        tuple: (注册表数量, 成功导入的模块列表)
    """
    print("📋 开始自动发现和导入模型...")
    
    # 1. 发现所有模块的models文件
    model_modules = discover_module_models()
    
    if not model_modules:
        print("⚠️  未发现任何模块models文件")
        return 0, []
    
    # 2. 动态导入所有模型
    imported_modules = import_models_dynamically(model_modules)
    
    # 3. 统计注册的表
    table_count = len(Base.metadata.tables)
    table_names = list(Base.metadata.tables.keys())
    
    print(f"🔍 自动发现模块数量: {len(model_modules)}")
    print(f"✅ 成功导入模块数量: {len(imported_modules)}")
    print(f"🔍 注册的表数量: {table_count}")
    print(f"🔍 注册的表: {table_names}")
    
    return table_count, list(imported_modules)


def validate_critical_models() -> bool:
    """
    验证关键模型是否已注册（用于烟雾测试）
    
    Returns:
        bool: 关键模型是否都已注册
    """
    # 定义烟雾测试必需的关键表
    critical_tables = {
        'users',      # 用户认证
        'roles',      # 权限系统
        'products',   # 产品管理
    }
    
    registered_tables = set(Base.metadata.tables.keys())
    missing_tables = critical_tables - registered_tables
    
    if missing_tables:
        print(f"❌ 缺少关键表: {missing_tables}")
        return False
    
    print("✅ 所有关键模型已注册")
    return True