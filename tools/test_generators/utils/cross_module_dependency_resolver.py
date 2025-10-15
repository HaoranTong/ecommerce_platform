"""
跨模块依赖解析工具（ModelAnalyzer的门面）

作为ModelAnalyzer的便捷接口，提供：
1. 跨模块依赖检测
2. Factory导入语句生成
3. 依赖树解析（包括传递依赖）

设计原则：
- 不再直接扫描模型，所有信息委托给ModelAnalyzer
- 保持职责单一：只做依赖判断和Factory生成
- 作为"门面"模式，简化其他生成器的使用

使用示例：
    resolver = CrossModuleDependencyResolver()
    
    # 检测是否为跨模块依赖
    is_cross = resolver.is_cross_module_dependency('Product', 'shopping_cart')
    
    # 获取模型所属模块（委托给ModelAnalyzer）
    module = resolver.get_module_for_model('SKU')  # 返回 'product_catalog'
    
    # 通过表名查找模型（委托给ModelAnalyzer）
    model = resolver.get_model_by_table('product_skus')  # 返回 'SKU'
    
    # 生成Factory导入语句
    import_stmt = resolver.get_factory_import('Product', 'product_catalog')
    # 返回: 'from tests.factories.product_catalog_factories import ProductFactory'

创建时间：2025-10-14
最后修改：2025-10-15（重构为ModelAnalyzer门面）
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class CrossModuleDependencyResolver:
    """跨模块依赖解析工具（ModelAnalyzer的门面）
    
    职责：
    - 判断依赖关系（is_cross_module_dependency）
    - 生成Factory导入语句（get_factory_import）
    - 提供便捷查询接口（委托给ModelAnalyzer）
    
    注意：本类不再直接扫描模型，所有信息来自ModelAnalyzer
    
    Attributes:
        model_analyzer: ModelAnalyzer实例，提供所有模型信息
        project_root: 项目根目录路径
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """初始化依赖解析器
        
        Args:
            project_root: 项目根目录路径，默认为当前文件的祖父目录
        """
        if project_root is None:
            # 默认为 tools/test_generators/utils -> tools -> project_root
            project_root = Path(__file__).parent.parent.parent.parent
        
        self.project_root = Path(project_root)
        
        # 使用ModelAnalyzer作为唯一信息来源
        from .model_analyzer import ModelAnalyzer
        self.model_analyzer = ModelAnalyzer(self.project_root)
        
        # 初始化时进行全局分析
        self.model_analyzer.analyze_all_modules()
    

    
    def get_module_for_model(self, model_name: str) -> Optional[str]:
        """获取模型所属的模块名称（委托给ModelAnalyzer）
        
        Args:
            model_name: 模型类名，如 'Product', 'User', 'SKU'
            
        Returns:
            模块名称，如 'product_catalog', 'user_auth'，如果未找到返回None
        """
        return self.model_analyzer.get_module_for_model(model_name)
    
    def get_model_by_table(self, table_name: str) -> Optional[str]:
        """通过表名获取模型名称（委托给ModelAnalyzer）
        
        Args:
            table_name: 表名，如 'product_skus', 'users'
            
        Returns:
            模型名称，如 'SKU', 'User'，如果未找到返回None
        """
        return self.model_analyzer.get_model_by_table(table_name)
    
    def is_cross_module_dependency(self, model_name: str, current_module: str) -> bool:
        """检测外键是否为跨模块依赖
        
        判断外键引用的模型是否属于当前模块。
        
        Args:
            model_name: 外键模型名称
            current_module: 当前模块名称
            
        Returns:
            True表示跨模块依赖，False表示模块内依赖
        """
        target_module = self.get_module_for_model(model_name)
        
        if target_module is None:
            # 如果找不到模型所属模块，假设为跨模块依赖（保守处理）
            return True
        
        return target_module != current_module
    
    def get_factory_import(self, model_name: str, target_module: Optional[str] = None) -> str:
        """生成Factory导入语句
        
        Args:
            model_name: 模型类名
            target_module: 目标模块名（可选，如果不提供则自动查找）
            
        Returns:
            Factory导入语句，如:
            'from tests.factories.product_catalog_factories import ProductFactory'
        """
        if target_module is None:
            target_module = self.get_module_for_model(model_name)
        
        if target_module is None:
            return f'# TODO: 未找到模型 {model_name} 所属模块'
        
        factory_name = f"{model_name}Factory"
        return f"from tests.factories.{target_module}_factories import {factory_name}"
    
    def get_factory_manager_import(self, module_name: str) -> str:
        """生成FactoryManager导入语句
        
        Args:
            module_name: 模块名称
            
        Returns:
            FactoryManager导入语句
        """
        manager_name = ''.join(word.capitalize() for word in module_name.split('_')) + 'FactoryManager'
        return f"from tests.factories.{module_name}_factories import {manager_name}"
    
    def get_all_models(self) -> Dict[str, str]:
        """获取所有模型的映射表
        
        Returns:
            {模型名: 模块名} 字典
        """
        return self.model_to_module.copy()
    
    def print_mapping_table(self) -> None:
        """打印模型→模块映射表（用于调试）"""
        print("\n📋 模型→模块映射表:")
        print("=" * 50)
        for model_name in sorted(self.model_to_module.keys()):
            module_name = self.model_to_module[model_name]
            print(f"  {model_name:<20} → {module_name}")
        print("=" * 50)
        print(f"✅ 共识别 {len(self.model_to_module)} 个模型\n")


# 全局单例实例（延迟初始化）
_resolver_instance: Optional[CrossModuleDependencyResolver] = None


def get_resolver(project_root: Optional[Path] = None) -> CrossModuleDependencyResolver:
    """获取全局依赖解析器单例
    
    Args:
        project_root: 项目根目录（仅首次调用时需要）
        
    Returns:
        CrossModuleDependencyResolver实例
    """
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = CrossModuleDependencyResolver(project_root)
    return _resolver_instance


if __name__ == "__main__":
    # 测试代码
    print("🔍 测试跨模块依赖解析器\n")
    
    resolver = CrossModuleDependencyResolver()
    
    # 打印映射表
    resolver.print_mapping_table()
    
    # 测试几个常见场景
    test_cases = [
        ('Product', 'product_catalog', False),  # 同模块
        ('Product', 'shopping_cart', True),     # 跨模块
        ('User', 'user_auth', False),           # 同模块
        ('User', 'order_management', True),     # 跨模块
        ('SKU', 'product_catalog', False),      # 同模块
        ('SKU', 'shopping_cart', True),         # 跨模块
    ]
    
    print("\n🧪 测试跨模块依赖检测:")
    print("=" * 70)
    for model_name, current_module, expected in test_cases:
        result = resolver.is_cross_module_dependency(model_name, current_module)
        status = "✅" if result == expected else "❌"
        print(f"{status} {model_name:15} in {current_module:20} → {'跨模块' if result else '同模块'}")
    
    print("\n📦 测试Factory导入生成:")
    print("=" * 70)
    test_models = ['Product', 'User', 'SKU', 'Cart', 'Order']
    for model_name in test_models:
        import_stmt = resolver.get_factory_import(model_name)
        print(f"  {import_stmt}")
