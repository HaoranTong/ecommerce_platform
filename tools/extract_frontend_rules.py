#!/usr/bin/env python3
"""
前端规则提取工具

功能：
  从 design.md 文档中提取 <!-- FRONTEND_RULES --> 标记后的 YAML 代码块，
  并将其解析为字典格式，支持单个文件处理和批量处理两种模式。

使用方法：
  # 提取单个 design.md 文件中的前端规则
  python extract_frontend_rules.py docs/design/modules/user_auth/design.md
  
  # 提取并保存为 JSON 文件
  python extract_frontend_rules.py docs/design/modules/user_auth/design.md -o user_auth_rules.json
  
  # 提取并保存为 YAML 文件
  python extract_frontend_rules.py docs/design/modules/user_auth/design.md -o user_auth_rules.yaml
  
  # 批量处理所有模块的 design.md 文件
  python extract_frontend_rules.py --batch
  
  # 指定模块根目录和输出文件名
  python extract_frontend_rules.py --batch --modules-root docs/design/modules --output-filename frontend-rules.json

输出：
  - 单个文件处理时，如果未指定输出文件，则直接打印到标准输出
  - 批量处理时，会在每个模块目录下生成指定名称的规则文件

应用场景:
  1. 前端开发 - 为前端应用提供配置规则和约束
  2. 自动化构建 - 在构建过程中提取前端配置
  3. 文档同步 - 确保文档中的前端规则与实际代码一致
  4. 代码生成 - 为前端代码生成提供配置信息
"""

import re
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional

def extract_frontend_rules(md_file_path: str) -> Optional[Dict[str, Any]]:
    path = Path(md_file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {md_file_path}")
    
    content = path.read_text(encoding='utf-8')
    
    marker = "<!-- FRONTEND_RULES -->"
    marker_pos = content.find(marker)
    if marker_pos == -1:
        return None
    
    search_start = marker_pos + len(marker)
    code_block_pattern = r"```(?:yaml|yml)\s*\n(.*?)\n```"
    match = re.search(code_block_pattern, content[search_start:], re.DOTALL | re.IGNORECASE)
    
    if not match:
        return None
    
    yaml_content = match.group(1).strip()
    if not yaml_content:
        return None
    
    try:
        data = yaml.safe_load(yaml_content)
        return data if isinstance(data, dict) else {}
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 解析失败（文件: {md_file_path}）: {e}")

def save_to_file(data: dict, output_path: str):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)  # 自动创建目录
    
    if output_path.suffix.lower() in ('.yaml', '.yml'):
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, indent=2, sort_keys=False)
    elif output_path.suffix.lower() == '.json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError("输出文件必须是 .json、.yaml 或 .yml")

# ===== 批量处理入口 =====
def batch_extract_rules(modules_root: str = "docs/design/modules", output_filename: str = "frontend-rules.json"):
    modules_dir = Path(modules_root)
    if not modules_dir.exists():
        print(f"❌ 模块根目录不存在: {modules_dir}")
        return

    success_count = 0
    skip_count = 0
    error_count = 0

    for module_dir in sorted(modules_dir.iterdir()):
        if not module_dir.is_dir():
            continue

        design_md = module_dir / "design.md"
        if not design_md.exists():
            print(f"⚠️ 跳过（无 design.md）: {module_dir.name}")
            skip_count += 1
            continue

        output_file = module_dir / output_filename
        try:
            rules = extract_frontend_rules(str(design_md))
            if rules is None:
                print(f"⏭️ 跳过（无 FRONTEND_RULES）: {module_dir.name}")
                skip_count += 1
                continue

            save_to_file(rules, str(output_file))
            print(f"✅ 生成: {output_file}")
            success_count += 1

        except Exception as e:
            print(f"❌ 失败（{module_dir.name}）: {e}")
            error_count += 1

    print("\n" + "="*50)
    print(f"✅ 成功: {success_count}")
    print(f"⏭️ 跳过: {skip_count}")
    print(f"❌ 错误: {error_count}")
    print("="*50)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="提取单个或批量 design.md 中的 FRONTEND_RULES")
    parser.add_argument("input", nargs="?", help="单个 design.md 路径（可选）")
    parser.add_argument("-o", "--output", help="单个输出文件路径（配合 input 使用）")
    parser.add_argument("--batch", action="store_true", help="批量处理所有模块")
    parser.add_argument("--modules-root", default="docs/design/modules", help="模块根目录")
    parser.add_argument("--output-filename", default="frontend-rules.json", help="批量输出文件名")

    args = parser.parse_args()

    if args.batch:
        batch_extract_rules(
            modules_root=args.modules_root,
            output_filename=args.output_filename
        )
    elif args.input:
        rules = extract_frontend_rules(args.input)
        if rules is None:
            print("❌ 未找到 <!-- FRONTEND_RULES --> 区块")
            exit(1)
        if args.output:
            save_to_file(rules, args.output)
            print(f"✅ 已保存: {args.output}")
        else:
            print(yaml.dump(rules, allow_unicode=True, indent=2))
    else:
        parser.print_help()