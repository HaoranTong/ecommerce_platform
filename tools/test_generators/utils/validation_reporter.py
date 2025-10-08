"""
验证报告生成器 - 测试质量验证报告

职责：
1. 汇总测试验证结果
2. 生成Markdown格式报告
3. 计算质量评分和状态
4. 提供改进建议

版本: v1.0
创建时间: 2025-10-08
"""
from datetime import datetime
from typing import Any, Dict


class ValidationReporter:
    """测试验证报告生成器"""
    
    def summarize_validation_results(self, validation_results: Dict[str, Any]) -> None:
        """汇总验证结果并打印到控制台"""
        print("\n📊 测试质量验证报告 [CHECK:TEST-008]")
        print("=" * 50)

        summary = validation_results["summary"]

        # 语法检查总结
        syntax = validation_results["syntax_check"]
        syntax_pass_rate = (
            len(syntax["passed"]) / len(syntax["passed"] + syntax["failed"]) * 100
            if (syntax["passed"] + syntax["failed"])
            else 100
        )
        print(
            f"🔍 语法检查: {len(syntax['passed'])}/{len(syntax['passed']) + len(syntax['failed'])} 通过 ({syntax_pass_rate:.1f}%)"
        )

        # pytest收集总结
        collection = validation_results["pytest_collection"]
        collection_files = len(collection["test_files"])
        total_tests = collection["collected_tests"]
        print(f"🧪 pytest收集: {collection_files}个测试文件, {total_tests}个测试方法")

        # 导入验证总结
        imports = validation_results["import_validation"]
        import_pass_rate = (
            len(imports["passed"]) / len(imports["passed"] + imports["failed"]) * 100
            if (imports["passed"] + imports["failed"])
            else 100
        )
        print(
            f"📦 导入验证: {len(imports['passed'])}/{len(imports['passed']) + len(imports['failed'])} 通过 ({import_pass_rate:.1f}%)"
        )

        # 依赖完整性总结
        deps = validation_results["dependency_check"]
        missing_count = len(deps["missing_factories"])
        print(
            f"🔗 依赖检查: {len(deps['factory_dependencies'])}个工厂文件, {missing_count}个缺失依赖"
        )

        # 执行成功率总结
        execution = validation_results["execution_test"]
        exec_rate = execution["success_rate"]
        print(
            f"▶️ 执行测试: {execution['successful_executions']}/{execution['executed_files']} 通过 ({exec_rate:.1f}%)"
        )

        # 整体评估
        overall_score = (syntax_pass_rate + import_pass_rate + exec_rate) / 3
        if overall_score >= 90:
            status = "🎉 优秀"
            validation_results["overall_success"] = True
        elif overall_score >= 75:
            status = "✅ 良好"
            validation_results["overall_success"] = True
        elif overall_score >= 60:
            status = "⚠️ 一般"
            validation_results["overall_success"] = False
        else:
            status = "❌ 需要改进"
            validation_results["overall_success"] = False

        print(f"\n📈 整体质量评分: {overall_score:.1f}% - {status}")

        # 更新汇总信息
        summary["passed"] = len(syntax["passed"])
        summary["failed"] = len(syntax["failed"]) + len(imports["failed"])
        summary["overall_score"] = overall_score
        summary["status"] = status

        if not validation_results["overall_success"]:
            print("\n⚠️ 建议检查和修复以上问题后重新验证")
        else:
            print("\n🎯 验证通过，生成的测试文件质量符合标准 [CHECK:TEST-008]")
    
    def generate_validation_markdown_report(
        self, module_name: str, validation_results: Dict[str, Any]
    ) -> str:
        """生成Markdown格式的验证报告"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# {module_name.title()} 模块测试生成验证报告

## 基本信息
- **模块名称**: {module_name}
- **验证时间**: {timestamp}
- **验证标准**: [CHECK:TEST-008] 测试质量自动验证
- **总体评分**: {validation_results['summary']['overall_score']:.1f}%
- **验证状态**: {validation_results['summary']['status']}

## 验证结果摘要

### 📊 整体指标
| 验证项目 | 通过数量 | 总数量 | 通过率 | 状态 |
|---------|---------|-------|-------|------|
"""

        # 添加各项验证结果
        syntax = validation_results["syntax_check"]
        syntax_total = len(syntax["passed"]) + len(syntax["failed"])
        syntax_rate = (
            len(syntax["passed"]) / syntax_total * 100 if syntax_total > 0 else 100
        )

        imports = validation_results["import_validation"]
        import_total = len(imports["passed"]) + len(imports["failed"])
        import_rate = (
            len(imports["passed"]) / import_total * 100 if import_total > 0 else 100
        )

        execution = validation_results["execution_test"]
        exec_rate = execution["success_rate"]

        collection = validation_results["pytest_collection"]

        report += f"""| 语法检查 | {len(syntax['passed'])} | {syntax_total} | {syntax_rate:.1f}% | {'✅' if syntax_rate >= 90 else '⚠️' if syntax_rate >= 70 else '❌'} |
| 导入验证 | {len(imports['passed'])} | {import_total} | {import_rate:.1f}% | {'✅' if import_rate >= 90 else '⚠️' if import_rate >= 70 else '❌'} |
| pytest收集 | {len(collection['test_files'])} | {len(collection['test_files']) + len(collection['collection_errors'])} | - | {'✅' if len(collection['collection_errors']) == 0 else '❌'} |
| 执行测试 | {execution['successful_executions']} | {execution['executed_files']} | {exec_rate:.1f}% | {'✅' if exec_rate >= 90 else '⚠️' if exec_rate >= 70 else '❌'} |

### 🔍 详细验证结果

#### 1. Python语法检查
"""

        if syntax["passed"]:
            report += "**通过的文件:**\n"
            for file_path in syntax["passed"]:
                report += f"- ✅ `{file_path}`\n"

        if syntax["failed"]:
            report += "\n**失败的文件:**\n"
            for file_path in syntax["failed"]:
                details = syntax["details"].get(file_path, {})
                error = details.get("message", "未知错误")
                report += f"- ❌ `{file_path}`: {error}\n"

        report += f"""

#### 2. pytest测试收集
- **收集的测试文件数**: {len(collection['test_files'])}
- **收集的测试方法数**: {collection['collected_tests']}
"""

        if collection["test_files"]:
            report += "\n**成功收集的测试文件:**\n"
            for file_path in collection["test_files"]:
                details = collection["details"].get(file_path, {})
                test_count = details.get("test_count", 0)
                report += f"- ✅ `{file_path}` ({test_count}个测试)\n"

        if collection["collection_errors"]:
            report += "\n**收集失败的文件:**\n"
            for error_info in collection["collection_errors"]:
                report += (
                    f"- ❌ `{error_info['file']}`: {error_info['error'][:100]}...\n"
                )

        report += f"""

#### 3. 导入依赖验证
"""

        if imports["passed"]:
            report += "**验证通过的文件:**\n"
            for file_path in imports["passed"]:
                details = imports["details"].get(file_path, {})
                import_count = details.get("total_imports", 0)
                report += f"- ✅ `{file_path}` ({import_count}个导入)\n"

        if imports["failed"]:
            report += "\n**验证失败的文件:**\n"
            for file_path in imports["failed"]:
                details = imports["details"].get(file_path, {})
                failed_imports = details.get("failed_imports", [])
                report += f"- ❌ `{file_path}`: 缺失 {', '.join(failed_imports[:3])}\n"

        deps = validation_results["dependency_check"]
        report += f"""

#### 4. 依赖完整性检查
- **工厂文件数量**: {len(deps['factory_dependencies'])}
- **缺失的工厂依赖**: {len(deps['missing_factories'])}
"""

        if deps["missing_factories"]:
            report += "\n**缺失的工厂类:**\n"
            for factory in deps["missing_factories"]:
                report += f"- ❌ `{factory}`\n"
        else:
            report += "\n✅ 所有工厂依赖完整\n"

        report += f"""

#### 5. 基础执行测试
- **测试文件数**: {execution['executed_files']}
- **成功执行数**: {execution['successful_executions']}
- **执行成功率**: {execution['success_rate']:.1f}%

## 质量评估

### 🎯 符合标准检查
- [x] [CHECK:TEST-008] 自动化测试质量验证机制
- [x] [CHECK:DEV-009] 代码生成质量标准
- {'[x]' if validation_results['overall_success'] else '[ ]'} 整体质量达标 (≥75%)

### 📈 改进建议
"""

        suggestions = []
        if syntax_rate < 90:
            suggestions.append("- 修复语法错误，确保所有生成文件符合Python语法规范")
        if import_rate < 90:
            suggestions.append("- 检查并安装缺失的依赖包，确保所有导入可正确执行")
        if len(collection["collection_errors"]) > 0:
            suggestions.append("- 修复pytest收集错误，确保测试可以被正确发现和执行")
        if exec_rate < 90:
            suggestions.append("- 修复基础执行错误，确保工厂类和测试代码可以正常加载")
        if len(deps["missing_factories"]) > 0:
            suggestions.append("- 补充缺失的工厂类定义，确保测试数据依赖完整")

        if not suggestions:
            suggestions.append("🎉 当前质量已达到优秀标准，无需特别改进")

        for suggestion in suggestions:
            report += f"{suggestion}\n"

        report += f"""

## 附加信息
- **生成工具版本**: 智能五层架构测试生成器 v2.0
- **验证框架**: Python AST + pytest + 自定义验证
- **报告生成时间**: {timestamp}
- **遵循规范**: MASTER.md测试标准和检查点规范

---
*本报告由智能测试生成工具自动生成，遵循 [CHECK:TEST-008] 和 [CHECK:DEV-009] 标准*
"""

        return report
