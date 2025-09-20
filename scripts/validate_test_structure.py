#!/usr/bin/env python3
"""
测试结构自动验证脚本
运行: python scripts/validate_test_structure.py
"""

import os
import ast
import sys
from pathlib import Path

class TestStructureValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_file_naming(self, file_path):
        """验证文件命名规范"""
        filename = Path(file_path).name
        if not filename.startswith('test_'):
            self.errors.append(f"❌ {file_path}: 文件名必须以'test_'开头")
        
        if filename == 'test.py' or filename == 'tests.py':
            self.errors.append(f"❌ {file_path}: 文件名过于宽泛，应具体到功能域")
    
    def validate_test_functions(self, file_path):
        """验证测试函数命名和结构"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
        except SyntaxError as e:
            self.errors.append(f"❌ {file_path}: 语法错误 {e}")
            return
        except Exception as e:
            self.errors.append(f"❌ {file_path}: 文件读取错误 {e}")
            return
        
        test_functions = []
        test_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_functions.append(node.name)
                    self._validate_test_function_name(node.name, file_path)
            elif isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    test_classes.append(node.name)
        
        # 检查是否有测试函数
        if not test_functions and not test_classes:
            self.warnings.append(f"⚠️ {file_path}: 文件中没有找到测试函数或测试类")
    
    def _validate_test_function_name(self, func_name, file_path):
        """验证测试函数命名规范"""
        parts = func_name.split('_')
        if len(parts) < 3:  # test_功能_场景
            self.warnings.append(
                f"⚠️ {file_path}:{func_name} - 建议使用格式: test_功能_场景_预期结果"
            )
        
        # 检查是否包含预期结果描述
        result_keywords = ['returns', 'raises', 'creates', 'updates', 'deletes', 'validates']
        has_result_keyword = any(keyword in func_name.lower() for keyword in result_keywords)
        if not has_result_keyword:
            self.warnings.append(
                f"⚠️ {file_path}:{func_name} - 建议在函数名中包含预期结果 (returns/raises/creates等)"
            )
    
    def validate_required_imports(self, file_path):
        """验证必需的导入"""
        required_imports = ['pytest']
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for required in required_imports:
            if f"import {required}" not in content and f"from {required}" not in content:
                self.errors.append(f"❌ {file_path}: 缺少必需导入 '{required}'")
        
        # 检查是否使用了禁止的导入
        forbidden_patterns = [
            'from unittest.mock import',
            'import unittest.mock'
        ]
        
        for pattern in forbidden_patterns:
            if pattern in content:
                self.errors.append(f"❌ {file_path}: 禁止使用 '{pattern}'，请使用 pytest-mock")
    
    def validate_test_structure(self, file_path):
        """验证测试文件整体结构"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有文档字符串
        if '"""' not in content and "'''" not in content:
            self.warnings.append(f"⚠️ {file_path}: 建议添加模块或类的文档字符串")
        
        # 检查是否有setup/teardown方法
        if 'setup_method' in content or 'teardown_method' in content:
            if 'setup_method' in content and 'teardown_method' not in content:
                self.warnings.append(f"⚠️ {file_path}: 有setup_method但缺少teardown_method")
    
    def run_validation(self, test_dir="tests/"):
        """运行完整验证"""
        print("🔍 开始验证测试结构...")
        
        if not os.path.exists(test_dir):
            print(f"❌ 测试目录不存在: {test_dir}")
            return False
        
        test_files_found = 0
        
        for root, dirs, files in os.walk(test_dir):
            # 跳过__pycache__目录
            if '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py') and (file.startswith('test_') or file == 'conftest.py'):
                    file_path = os.path.join(root, file)
                    
                    if file.startswith('test_'):
                        test_files_found += 1
                        print(f"  📄 验证: {file_path}")
                        self.validate_file_naming(file_path)
                        self.validate_test_functions(file_path)
                        self.validate_required_imports(file_path)
                        self.validate_test_structure(file_path)
        
        print(f"\n📊 验证统计: 共检查 {test_files_found} 个测试文件")
        
        # 输出结果
        if self.errors:
            print(f"\n❌ 发现 {len(self.errors)} 个错误 (必须修复):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️ 发现 {len(self.warnings)} 个警告 (建议优化):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ 所有测试文件结构验证通过!")
        elif not self.errors:
            print("✅ 验证通过 (仅有建议性警告)")
        
        print(f"\n📋 验证摘要:")
        print(f"   ✅ 通过: {test_files_found - len(set(e.split(':')[1] for e in self.errors if ':' in e))} 个文件")
        print(f"   ❌ 错误: {len(self.errors)} 个")
        print(f"   ⚠️  警告: {len(self.warnings)} 个")
        
        return len(self.errors) == 0

if __name__ == "__main__":
    # 支持命令行参数指定测试目录
    test_directory = sys.argv[1] if len(sys.argv) > 1 else "tests/"
    
    validator = TestStructureValidator()
    success = validator.run_validation(test_directory)
    
    if success:
        print("\n🎉 测试结构验证完成! 可以安全进行测试。")
    else:
        print("\n🚨 发现结构问题，请修复后再运行测试。")
    
    sys.exit(0 if success else 1)