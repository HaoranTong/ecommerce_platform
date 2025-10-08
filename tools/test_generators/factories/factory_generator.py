"""
Factory生成器 - 测试数据工厂类

职责：
生成Factory Boy工厂类代码，包括：
1. 标准测试数据工厂
2. 模块专用工厂
3. 关联关系处理
4. 懒惰属性和序列

双工厂架构：
- StandardTestDataFactory: 通用标准工厂（所有模块）
- 模块专用Factory: 特定业务场景（可选）

版本: v1.0
创建时间: 2025-10-08
"""
from pathlib import Path
from typing import Dict, List
from ..core import ModelInfo, FieldInfo


class FactoryGenerator:
    """Factory Boy工厂类生成器"""
    
    def __init__(self, project_root: Path, config: Dict, main_generator=None):
        """初始化生成器
        
        Args:
            project_root: 项目根目录
            config: 配置字典
            main_generator: 主生成器实例（临时使用）
        """
        self.project_root = project_root
        self.config = config
        self.main_generator = main_generator
    
    def generate_factories(
        self,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Factory类代码（主入口）
        
        Args:
            module_name: 模块名称
            models: 模型信息字典
            
        Returns:
            生成的Factory代码字符串
        """
        # 🔄 重构标记：待从主程序迁移实现
        # 主程序方法：_generate_factories() 第5472行
        # 预计代码量：~900行
        # 包含：
        # - _generate_factory_imports()
        # - _generate_factory_class()
        # - _generate_factory_fields()
        # - _generate_factory_relationships()
        # - _generate_lazy_attributes()
        # - _generate_sequences()
        if self.main_generator:
            return self.main_generator._generate_factories(module_name, models)
        return f"# Factory占位符 - {module_name}"
