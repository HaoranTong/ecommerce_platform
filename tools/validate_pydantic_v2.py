#!/usr/bin/env python3
"""
Pydantic V2 强制合规验证工具

功能：
1. 扫描所有Python文件，检查Pydantic V2合规性
2. 自动检测和修复常见的V1->V2迁移问题
3. 提供实时验证和预防机制

使用方法：
python tools/validate_pydantic_v2.py --check     # 检查模式
python tools/validate_pydantic_v2.py --fix       # 自动修复模式
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class PydanticV2Validator:
    """Pydantic V2合规性验证器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []

        # Pydantic V2迁移规则
        self.v2_patterns = {
            # Config类 -> model_config
            "config_class": {
                "pattern": r"class Config:\s*\n\s*(.+)",
                "replacement": "model_config = ConfigDict(\g<1>)",
                "description": "Config类应改为model_config",
            },
            # @validator -> @field_validator
            "validator_decorator": {
                "pattern": r"@validator\(",
                "replacement": "@field_validator(",
                "description": "@validator应改为@field_validator",
            },
            # @root_validator -> @model_validator
            "root_validator_decorator": {
                "pattern": r"@root_validator\(",
                "replacement": "@model_validator(",
                "description": "@root_validator应改为@model_validator",
            },
            # model.dict() -> model.model_dump()
            "model_dict_method": {
                "pattern": r"\.dict\(\)",
                "replacement": ".model_dump()",
                "description": ".dict()应改为.model_dump()",
            },
            # Model.parse_obj() -> Model.model_validate()
            "parse_obj_method": {
                "pattern": r"\.parse_obj\(",
                "replacement": ".model_validate(",
                "description": ".parse_obj()应改为.model_validate()",
            },
        }

    def scan_directory(self, directory: str) -> List[str]:
        """扫描目录中的Python文件"""
        python_files = []
        scan_path = self.project_root / directory

        for root, dirs, files in os.walk(scan_path):
            # 跳过特定目录
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        return python_files

    def check_file(self, file_path: str) -> List[Dict]:
        """检查单个文件的Pydantic V2合规性"""
        file_issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # 检查各种V2模式
            for rule_name, rule_info in self.v2_patterns.items():
                pattern = rule_info["pattern"]
                matches = re.finditer(pattern, content, re.MULTILINE)

                for match in matches:
                    # 计算行号
                    line_no = content[: match.start()].count("\n") + 1

                    file_issues.append(
                        {
                            "file": file_path,
                            "line": line_no,
                            "rule": rule_name,
                            "description": rule_info["description"],
                            "content": lines[line_no - 1].strip(),
                            "pattern": pattern,
                            "replacement": rule_info["replacement"],
                        }
                    )

        except Exception as e:
            print(f"❌ 检查文件失败 {file_path}: {e}")

        return file_issues

    def check_project(self) -> Dict:
        """检查整个项目的Pydantic V2合规性"""
        print("🔍 开始Pydantic V2合规性检查...")

        # 扫描目标目录
        target_dirs = ["app", "tests"]
        all_issues = []

        for directory in target_dirs:
            if (self.project_root / directory).exists():
                print(f"📁 扫描目录: {directory}")
                files = self.scan_directory(directory)

                for file_path in files:
                    issues = self.check_file(file_path)
                    all_issues.extend(issues)

        # 统计结果
        issue_stats = {}
        for issue in all_issues:
            rule = issue["rule"]
            issue_stats[rule] = issue_stats.get(rule, 0) + 1

        return {
            "total_issues": len(all_issues),
            "issues": all_issues,
            "stats": issue_stats,
        }

    def fix_file(self, file_path: str, dry_run: bool = False) -> int:
        """修复单个文件的Pydantic V2问题"""
        fixes_applied = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # 应用修复规则
            for rule_name, rule_info in self.v2_patterns.items():
                pattern = rule_info["pattern"]
                replacement = rule_info["replacement"]

                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    fixes_applied += content.count(
                        re.search(pattern, content, re.MULTILINE).group(0)
                        if re.search(pattern, content, re.MULTILINE)
                        else ""
                    )
                    content = new_content

            # 写入修复后的内容
            if not dry_run and content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ 修复文件: {file_path} ({fixes_applied}个问题)")

        except Exception as e:
            print(f"❌ 修复文件失败 {file_path}: {e}")

        return fixes_applied

    def fix_project(self, dry_run: bool = False) -> Dict:
        """修复整个项目的Pydantic V2问题"""
        print("🔧 开始Pydantic V2自动修复..." + (" (预览模式)" if dry_run else ""))

        target_dirs = ["app", "tests"]
        total_fixes = 0
        fixed_files = []

        for directory in target_dirs:
            if (self.project_root / directory).exists():
                files = self.scan_directory(directory)

                for file_path in files:
                    fixes = self.fix_file(file_path, dry_run)
                    if fixes > 0:
                        total_fixes += fixes
                        fixed_files.append(file_path)

        return {
            "total_fixes": total_fixes,
            "fixed_files": fixed_files,
            "dry_run": dry_run,
        }

    def generate_report(self, results: Dict) -> None:
        """生成检查报告"""
        print("\n" + "=" * 60)
        print("📊 Pydantic V2合规性检查报告")
        print("=" * 60)

        if results["total_issues"] == 0:
            print("✅ 恭喜！没有发现Pydantic V2合规性问题")
            return

        print(f"❌ 发现 {results['total_issues']} 个问题")
        print("\n📋 问题统计:")
        for rule, count in results["stats"].items():
            rule_desc = self.v2_patterns[rule]["description"]
            print(f"  {rule}: {count}个 - {rule_desc}")

        print(f"\n📄 详细问题列表:")
        for issue in results["issues"][:10]:  # 只显示前10个
            rel_path = os.path.relpath(issue["file"], self.project_root)
            print(f"  {rel_path}:{issue['line']} - {issue['description']}")
            print(f"    {issue['content']}")

        if len(results["issues"]) > 10:
            print(f"  ... 还有 {len(results['issues']) - 10} 个问题")

        print(f"\n💡 修复建议:")
        print(f"   python tools/validate_pydantic_v2.py --fix")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Pydantic V2合规性验证工具")
    parser.add_argument("--check", action="store_true", help="检查模式")
    parser.add_argument("--fix", action="store_true", help="自动修复模式")
    parser.add_argument(
        "--dry-run", action="store_true", help="预览修复（不实际修改文件）"
    )

    args = parser.parse_args()

    if not args.check and not args.fix:
        parser.print_help()
        return

    # 初始化验证器
    project_root = Path(__file__).parent.parent
    validator = PydanticV2Validator(str(project_root))

    if args.check:
        # 检查模式
        results = validator.check_project()
        validator.generate_report(results)

        if results["total_issues"] > 0:
            sys.exit(1)

    elif args.fix:
        # 修复模式
        results = validator.fix_project(dry_run=args.dry_run)

        if args.dry_run:
            print(f"📋 预览: 将修复 {results['total_fixes']} 个问题")
            print("💡 使用 --fix 参数实际执行修复")
        else:
            print(f"✅ 成功修复 {results['total_fixes']} 个问题")
            if results["fixed_files"]:
                print("📄 已修复的文件:")
                for file_path in results["fixed_files"]:
                    rel_path = os.path.relpath(file_path, project_root)
                    print(f"  {rel_path}")


if __name__ == "__main__":
    main()
