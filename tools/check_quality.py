#!/usr/bin/env python3
"""
代码质量综合检查工具 (Code Quality Comprehensive Checker)

功能说明:
- 硬编码检查: 检测Python文件中的硬编码字符串、邮箱、密码、用户名等测试数据
- 重复代码检查: 检测重复的函数定义、方法定义、导入语句和代码块
- 批量文件检查: 支持单文件检查和目录递归检查
- 统一报告: 提供详细的检查报告和修复建议

使用场景:
1. 开发阶段 - 在编写代码时发现和修复质量问题
2. 代码审查 - 在代码合并前进行质量检查
3. CI/CD集成 - 在持续集成中自动运行质量检查
4. 代码重构 - 在重构代码时识别重复和硬编码问题
5. 测试生成器维护 - 专门检查测试生成器的代码质量

基本使用方法:
    # 检查所有测试生成器的硬编码问题
    python tools/check_quality.py --hardcode
    
    # 检查单个文件的硬编码问题
    python tools/check_quality.py --hardcode --file api_test_generator.py
    
    # 检查指定目录的重复代码问题
    python tools/check_quality.py --duplication --dir tools/
    
    # 检查单个文件的重复代码问题
    python tools/check_quality.py --duplication --file base_generator.py
    
    # 运行所有检查 (推荐)
    python tools/check_quality.py --all

高级使用方法:
    # 检查整个项目的硬编码问题
    python tools/check_quality.py --hardcode --dir .
    
    # 检查指定模块的代码质量
    python tools/check_quality.py --all --dir app/modules/user_auth/
    
    # 检查特定生成器文件
    python tools/check_quality.py --all --file tools/test_generators/security_test_generator.py

集成建议:
1. Git pre-commit hook: 在提交前自动运行检查
2. IDE集成: 配置为IDE的外部工具
3. CI/CD流水线: 作为代码质量门禁
4. 定期维护: 每周运行全项目检查

输出说明:
- ✅ 绿色: 检查通过，无问题
- ⚠️ 黄色: 发现问题，需要关注
- ❌ 红色: 发现严重问题，需要修复
- 📊 统计: 提供详细的统计信息
- 🔧 建议: 提供具体的修复建议

版本: v1.0.0
作者: AI Assistant
创建时间: 2025-10-04
最后更新: 2025-10-04
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
import re
import ast
from collections import defaultdict


class QualityChecker:
    """代码质量检查器"""
    
    def __init__(self):
        self.hardcode_patterns = [
            # 邮箱地址
            r'"[^"]*@[^"]*\.(com|cn|org)"',
            # 测试用户名
            r'"test_?user"',
            r'"user_?test"', 
            # 测试密码
            r'"test_?password\d*"',
            r'"password\d+"',
            # 手机号
            r'"1[3-9]\d{9}"',
            # 具体的硬编码值
            r'"test@example\.com"',
            r'"13800138000"',
            r'"test_password123"',
            r'"123456"',
            # 测试数据
            r'"test_?data"',
            r'"test_?value"',
            r'"test_?field"',
            # 硬编码的断言字段
            r'assert "username"',
            r'assert "email"', 
            r'assert "password"',
            # 其他明显的测试硬编码
            r'"[^"]*test[^"]*@[^"]*"',
        ]
        
        # 忽略规则 - 这些情况不应该被标记为硬编码
        self.ignore_patterns = [
            # 模式定义本身 (在字符串数组或正则定义中)
            r'self\.hardcode_patterns\s*=\s*\[',
            r'hardcode_patterns\s*=\s*\[',
            r'r["\'].*["\'],?\s*#.*',  # 正则表达式定义 (带注释)
            r'r["\'].*["\'],?\s*$',    # 正则表达式定义 (行尾)
            # 配置示例或文档字符串
            r'""".*"""',
            r"'''.*'''", 
            # SQL连接字符串 (配置文件中)
            r'mysql\+pymysql://',
            # 测试工厂中的mock数据 (合理的测试数据)
            r'mock_.*\s*=',
            r'fake\.',
            r'Faker\(',
            # 示例数据定义
            r'valid_.*\s*=\s*\[',
            r'invalid_.*\s*=\s*\[',
            r'example_.*\s*=',
            # 测试模板生成器中的模板内容 (这些是生成的模板，不是真实硬编码)
            r'class.*TestGenerator.*:',  # 测试生成器类内部
            r'def.*generate.*\(',  # 生成器方法内部
            r'return.*f["\'].*["\']',  # 格式化字符串模板
            r'""".*测试.*"""',  # 测试相关的文档字符串
            # 测试代码模板中的占位符和示例
            r'username.*=.*integration_test_user',
            r'email.*=.*@test\.',
            r'phone.*=.*\d{11}',
            r'assert.*@test\.',
            r'created_user\..*==.*@test\.',
            # 配置文件中的示例值
            r'mysql\+pymysql://.*test.*@.*:\d+/',
            # 测试模板生成器特定的模板代码行
            r'valid_value\s*=\s*["\'].*["\']',  # 模板中的有效值示例
            r'valid_email\s*=\s*["\'].*["\']',  # 模板中的邮箱示例
            r'test_value\s*=\s*["\'].*["\']',   # 模板中的测试值示例
            r'return\s*["\'].*@.*["\']',        # 返回的邮箱模板
            r'email\s*=\s*["\'].*@.*["\'],?',   # 邮箱赋值模板
            r'"email":\s*["\'].*@.*["\'],?',    # JSON中的邮箱模板
        ]
        
    def _should_ignore_line(self, line: str, file_path: str = "") -> bool:
        """检查是否应该忽略某行"""
        line_stripped = line.strip()
        
        # 添加调试信息
        debug_mode = False  # 可以设置为True来调试
        
        # 基础忽略模式 - 适用于所有文件
        basic_ignore_patterns = [
            # 模式定义本身 (在字符串数组或正则定义中)
            r'self\.hardcode_patterns\s*=\s*\[',
            r'hardcode_patterns\s*=\s*\[',
            r'r["\'].*["\'],?\s*#.*',  # 正则表达式定义 (带注释)
            r'r["\'].*["\'],?\s*$',    # 正则表达式定义 (行尾)
            # 配置示例或文档字符串 - 暂时注释掉，避免过度忽略
            # r'""".*"""',
            # r"'''.*'''", 
            # SQL连接字符串 (配置文件中)
            r'mysql\+pymysql://',
            # 测试工厂中的mock数据 (合理的测试数据)
            r'mock_.*\s*=',
            r'fake\.',
            r'Faker\(',
            # 示例数据定义
            r'valid_.*\s*=\s*\[',
            r'invalid_.*\s*=\s*\[',
            r'example_.*\s*=',
        ]
        
        # 检查基础忽略模式
        for ignore_pattern in basic_ignore_patterns:
            if re.search(ignore_pattern, line, re.IGNORECASE | re.MULTILINE):
                if debug_mode:
                    print(f"DEBUG: 忽略行 '{line_stripped}' 匹配基础模式: {ignore_pattern}")
                return True
        
        # 特定文件的忽略模式 - 只在测试模板生成器中生效
        if "generate_test_template.py" in file_path:
            template_ignore_patterns = [
                # 测试模板生成器特定的模板代码行
                r'valid_value\s*=\s*["\'].*["\']',  # 模板中的有效值示例
                r'valid_email\s*=\s*["\'].*["\']',  # 模板中的邮箱示例
                r'test_value\s*=\s*["\'].*["\']',   # 模板中的测试值示例
                r'return\s*["\'].*@.*["\']',        # 返回的邮箱模板
                r'email\s*=\s*["\'].*@.*["\'],?',   # 邮箱赋值模板
                r'"email":\s*["\'].*@.*["\'],?',    # JSON中的邮箱模板
                # 测试代码模板中的占位符和示例
                r'username.*=.*integration_test_user',
                r'email.*=.*@test\.',
                r'phone.*=.*\d{11}',
                r'assert.*@test\.',
                r'created_user\..*==.*@test\.',
            ]
            
            for ignore_pattern in template_ignore_patterns:
                if re.search(ignore_pattern, line, re.IGNORECASE | re.MULTILINE):
                    if debug_mode:
                        print(f"DEBUG: 忽略模板行 '{line_stripped}' 匹配模式: {ignore_pattern}")
                    return True
                
        # 检查是否在正则表达式定义上下文中
        if ('r"' in line or "r'" in line) and line.strip().startswith('r'):
            if debug_mode:
                print(f"DEBUG: 忽略正则表达式行: '{line_stripped}'")
            return True
            
        return False

    def check_hardcode_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """检查单个文件的硬编码"""
        if not file_path.exists() or not file_path.suffix == '.py':
            return []
            
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # 检查是否应该忽略这一行
                if self._should_ignore_line(line, str(file_path)):
                    continue
                    
                for pattern in self.hardcode_patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    if matches:
                        violations.append({
                            'file': str(file_path),
                            'line': i,
                            'content': line.strip(),
                            'matches': matches,
                            'pattern': pattern
                        })
        except Exception as e:
            print(f"⚠️ 读取文件失败 {file_path}: {e}")
            
        return violations

    def check_hardcode_directory(self, dir_path: Path) -> List[Dict[str, Any]]:
        """检查目录下所有Python文件的硬编码"""
        all_violations = []
        
        # 默认检查测试生成器目录
        if not dir_path:
            dir_path = Path("tools/test_generators/")
            
        if not dir_path.exists():
            print(f"❌ 目录不存在: {dir_path}")
            return []
            
        python_files = list(dir_path.rglob("*.py"))
        
        for py_file in python_files:
            violations = self.check_hardcode_file(py_file)
            all_violations.extend(violations)
            
        return all_violations

    def check_duplication_file(self, file_path: Path) -> Dict[str, Any]:
        """检查单个文件的重复代码"""
        if not file_path.exists() or not file_path.suffix == '.py':
            return {'functions': {}, 'methods': {}, 'imports': [], 'classes': {}}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            detector = DuplicationDetector()
            detector.visit(tree)
            
            return {
                'file': str(file_path),
                'functions': dict(detector.functions),
                'methods': dict(detector.methods), 
                'imports': detector.imports,
                'classes': dict(detector.classes)
            }
        except Exception as e:
            print(f"⚠️ 解析文件失败 {file_path}: {e}")
            return {'functions': {}, 'methods': {}, 'imports': [], 'classes': {}}

    def check_duplication_directory(self, dir_path: Path) -> List[Dict[str, Any]]:
        """检查目录下所有Python文件的重复代码"""
        all_results = []
        
        if not dir_path.exists():
            print(f"❌ 目录不存在: {dir_path}")
            return []
            
        python_files = list(dir_path.rglob("*.py"))
        
        for py_file in python_files:
            result = self.check_duplication_file(py_file)
            if result['functions'] or result['methods'] or result['imports']:
                all_results.append(result)
                
        return all_results

    def report_hardcode_violations(self, violations: List[Dict[str, Any]]):
        """报告硬编码违规"""
        if violations:
            print(f"❌ 发现 {len(violations)} 个硬编码违规:")
            
            # 按文件分组
            by_file = defaultdict(list)
            for v in violations:
                by_file[v['file']].append(v)
                
            for file_path, file_violations in by_file.items():
                print(f"\n📁 文件: {file_path}")
                for v in file_violations:
                    print(f"  行{v['line']}: {v['content']}")
                    print(f"    匹配: {v['matches']}")
                    print(f"    模式: {v['pattern']}")
                    print()
            return False
        else:
            print("✅ 硬编码检查通过！没有发现违规项")
            return True

    def report_duplication_results(self, results: List[Dict[str, Any]]):
        """报告重复代码结果"""
        has_duplicates = False
        
        for result in results:
            file_path = result['file']
            print(f"\n🔍 代码重复检查报告: {Path(file_path).name}")
            print("=" * 60)
            
            # 统计信息
            total_functions = sum(len(funcs) for funcs in result['functions'].values())
            total_methods = sum(len(methods) for methods in result['methods'].values())
            total_classes = sum(len(classes) for classes in result['classes'].values())
            
            print(f"📊 概览:")
            print(f"  • 总函数数量: {total_functions}")
            print(f"  • 总方法数量: {total_methods}")
            print(f"  • 总类数量: {total_classes}")
            
            # 检查重复定义
            duplicates_found = False
            
            # 检查重复函数
            for func_name, occurrences in result['functions'].items():
                if len(occurrences) > 1:
                    print(f"\n⚠️ 发现重复函数定义: {func_name}")
                    for line, signature in occurrences:
                        print(f"  🟡 第{line}行: {signature}")
                    duplicates_found = True
                    has_duplicates = True
                    
            # 检查重复方法
            for method_name, occurrences in result['methods'].items():
                if len(occurrences) > 1:
                    print(f"\n⚠️ 发现重复方法定义: {method_name}")
                    for line, signature, class_name in occurrences:
                        print(f"  🟡 第{line}行 (类{class_name}): {signature}")
                    duplicates_found = True
                    has_duplicates = True
                    
            # 检查重复导入
            import_counts = defaultdict(list)
            for import_info in result['imports']:
                import_counts[import_info['statement']].append(import_info['line'])
                
            for statement, lines in import_counts.items():
                if len(lines) > 1:
                    print(f"\n⚠️ 发现重复导入:")
                    print(f"  🟡 {statement}")
                    print(f"     重复在第 {', '.join(map(str, lines))} 行")
                    duplicates_found = True
                    has_duplicates = True
                    
            if not duplicates_found:
                print("\n✅ 未发现重复定义问题")
                
        if not has_duplicates:
            print("\n✅ 所有文件都没有重复代码问题")
            return True
        else:
            print(f"\n📈 建议:")
            print(f"  1. 删除重复的函数/方法定义")
            print(f"  2. 合并相似功能的方法") 
            print(f"  3. 清理重复的导入语句")
            return False


class DuplicationDetector(ast.NodeVisitor):
    """代码重复检测器"""
    
    def __init__(self):
        self.functions = defaultdict(list)
        self.methods = defaultdict(list)
        self.classes = defaultdict(list)
        self.imports = []
        
    def visit_FunctionDef(self, node):
        signature = self._get_function_signature(node)
        self.functions[node.name].append((node.lineno, signature))
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        signature = self._get_function_signature(node, is_async=True)
        self.functions[node.name].append((node.lineno, signature))
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.classes[node.name].append(node.lineno)
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                signature = self._get_function_signature(item, is_async=isinstance(item, ast.AsyncFunctionDef))
                self.methods[item.name].append((item.lineno, signature, node.name))
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({
                'line': node.lineno,
                'statement': f"import {alias.name}",
                'type': 'import'
            })
    
    def visit_ImportFrom(self, node):
        module = node.module or ""
        names = [alias.name for alias in node.names]
        self.imports.append({
            'line': node.lineno,
            'statement': f"from {module} import {', '.join(names)}",
            'type': 'from_import'
        })
    
    def _get_function_signature(self, node, is_async=False):
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        prefix = "async " if is_async else ""
        signature = f"{prefix}def {node.name}({', '.join(args)})"
        return signature


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='代码质量检查工具')
    parser.add_argument('--hardcode', action='store_true', help='检查硬编码')
    parser.add_argument('--duplication', action='store_true', help='检查重复代码')
    parser.add_argument('--all', action='store_true', help='运行所有检查')
    parser.add_argument('--file', type=str, help='检查单个文件')
    parser.add_argument('--dir', type=str, help='检查目录')
    
    args = parser.parse_args()
    
    if not any([args.hardcode, args.duplication, args.all]):
        print("请指定检查类型: --hardcode, --duplication, 或 --all")
        parser.print_help()
        sys.exit(1)
        
    checker = QualityChecker()
    success = True
    
    # 硬编码检查
    if args.hardcode or args.all:
        print("🔍 开始硬编码检查...")
        
        if args.file:
            file_path = Path(args.file)
            # 如果是相对路径且不存在，尝试在tools/test_generators中查找
            if not file_path.is_absolute() and not file_path.exists():
                test_generators_path = Path("tools/test_generators") / file_path
                if test_generators_path.exists():
                    file_path = test_generators_path
            violations = checker.check_hardcode_file(file_path)
        elif args.dir:
            violations = checker.check_hardcode_directory(Path(args.dir))
        else:
            # 默认检查测试生成器目录
            violations = checker.check_hardcode_directory(Path("tools/test_generators"))
            
        if not checker.report_hardcode_violations(violations):
            success = False
    
    # 重复代码检查  
    if args.duplication or args.all:
        print("\n🔍 开始重复代码检查...")
        
        if args.file:
            file_path = Path(args.file)
            # 如果是相对路径且不存在，尝试在tools/test_generators中查找
            if not file_path.is_absolute() and not file_path.exists():
                test_generators_path = Path("tools/test_generators") / file_path
                if test_generators_path.exists():
                    file_path = test_generators_path
            results = [checker.check_duplication_file(file_path)]
        elif args.dir:
            results = checker.check_duplication_directory(Path(args.dir))
        else:
            # 默认检查测试生成器目录
            results = checker.check_duplication_directory(Path("tools/test_generators"))
            
        if not checker.report_duplication_results(results):
            success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()