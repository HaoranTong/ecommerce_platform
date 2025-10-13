#!/usr/bin/env python3
"""
智能Factory导入修复器 - 渐进式改造方案A

📋 功能说明:
- 自动分析Factory文件中的跨模块依赖
- 基于tests/factories/__init__.py的统一导入架构
- 智能修复缺失的导入，不修改复杂模板逻辑
- 支持验证和回滚

🎯 设计原则:
- 最小侵入性：只修复导入部分
- 利用现有架构：基于__init__.py的统一导入设计
- 可验证性：每次修改都可以测试验证
- 全局思维：为所有模块提供通用解决方案

作者: AI Assistant
创建时间: 2025-10-12
版本: v1.0.0
"""

import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import importlib.util


class FactoryDependencyAnalyzer:
    """Factory依赖分析器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.factories_dir = self.project_root / "tests" / "factories"
        
    def analyze_factory_file(self, factory_file_path: Path) -> Dict[str, List[str]]:
        """分析Factory文件中的跨模块依赖
        
        Returns:
            {
                'used_factories': ['UserFactory', 'ProductFactory'],
                'current_imports': ['Cart', 'CartItem'],
                'missing_imports': ['UserFactory', 'ProductFactory']
            }
        """
        if not factory_file_path.exists():
            return {'used_factories': [], 'current_imports': [], 'missing_imports': []}
            
        content = factory_file_path.read_text(encoding='utf-8')
        
        # 找到所有使用的Factory类
        used_factories = self._find_used_factories(content)
        
        # 找到当前已导入的Factory类
        current_imports = self._find_current_imports(content)
        
        # 计算缺失的导入
        missing_imports = [f for f in used_factories if f not in current_imports]
        
        return {
            'used_factories': used_factories,
            'current_imports': current_imports,
            'missing_imports': missing_imports
        }
    
    def _find_used_factories(self, content: str) -> List[str]:
        """找到代码中使用的所有Factory类"""
        # 匹配Factory使用模式：
        # 1. factory.SubFactory(UserFactory)
        # 2. UserFactory()
        # 3. UserFactory.create()
        
        factory_patterns = [
            r'factory\.SubFactory\((\w+Factory)\)',  # SubFactory引用
            r'(\w+Factory)\(\)',                     # 直接调用
            r'(\w+Factory)\.create\(',              # create方法调用
            r'(\w+Factory)\.build\(',               # build方法调用
        ]
        
        used_factories = set()
        for pattern in factory_patterns:
            matches = re.findall(pattern, content)
            used_factories.update(matches)
            
        return list(used_factories)
    
    def _find_current_imports(self, content: str) -> List[str]:
        """找到当前已导入的Factory类"""
        # 解析导入语句
        import_patterns = [
            r'from tests\.factories\.?\w* import.*?(\w+Factory)',
            r'from tests\.factories import.*?(\w+Factory)',
            r'import.*?(\w+Factory)',
        ]
        
        imported_factories = set()
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imported_factories.update(matches)
            
        return list(imported_factories)


class FactoryImportFixer:
    """Factory导入修复器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.factories_dir = self.project_root / "tests" / "factories"
        self.analyzer = FactoryDependencyAnalyzer()
        
        # 从__init__.py获取可用的Factory映射
        self.available_factories = self._load_available_factories()
        
    def _load_available_factories(self) -> Dict[str, str]:
        """从tests/factories/__init__.py加载可用的Factory映射
        
        Returns:
            {'UserFactory': 'user_auth_factories', 'ProductFactory': 'product_catalog_factories'}
        """
        init_file = self.factories_dir / "__init__.py"
        if not init_file.exists():
            return {}
            
        content = init_file.read_text(encoding='utf-8')
        factory_mapping = {}
        
        # 解析导入语句，建立Factory -> 模块的映射
        import_patterns = [
            r'from \.(\w+_factories) import \((.*?)\)',  # 多行导入
            r'from \.(\w+_factories) import (.+)',       # 单行导入
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for module_name, imports in matches:
                # 处理导入的Factory列表
                factories = re.findall(r'(\w+Factory)', imports)
                for factory in factories:
                    factory_mapping[factory] = module_name
                    
        return factory_mapping
    
    def fix_factory_file(self, factory_file_path: Path, dry_run: bool = True) -> Dict[str, any]:
        """修复Factory文件的导入问题
        
        Args:
            factory_file_path: Factory文件路径
            dry_run: 是否只是预览修改，不实际写入
            
        Returns:
            修复结果和统计信息
        """
        if not factory_file_path.exists():
            return {'status': 'error', 'message': 'File not found'}
            
        # 分析依赖
        analysis = self.analyzer.analyze_factory_file(factory_file_path)
        missing_imports = analysis['missing_imports']
        
        if not missing_imports:
            return {'status': 'ok', 'message': 'No missing imports found'}
            
        # 生成修复后的内容
        original_content = factory_file_path.read_text(encoding='utf-8')
        fixed_content = self._add_missing_imports(original_content, missing_imports)
        
        result = {
            'status': 'fixed',
            'file': str(factory_file_path),
            'missing_imports': missing_imports,
            'analysis': analysis,
            'content_changed': original_content != fixed_content
        }
        
        if not dry_run and result['content_changed']:
            # 备份原文件
            backup_path = factory_file_path.with_suffix('.py.backup')
            backup_path.write_text(original_content, encoding='utf-8')
            
            # 写入修复后的内容
            factory_file_path.write_text(fixed_content, encoding='utf-8')
            result['backup_created'] = str(backup_path)
            
        return result
    
    def _add_missing_imports(self, content: str, missing_imports: List[str]) -> str:
        """添加缺失的导入到文件内容中"""
        if not missing_imports:
            return content
            
        # 按模块分组导入
        imports_by_module = {}
        for factory in missing_imports:
            if factory in self.available_factories:
                module = self.available_factories[factory]
                if module not in imports_by_module:
                    imports_by_module[module] = []
                imports_by_module[module].append(factory)
            else:
                print(f"⚠️  Warning: {factory} not found in available factories")
                
        # 生成导入语句
        import_statements = []
        for module, factories in imports_by_module.items():
            factories_str = ', '.join(sorted(factories))
            import_statements.append(f"from tests.factories.{module} import {factories_str}")
            
        if not import_statements:
            return content
            
        # 更智能地找到导入插入位置
        lines = content.split('\n')
        
        # 寻找合适的导入位置：
        # 1. 跳过文件头注释和文档字符串
        # 2. 在现有导入语句后插入
        
        insertion_point = 0
        in_docstring = False
        docstring_quote = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检测文档字符串的开始和结束
            if '"""' in stripped or "'''" in stripped:
                if not in_docstring:
                    in_docstring = True
                    docstring_quote = '"""' if '"""' in stripped else "'''"
                elif docstring_quote in stripped:
                    in_docstring = False
                    docstring_quote = None
                    insertion_point = i + 1
                continue
                    
            # 如果在文档字符串内，跳过
            if in_docstring:
                continue
                
            # 如果是导入语句，更新插入点
            if (stripped.startswith('from ') or 
                stripped.startswith('import ') and 'factory' not in stripped.lower()):
                insertion_point = i + 1
            elif stripped.startswith('#') or stripped == '':
                # 注释和空行，继续
                if insertion_point == 0:
                    insertion_point = i + 1
            elif stripped and not stripped.startswith('#'):
                # 遇到实际代码，停止查找
                break
                
        # 在找到的位置插入导入语句
        for j, statement in enumerate(import_statements):
            lines.insert(insertion_point + j, statement)
            
        # 在导入语句后添加空行（如果不存在）
        if insertion_point + len(import_statements) < len(lines):
            next_line = lines[insertion_point + len(import_statements)]
            if next_line.strip() != '':
                lines.insert(insertion_point + len(import_statements), '')
            
        return '\n'.join(lines)
    
    def validate_fixed_file(self, factory_file_path: Path) -> Dict[str, any]:
        """验证修复后的Factory文件是否可以正常导入"""
        try:
            # 尝试导入修复后的文件
            spec = importlib.util.spec_from_file_location("test_factory", factory_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return {'status': 'valid', 'message': 'File can be imported successfully'}
        except Exception as e:
            return {'status': 'invalid', 'message': f'Import error: {str(e)}'}


def fix_shopping_cart_factories():
    """修复shopping_cart_factories.py的导入问题"""
    print("🚀 开始修复shopping_cart_factories.py导入问题")
    
    fixer = FactoryImportFixer()
    shopping_cart_factory = fixer.project_root / "tests" / "factories" / "shopping_cart_factories.py"
    
    print(f"📁 目标文件: {shopping_cart_factory}")
    print(f"📁 文件存在: {shopping_cart_factory.exists()}")
    
    if not shopping_cart_factory.exists():
        print("❌ 文件不存在")
        return {'status': 'error', 'message': 'File not found'}
    
    # 先预览修改
    print("\n📋 预览修改:")
    result = fixer.fix_factory_file(shopping_cart_factory, dry_run=True)
    print(f"Status: {result['status']}")
    if result['status'] == 'fixed':
        print(f"Missing imports: {result['missing_imports']}")
        print(f"Content will change: {result['content_changed']}")
    elif result['status'] == 'error':
        print(f"Error: {result.get('message', 'Unknown error')}")
    
    # 实际修复
    if result['status'] == 'fixed' and result['content_changed']:
        print("\n🔧 执行修复:")
        fix_result = fixer.fix_factory_file(shopping_cart_factory, dry_run=False)
        if 'backup_created' in fix_result:
            print(f"✅ 备份文件: {fix_result['backup_created']}")
        print("✅ 导入修复完成")
        
        # 验证修复结果
        print("\n🔍 验证修复结果:")
        validation = fixer.validate_fixed_file(shopping_cart_factory)
        print(f"Validation: {validation['status']} - {validation['message']}")
    
    return result


if __name__ == "__main__":
    # 修复shopping_cart模块的Factory导入问题
    fix_shopping_cart_factories()