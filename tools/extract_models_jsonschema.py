#!/usr/bin/env python3
"""
模型提取工具 - JSON Schema 输出版（供前端 AI 设计使用）

功能：
  从 models.py 提取 SQLAlchemy 模型，输出标准 JSON Schema（Draft 7），
  可直接用于前端表单生成、AI 设计工具、API 文档等。

使用方法:
  # 提取单个模块的模型并输出到控制台
  python extract_models_jsonschema.py ./app/modules/user_auth/models.py
  
  # 提取模型并保存为JSON文件
  python extract_models_jsonschema.py ./app/modules/user_auth/models.py > user_auth.schema.json
  
  # 在管道中使用
  python extract_models_jsonschema.py ./app/modules/product_catalog/models.py | jq '.["$defs"].Product'

输出示例:
  {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/product-catalog-schemas",
    "title": "Product Catalog Schemas",
    "$defs": {
      "Product": { ... },
      "SKU": { ... }
    }
  }

特点:
  - 自动类型映射（String → string, Integer → integer, DateTime → string + format: date-time）
  - 提取 maxLength（正确解析 String(100)）
  - 启发式 enum（基于字段名）
  - 标记 required 字段（nullable=False）
  - 外键字段标注 "x-foreign-key": "Brand.id"
  - 混入字段（created_at, is_deleted）自动注入

应用场景:
  1. 前端开发 - 为前端表单生成提供数据模型定义
  2. API文档 - 生成标准的API数据结构文档
  3. 测试数据生成 - 为自动化测试提供数据结构参考
  4. AI辅助开发 - 为AI设计工具提供标准的数据模型
  5. 数据验证 - 在前端进行数据格式验证
"""

import ast
import sys
import json
import re
from typing import Dict, Any, List, Optional

# 启发式枚举值映射（可根据实际代码增强）
ENUM_HINTS = {
    "status": ["draft", "published", "archived"],
    "tag_type": ["general", "promotion", "feature"],
    "attribute_type": ["text", "number", "boolean", "select"]
}

def map_sqlalchemy_type_to_json(col_type: str, field_name: str = "") -> Dict[str, Any]:
    """将 SQLAlchemy 类型映射为 JSON Schema 类型定义"""
    result: Dict[str, Any] = {}

    if col_type.startswith("String"):
        result["type"] = "string"
        # 正确匹配 String(100) 中的数字
        match = re.search(r"String\((\d+)\)", col_type)
        if match:
            result["maxLength"] = int(match.group(1))
    elif col_type.startswith("Text"):
        result["type"] = "string"
    elif col_type.startswith("Integer"):
        result["type"] = "integer"
    elif col_type.startswith("Boolean"):
        result["type"] = "boolean"
    elif col_type.startswith("DECIMAL") or col_type.startswith("Float"):
        result["type"] = "number"
    elif col_type in ("DateTime", "Date"):
        result["type"] = "string"
        result["format"] = "date-time" if col_type == "DateTime" else "date"
    else:
        result["type"] = "string"  # fallback

    # 启发式添加 enum
    base_name = field_name.lower()
    for key, enum_vals in ENUM_HINTS.items():
        if key in base_name:
            result["enum"] = enum_vals
            break

    return result

def extract_field_schema(assign_node, model_name: str) -> Optional[Dict[str, Any]]:
    if not (isinstance(assign_node, ast.Assign) and len(assign_node.targets) == 1):
        return None
    target = assign_node.targets[0]
    if not isinstance(target, ast.Name):
        return None
    field_name = target.id
    if field_name.startswith("__"):
        return None
    if not (isinstance(assign_node.value, ast.Call) and assign_node.value.func.id == "Column"):
        return None

    col_call = assign_node.value
    col_type_str = "Unknown"
    if col_call.args:
        type_arg = col_call.args[0]
        if isinstance(type_arg, ast.Call):
            func_name = type_arg.func.id if isinstance(type_arg.func, ast.Name) else "Unknown"
            args = []
            for arg in type_arg.args:
                if isinstance(arg, ast.Constant):
                    args.append(str(arg.value))
                elif hasattr(arg, 'n'):  # Python <3.8
                    args.append(str(arg.n))
            col_type_str = f"{func_name}({', '.join(args)})" if args else func_name
        elif isinstance(type_arg, ast.Name):
            col_type_str = type_arg.id

    # 提取关键字参数
    nullable = True
    default = None
    comment = ""
    for kw in col_call.keywords:
        if kw.arg == "nullable":
            if isinstance(kw.value, ast.Constant):
                nullable = kw.value.value
            else:
                nullable = True
        elif kw.arg == "default":
            if isinstance(kw.value, ast.Constant):
                default = kw.value.value
            else:
                default = str(kw.value)
        elif kw.arg == "comment" and isinstance(kw.value, ast.Constant):
            comment = kw.value.value

    # 构建 schema
    schema = map_sqlalchemy_type_to_json(col_type_str, field_name)
    if comment:
        schema["description"] = comment
    if default is not None:
        schema["default"] = default

    # 标记外键（启发式）
    if field_name.endswith("_id") and "Integer" in col_type_str:
        ref_table = field_name[:-3]  # brand_id -> brand
        schema["x-foreign-key"] = f"{ref_table.capitalize()}.id"

    return {
        "field_name": field_name,
        "schema": schema,
        "required": not nullable
    }

def inject_mixin_fields(model_name: str, base_classes: List[str]) -> List[Dict[str, Any]]:
    """注入混入类字段的 schema"""
    fields = []
    if "TimestampMixin" in base_classes:
        fields.extend([
            {"field_name": "created_at", "schema": {"type": "string", "format": "date-time", "description": "(创建时间)"}, "required": True},
            {"field_name": "updated_at", "schema": {"type": "string", "format": "date-time", "description": "(更新时间)"}, "required": True}
        ])
    if "SoftDeleteMixin" in base_classes:
        fields.append({
            "field_name": "is_deleted",
            "schema": {"type": "boolean", "default": False, "description": "(软删除标识)"},
            "required": True
        })
    return fields

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_models_jsonschema.py <models.py>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    schemas = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        # 检查是否被 @ModelRegistry.register 装饰
        if not any(
            isinstance(d, ast.Call) and getattr(d.func, 'attr', None) == 'register'
            for d in node.decorator_list
        ):
            continue

        model_name = node.name
        table_name = model_name.lower() + "s"
        base_classes = [b.id for b in node.bases if isinstance(b, ast.Name)]
        fields_info = []

        for item in node.body:
            # 处理 __tablename__
            if isinstance(item, ast.Assign) and len(item.targets) == 1:
                target = item.targets[0]
                if isinstance(target, ast.Name) and target.id == "__tablename__":
                    if isinstance(item.value, ast.Constant):
                        table_name = item.value.value
                    continue

            field_info = extract_field_schema(item, model_name)
            if field_info:
                fields_info.append(field_info)

        # 注入混入字段
        fields_info.extend(inject_mixin_fields(model_name, base_classes))

        # 构建 JSON Schema
        properties = {}
        required = []
        for info in fields_info:
            properties[info["field_name"]] = info["schema"]
            if info["required"]:
                required.append(info["field_name"])

        schema = {
            "type": "object",
            "title": f"{model_name} Model",
            "description": f"Table: {table_name}",
            "properties": properties,
            "required": required,
            "additionalProperties": False
        }

        schemas[model_name] = schema

    # 输出完整 JSON Schema
    output = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://your-domain.com/schemas/product-catalog.json",
        "title": "Product Catalog Domain Models",
        "$defs": schemas
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()