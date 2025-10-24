#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量从各模块的 schemas.py 中提取 Pydantic v2 模型，生成 Markdown 和 JSON Schema 文档。

目录结构假设：
app/
├── modules/
│   ├── user_auth/
│   │   └── schemas.py
│   ├── product_catalog/
│   │   └── schemas.py
│   └── ...
"""

import ast
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set,Tuple

# ==============================
# 配置区（可根据需要调整）
# ==============================
MODULES_DIR = Path("app") / "modules"  # 业务模块根目录
SCHEMA_FILENAME = "schemas.py"

# 要跳过的通用模型类名（通常是包装器或基础类）
SKIP_MODEL_NAMES: Set[str] = {
    "BaseModel",
    "BaseSchema",
    "StandardResponse",
    "ErrorResponse",
    "TimestampSchema",
    "TokenData",
    "TokenRefresh",
    "SendVerificationCode",  # 可选：按需保留或跳过
}

# 只保留我们认为是“业务实体”的模型（可选：改为白名单模式）
# 如果留空，则自动排除 SKIP_MODEL_NAMES 中的类
BUSINESS_MODEL_WHITELIST: Set[str] = set()  # 例如 {"UserRead", "ProductDetail", ...}

# ==============================
# 工具函数
# ==============================

def is_basemodel_subclass(node: ast.ClassDef, basemodel_names: Set[str]) -> bool:
    """判断该类是否直接或间接继承自 BaseModel（通过名称匹配）"""
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id in basemodel_names:
            return True
        if isinstance(base, ast.Attribute):
            # 处理如 pydantic.BaseModel 的情况（但通常不会出现在 schema.py 中）
            if base.attr == "BaseModel":
                return True
    return False

def get_full_type_annotation(annotation) -> str:
    """将 AST 类型注解转为字符串"""
    try:
        return ast.unparse(annotation)
    except Exception:
        return str(annotation).replace("<ast.", "").rstrip(">")

def extract_field_info(assign: ast.AnnAssign) -> Tuple[str, str, bool, Optional[str], Optional[str]]:
    """从 AnnAssign 节点提取字段信息"""
    field_name = assign.target.id  # type: ignore
    field_type = get_full_type_annotation(assign.annotation)
    
    has_default = assign.value is not None
    required = not has_default and "Optional[" not in field_type and field_type != "None"

    default_value = None
    description = None

    # 如果有 Field(...)，尝试提取 description 和默认值
    if assign.value and isinstance(assign.value, ast.Call) and isinstance(assign.value.func, ast.Name):
        if assign.value.func.id == "Field":
            # 提取关键字参数
            for kw in assign.value.keywords:
                if kw.arg == "description" and isinstance(kw.value, ast.Constant):
                    description = kw.value.value
                elif kw.arg is None:  # *args 不处理
                    continue
                # 默认值通常是第一个位置参数（但 Field 通常用关键字）
                if len(assign.value.args) > 0 and not isinstance(assign.value.args[0], ast.Constant):
                    default_value = assign.value.args[0].value

    # 如果没有 Field，但有常量默认值
    if assign.value and isinstance(assign.value, ast.Constant):
        default_value = assign.value.value

    return field_name, field_type, required, default_value, description

def parse_schema_file(file_path: Path) -> Dict[str, Any]:
    """解析单个 schemas.py，返回模型字典"""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # 第一步：收集所有 BaseModel 子类名称（包括间接）
    basemodel_subclasses: Set[str] = set()
    class_nodes: Dict[str, ast.ClassDef] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_nodes[node.name] = node
            # 简单判断：只要继承了 BaseModel 或已知子类，就标记
            if any(
                (isinstance(base, ast.Name) and base.id in ("BaseModel", "BaseSchema"))
                or (isinstance(base, ast.Attribute) and base.attr == "BaseModel")
                for base in node.bases
            ):
                basemodel_subclasses.add(node.name)

    # 第二步：递归扩展继承链（简单处理一层继承）
    extended = True
    while extended:
        extended = False
        for name, node in class_nodes.items():
            if name in basemodel_subclasses:
                continue
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id in basemodel_subclasses:
                    basemodel_subclasses.add(name)
                    extended = True

    # 第三步：提取每个模型的字段
    models = {}
    for name, node in class_nodes.items():
        if name in SKIP_MODEL_NAMES:
            continue
        if BUSINESS_MODEL_WHITELIST and name not in BUSINESS_MODEL_WHITELIST:
            continue
        if name not in basemodel_subclasses:
            continue

        fields = {}
        # 先收集父类字段（仅一层，简单处理）
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in models:
                # 继承父类字段（浅拷贝）
                fields.update(models[base.id].get("fields", {}))

        # 再收集自身字段
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                try:
                    fname, ftype, required, default, desc = extract_field_info(item)
                    fields[fname] = {
                        "type": ftype,
                        "required": required,
                        "default": default,
                        "description": desc,
                    }
                except Exception as e:
                    print(f"⚠️ 解析字段失败 {file_path}:{name}.{item.target.id} - {e}")

        models[name] = {
            "name": name,
            "fields": fields,
            "source_file": str(file_path),
        }

    return models

def render_markdown(models: Dict[str, Any], output_path: Path):
    """生成 schema.md"""
    lines = []
    lines.append("# API Schemas\n\n")
    lines.append("> 自动生成于 schemas.py，勿手动修改\n\n")

    for name, info in sorted(models.items()):
        lines.append(f"## `{name}`\n\n")
        if info["fields"]:
            lines.append("| 字段 | 类型 | 必填 | 默认值 | 描述 |\n")
            lines.append("|------|------|------|--------|------|\n")
            for fname, f in info["fields"].items():
                req = "✅" if f["required"] else "❌"
                default = f["default"] if f["default"] is not None else ""
                desc = f["description"] or ""
                lines.append(f"| `{fname}` | `{f['type']}` | {req} | `{default}` | {desc} |\n")
        else:
            lines.append("无字段。\n")
        lines.append("\n---\n\n")

    output_path.write_text("".join(lines), encoding="utf-8")

def convert_to_json_schema(models: Dict[str, Any]) -> Dict[str, Any]:
    """生成符合 JSON Schema Draft 2020-12 的结构（简化版）"""
    definitions = {}
    for name, info in models.items():
        props = {}
        required = []
        for fname, f in info["fields"].items():
            # 简化类型映射（实际可更复杂）
            type_map = {
                "str": "string",
                "int": "integer",
                "float": "number",
                "bool": "boolean",
                "datetime": "string",  # format: date-time
            }
            raw_type = f["type"].replace("Optional[", "").replace("]", "").split(".")[-1]
            json_type = type_map.get(raw_type, "string")

            prop = {"type": json_type}
            if f["description"]:
                prop["description"] = f["description"]
            if f["required"]:
                required.append(fname)
            props[fname] = prop

        definitions[name] = {
            "type": "object",
            "properties": props,
            "required": required,
        }

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://your-api.com/schemas",
        "definitions": definitions,
    }

# ==============================
# 主程序
# ==============================

def main():
    print("🔍 扫描模块中的 schemas.py 文件...")
    schema_files = list(MODULES_DIR.rglob(f"*/{SCHEMA_FILENAME}"))

    if not schema_files:
        print(f"❌ 未找到任何 {SCHEMA_FILENAME} 文件，请检查 MODULES_DIR 路径。")
        return

    print(f"✅ 找到 {len(schema_files)} 个 schemas.py 文件")

    for schema_file in schema_files:
        print(f"\n📄 处理: {schema_file}")
        try:
            models = parse_schema_file(schema_file)
            if not models:
                print("  ⚠️ 未提取到有效模型")
                continue

            module_dir = schema_file.parent
            md_path = module_dir / "schema.md"
            json_path = module_dir / "api.schema.json"

            render_markdown(models, md_path)
            json_schema = convert_to_json_schema(models)
            json_path.write_text(json.dumps(json_schema, indent=2, ensure_ascii=False), encoding="utf-8")

            print(f"  ✅ 生成: {md_path.name}, {json_path.name}")
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")

    print("\n🎉 所有模块处理完成！")

if __name__ == "__main__":
    main()