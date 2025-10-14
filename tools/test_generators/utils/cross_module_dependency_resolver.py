"""
跨模块依赖解析工具

提供统一的跨模块依赖检测和Factory导入生成功能，
供Repository测试、API测试、E2E测试等生成器共享。

主要功能：
1. 自动扫描所有模块的models.py，构建模型→模块映射表
2. 检测外键是否为跨模块依赖
3. 生成正确的Factory导入语句
4. 解析依赖树（包括传递依赖）

使用示例：
    resolver = CrossModuleDependencyResolver()
    
    # 检测是否为跨模块依赖
    is_cross = resolver.is_cross_module_dependency('Product', 'shopping_cart')
    
    # 获取模型所属模块
    module = resolver.get_module_for_model('SKU')  # 返回 'product_catalog'
    
    # 生成Factory导入语句
    import_stmt = resolver.get_factory_import('Product', 'product_catalog')
    # 返回: 'from tests.factories.product_catalog_factories import ProductFactory'

创建时间：2025-10-14
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class CrossModuleDependencyResolver:
    """跨模块依赖解析工具
    
    Attributes:
        model_to_module: 模型名称到模块名称的映射 {模型名: 模块名}
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
        self.model_to_module: Dict[str, str] = {}
        self._build_model_module_mapping()
    
    def _build_model_module_mapping(self) -> None:
        """自动扫描所有模块的models.py，构建模型→模块映射表
        
        扫描 app/modules/*/models.py，提取所有的模型类定义，
        建立模型名称到模块名称的映射关系。
        """
        modules_dir = self.project_root / 'app' / 'modules'
        
        if not modules_dir.exists():
            print(f"⚠️  警告: 模块目录不存在: {modules_dir}")
            return
        
        # 遍历所有模块目录
        for module_path in modules_dir.iterdir():
            if not module_path.is_dir():
                continue
            
            module_name = module_path.name
            models_file = module_path / 'models.py'
            
            if not models_file.exists():
                continue
            
            # 解析models.py，提取模型类
            try:
                model_classes = self._extract_model_classes(models_file)
                for model_class in model_classes:
                    self.model_to_module[model_class] = module_name
            except Exception as e:
                print(f"⚠️  警告: 解析 {models_file} 失败: {e}")
    
    def _extract_model_classes(self, models_file: Path) -> List[str]:
        """从models.py文件中提取所有模型类名
        
        Args:
            models_file: models.py文件路径
            
        Returns:
            模型类名列表
        """
        model_classes = []
        
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用AST解析
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # 检查是否继承自Base或BaseModel
                    for base in node.bases:
                        base_name = None
                        if isinstance(base, ast.Name):
                            base_name = base.id
                        elif isinstance(base, ast.Attribute):
                            base_name = base.attr
                        
                        # 如果继承自Base、BaseModel、SoftDeleteMixin等，认为是模型类
                        if base_name in ['Base', 'BaseModel', 'TimestampMixin', 'SoftDeleteMixin']:
                            model_classes.append(node.name)
                            break
        except Exception as e:
            # 如果AST解析失败，尝试正则表达式
            try:
                with open(models_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 匹配 class ModelName(Base): 或 class ModelName(TimestampMixin, Base):
                pattern = r'class\s+(\w+)\s*\([^)]*(?:Base|BaseModel|TimestampMixin)[^)]*\):'
                matches = re.findall(pattern, content)
                model_classes.extend(matches)
            except Exception as e2:
                print(f"⚠️  警告: 正则提取模型类失败: {e2}")
        
        return model_classes
    
    def get_module_for_model(self, model_name: str) -> Optional[str]:
        """获取模型所属的模块名称
        
        Args:
            model_name: 模型类名，如 'Product', 'User', 'SKU'
            
        Returns:
            模块名称，如 'product_catalog', 'user_auth'，如果未找到返回None
        """
        return self.model_to_module.get(model_name)
    
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
