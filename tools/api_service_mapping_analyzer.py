#!/usr/bin/env python3
"""
API与服务层映射分析脚本

功能描述：
- 分析所有模块的router.py和service.py文件
- 提取API函数名和服务方法名的映射关系
- 识别命名不一致问题
- 生成标准化的测试代码

解决问题：
- 防止测试代码中使用错误的方法名
- 提供API与Service层的准确映射
- 自动生成符合实际代码的测试模板

使用方法：
    python tools/api_service_mapping_analyzer.py --analyze shopping_cart
    python tools/api_service_mapping_analyzer.py --analyze-all
    python tools/api_service_mapping_analyzer.py --generate-test shopping_cart
    
示例:
    # 分析特定模块的API/Service映射
    python tools/api_service_mapping_analyzer.py --analyze user_auth
    
    # 分析所有模块的API/Service映射
    python tools/api_service_mapping_analyzer.py --analyze-all
    
    # 生成特定模块的测试代码
    python tools/api_service_mapping_analyzer.py --generate-test product_catalog
    
    # 导出分析结果到JSON文件
    python tools/api_service_mapping_analyzer.py --analyze-all --export mapping.json

输出格式:
    - 控制台输出: 可读性良好的文本报告
    - JSON格式: 结构化的映射数据
    - 测试代码: 自动生成的pytest测试模板

应用场景:
    1. 测试自动化 - 生成准确的API测试代码
    2. 代码审查 - 检查API与Service层的一致性
    3. 文档生成 - 自动生成API文档
    4. 重构辅助 - 识别需要同步修改的API和服务方法
"""

import ast
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class APIServiceMappingAnalyzer:
    """API与服务层映射分析器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.modules_dir = self.project_root / "app" / "modules"

    def analyze_all_modules(self) -> Dict[str, Dict]:
        """分析所有模块的API/Service映射"""
        results = {}

        # 遍历所有模块目录
        for module_dir in self.modules_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith("_"):
                module_name = module_dir.name
                print(f"\n📦 分析模块: {module_name}")

                analysis = self.analyze_module(module_name)
                if analysis:
                    results[module_name] = analysis

        return results

    def analyze_module(self, module_name: str) -> Optional[Dict]:
        """分析单个模块"""
        module_path = self.modules_dir / module_name

        # 分析API层 (router.py)
        api_functions = self.extract_api_functions(module_path)

        # 分析服务层 (service.py)
        service_methods = self.extract_service_methods(module_path)

        if not api_functions and not service_methods:
            print(f"   ⚠️  模块 {module_name} 没有发现API或Service代码")
            return None

        # 映射分析
        mapping_analysis = self.analyze_api_service_mapping(
            api_functions, service_methods
        )

        result = {
            "module_name": module_name,
            "api_functions": api_functions,
            "service_methods": service_methods,
            "mapping_analysis": mapping_analysis,
            "analysis_time": datetime.now().isoformat(),
        }

        # 打印映射报告
        self.print_mapping_report(module_name, result)

        return result

    def extract_api_functions(self, module_path: Path) -> List[Dict]:
        """提取API函数信息"""
        router_file = module_path / "router.py"
        if not router_file.exists():
            return []

        functions = []
        try:
            with open(router_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef) or isinstance(
                    node, ast.FunctionDef
                ):
                    # 检查是否有路由装饰器
                    route_info = self._extract_route_decorator(node)

                    if route_info:
                        functions.append(
                            {
                                "name": node.name,
                                "http_method": route_info["method"],
                                "path": route_info["path"],
                                "is_async": isinstance(node, ast.AsyncFunctionDef),
                                "parameters": [arg.arg for arg in node.args.args],
                                "line_number": node.lineno,
                                "service_calls": self._extract_service_calls(node),
                            }
                        )

        except Exception as e:
            print(f"   ❌ 解析router.py失败: {e}")

        return functions

    def extract_service_methods(self, module_path: Path) -> List[Dict]:
        """提取服务方法信息"""
        service_file = module_path / "service.py"
        if not service_file.exists():
            return []

        methods = []
        service_class_name = None

        try:
            with open(service_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # 查找服务类
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and "Service" in node.name:
                    service_class_name = node.name

                    # 提取类中的公共方法
                    for item in node.body:
                        if isinstance(item, (ast.AsyncFunctionDef, ast.FunctionDef)):
                            if not item.name.startswith("_"):  # 排除私有方法
                                methods.append(
                                    {
                                        "name": item.name,
                                        "class_name": service_class_name,
                                        "is_async": isinstance(
                                            item, ast.AsyncFunctionDef
                                        ),
                                        "parameters": [
                                            arg.arg
                                            for arg in item.args.args
                                            if arg.arg != "self"
                                        ],
                                        "line_number": item.lineno,
                                    }
                                )

        except Exception as e:
            print(f"   ❌ 解析service.py失败: {e}")

        return methods

    def _extract_route_decorator(self, node) -> Optional[Dict]:
        """提取路由装饰器信息"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                func = decorator.func

                # @router.post(), @router.get() 等
                if (
                    isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "router"
                ):

                    method = func.attr.upper()
                    path = ""

                    # 提取路径参数
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        path = decorator.args[0].value

                    return {"method": method, "path": path}

        return None

    def _extract_service_calls(self, node) -> List[str]:
        """提取函数中的服务方法调用"""
        service_calls = []

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # 检查 service.method_name() 或 await service.method_name() 调用
                if isinstance(child.func, ast.Attribute):
                    if isinstance(
                        child.func.value, ast.Name
                    ) and child.func.value.id in [
                        "service",
                        "cart_service",
                        "user_service",
                    ]:
                        service_calls.append(child.func.attr)

        return list(set(service_calls))  # 去重

    def analyze_api_service_mapping(
        self, api_functions: List[Dict], service_methods: List[Dict]
    ) -> Dict:
        """分析API与Service的映射关系"""
        service_method_names = {m["name"] for m in service_methods}

        mapping_results = []
        inconsistent_count = 0

        for api_func in api_functions:
            api_name = api_func["name"]
            service_calls = api_func["service_calls"]

            # 查找实际调用的服务方法
            actual_service_calls = [
                call for call in service_calls if call in service_method_names
            ]

            # 预期的服务方法名（基于命名约定）
            expected_service_method = self._predict_service_method_name(api_name)

            # 判断是否一致
            is_consistent = len(actual_service_calls) > 0 and (
                api_name in service_method_names
                or expected_service_method in actual_service_calls
                or any(call == api_name for call in actual_service_calls)
            )

            if not is_consistent:
                inconsistent_count += 1

            mapping_results.append(
                {
                    "api_function": api_name,
                    "actual_service_calls": actual_service_calls,
                    "expected_service_method": expected_service_method,
                    "is_consistent": is_consistent,
                    "http_method": api_func["http_method"],
                    "path": api_func["path"],
                }
            )

        return {
            "total_api_functions": len(api_functions),
            "total_service_methods": len(service_methods),
            "inconsistent_mappings": inconsistent_count,
            "consistency_rate": (
                (len(api_functions) - inconsistent_count) / len(api_functions)
                if api_functions
                else 0
            ),
            "mappings": mapping_results,
        }

    def _predict_service_method_name(self, api_function_name: str) -> str:
        """基于API函数名预测对应的服务方法名"""
        # 常见映射规则
        mappings = {
            "register_user": "create_user",
            "login_user": "authenticate_user",
            "add_item_to_cart": "add_item",
            "update_item_quantity": "update_quantity",
            "delete_cart_item": "delete_item",
            "get_current_user_info": "get_user_by_id",
            "list_users": "get_users",
            "get_order_detail": "get_order_by_id",
            "list_orders": "get_orders_list",
            "create_order": "create_order",
            "get_payment": "get_payment_by_id",
        }

        return mappings.get(api_function_name, api_function_name)

    def print_mapping_report(self, module_name: str, analysis: Dict):
        """打印映射分析报告"""
        mapping = analysis["mapping_analysis"]

        print(f"   📊 API函数: {mapping['total_api_functions']} 个")
        print(f"   🔧 服务方法: {mapping['total_service_methods']} 个")
        print(f"   ⚠️  不一致映射: {mapping['inconsistent_mappings']} 个")
        print(f"   ✅ 一致性率: {mapping['consistency_rate']:.1%}")

        if mapping["inconsistent_mappings"] > 0:
            print(f"   \n   🔍 不一致映射详情:")
            for item in mapping["mappings"]:
                if not item["is_consistent"]:
                    print(
                        f"      • API: {item['api_function']}() → 期望: {item['expected_service_method']}() → 实际: {item['actual_service_calls']}"
                    )

    def generate_corrected_test_template(self, module_name: str) -> str:
        """生成修正后的测试模板"""
        analysis = self.analyze_module(module_name)
        if not analysis:
            return "# ❌ 无法分析模块"

        template_lines = [
            f'"""',
            f"{module_name.title()} Module Standalone Unit Tests - Auto Generated",
            f"",
            f"基于实际API/Service映射自动生成，确保测试代码与实际代码一致。",
            f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            f'分析结果: {analysis["mapping_analysis"]["total_api_functions"]}个API, {analysis["mapping_analysis"]["total_service_methods"]}个服务方法',
            f'一致性率: {analysis["mapping_analysis"]["consistency_rate"]:.1%}',
            f'"""',
            f"import pytest",
            f"from unittest.mock import Mock",
            f"from app.modules.{module_name}.service import *",
            f"",
            f"class Test{module_name.title()}ServiceMethods:",
            f'    """服务方法测试 - 基于实际代码生成"""',
        ]

        # 为每个服务方法生成测试
        for method in analysis["service_methods"]:
            method_name = method["name"]
            is_async = method["is_async"]

            if is_async:
                template_lines.extend(
                    [
                        f"",
                        f"    @pytest.mark.asyncio",
                        f"    async def test_{method_name}(self):",
                        f'        """测试 {method_name} 方法"""',
                        f"        # TODO: 实现 {method_name} 的具体测试逻辑",
                        f"        pass",
                    ]
                )
            else:
                template_lines.extend(
                    [
                        f"",
                        f"    def test_{method_name}(self):",
                        f'        """测试 {method_name} 方法"""',
                        f"        # TODO: 实现 {method_name} 的具体测试逻辑",
                        f"        pass",
                    ]
                )

        # 添加API映射测试
        template_lines.extend(
            [
                f"",
                f"class Test{module_name.title()}APIMappingValidation:",
                f'    """API与Service映射验证测试"""',
            ]
        )

        for mapping in analysis["mapping_analysis"]["mappings"]:
            api_name = mapping["api_function"]
            service_calls = mapping["actual_service_calls"]

            template_lines.extend(
                [
                    f"",
                    f"    def test_{api_name}_service_mapping(self):",
                    f'        """验证 {api_name} API的服务调用映射"""',
                    f"        # API函数: {api_name}",
                    f"        # 实际调用: {service_calls}",
                    f'        # HTTP: {mapping["http_method"]} {mapping["path"]}',
                    f"        assert True  # TODO: 实现映射验证逻辑",
                ]
            )

        return "\n".join(template_lines)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="API与服务层映射分析工具")
    parser.add_argument("--analyze", type=str, help="分析指定模块")
    parser.add_argument("--analyze-all", action="store_true", help="分析所有模块")
    parser.add_argument("--generate-test", type=str, help="为指定模块生成测试模板")
    parser.add_argument("--output", type=str, help="输出文件路径")

    args = parser.parse_args()

    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    analyzer = APIServiceMappingAnalyzer(str(project_root))

    if args.analyze_all:
        print("🔍 分析所有模块的API/Service映射...")
        results = analyzer.analyze_all_modules()

        # 生成总结报告
        total_modules = len(results)
        total_inconsistent = sum(
            r["mapping_analysis"]["inconsistent_mappings"] for r in results.values()
        )

        print(f"\n📊 总结报告:")
        print(f"   📦 分析模块数: {total_modules}")
        print(f"   ⚠️  总不一致映射: {total_inconsistent}")

        # 输出详细结果
        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"   💾 详细结果已保存: {output_path}")

    elif args.analyze:
        print(f"🔍 分析模块: {args.analyze}")
        result = analyzer.analyze_module(args.analyze)

    elif args.generate_test:
        print(f"🛠️  生成测试模板: {args.generate_test}")
        template = analyzer.generate_corrected_test_template(args.generate_test)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(template)
            print(f"   💾 测试模板已保存: {args.output}")
        else:
            print("\n" + "=" * 60)
            print(template)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
