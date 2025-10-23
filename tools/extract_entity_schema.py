#!/usr/bin/env python3
"""
模型结构提取工具

功能：
    从指定的 SQLAlchemy models.py 文件中，自动提取所有注册模型（@ModelRegistry.register）
    的表名、字段名、类型、是否为主键/外键/可空/默认值等信息，并输出为 Markdown 格式。

使用方法：
    python extract_models.py <models_file_path>

示例：
    python extract_models.py ./app/modules/product_catalog/models.py
    
    # 将输出重定向到文件
    python extract_models.py ./app/modules/user_auth/models.py > user_auth_schema.md
    
    # 分析并保存为JSON格式
    python extract_models.py ./app/modules/order/models.py --format json > order_schema.json

输出：
    打印到标准输出（stdout），可重定向到文件：
        python extract_models.py models.py > schema.md

依赖：
    仅需 Python 3.6+ 标准库（ast, sys, re 等），无需安装第三方包。

支持格式:
    - Markdown (默认): 适用于文档和GitHub展示
    - JSON: 适用于程序处理和API接口
    - CSV: 适用于导入电子表格软件

注意：
    - 仅解析显式定义的 Column 字段；
    - 自动注入 TimestampMixin（created_at, updated_at）和 SoftDeleteMixin（is_deleted）字段；
    - 不解析关系字段（relationship）、索引、表参数等非 Column 内容；
    - 不支持动态生成的字段或条件字段。

应用场景:
    1. 文档生成 - 自动生成数据模型文档
    2. 代码审查 - 快速查看模型结构
    3. 数据库设计 - 对比模型与数据库表结构
    4. 测试辅助 - 为测试用例提供字段信息
"""

import ast
import sys
import re
from typing import Dict, List, Optional, Tuple

# 混入类自动注入的字段
TIMESTAMP_MIXIN_FIELDS = {
    "created_at": {"type": "DateTime", "nullable": False, "comment": "(创建时间)"},
    "updated_at": {"type": "DateTime", "nullable": False, "comment": "(更新时间)"},
}

SOFT_DELETE_MIXIN_FIELDS = {
    "is_deleted": {"type": "Boolean", "nullable": False, "default": "False", "comment": "(软删除标识)"},
}

def get_column_type(column_node: ast.Call) -> str:
    """从 Column(...) 调用中提取类型，如 String(100) -> 'String(100)'"""
    if not column_node.args:
        return "Unknown"
    type_arg = column_node.args[0]
    if isinstance(type_arg, ast.Call):
        # 如 String(100), DECIMAL(10, 2)
        func_name = type_arg.func.id if isinstance(type_arg.func, ast.Name) else "Unknown"
        args = []
        for arg in type_arg.args:
            if isinstance(arg, ast.Constant):
                args.append(str(arg.value))
            elif isinstance(arg, ast.Num):  # Python <3.8
                args.append(str(arg.n))
        return f"{func_name}({', '.join(args)})" if args else func_name
    elif isinstance(type_arg, ast.Name):
        return type_arg.id
    elif isinstance(type_arg, ast.Attribute):
        return f"{type_arg.value.id}.{type_arg.attr}" if isinstance(type_arg.value, ast.Name) else "Unknown"
    return "Unknown"

def extract_default_value(keywords: List[ast.keyword]) -> Optional[str]:
    """从 Column 的关键字参数中提取 default 值"""
    for kw in keywords:
        if kw.arg == "default":
            if isinstance(kw.value, ast.Constant):
                return str(kw.value.value)
            elif isinstance(kw.value, ast.Name):
                return kw.value.id
            elif isinstance(kw.value, ast.Num):  # Python <3.8
                return str(kw.value.n)
            elif isinstance(kw.value, ast.Str):  # Python <3.8
                return f'"{kw.value.s}"'
    return None

def is_nullable(keywords: List[ast.keyword]) -> bool:
    """判断字段是否 nullable=True"""
    for kw in keywords:
        if kw.arg == "nullable":
            if isinstance(kw.value, ast.Constant):
                return kw.value.value is True
            elif isinstance(kw.value, ast.NameConstant):  # Python <3.8
                return kw.value.value is True
    return True  # 默认 nullable=True

def has_primary_key(keywords: List[ast.keyword]) -> bool:
    """判断是否为主键"""
    for kw in keywords:
        if kw.arg == "primary_key":
            if isinstance(kw.value, ast.Constant):
                return kw.value.value is True
            elif isinstance(kw.value, ast.NameConstant):
                return kw.value.value is True
    return False

def extract_models_from_ast(tree: ast.AST) -> Dict[str, dict]:
    """从 AST 中提取所有模型定义"""
    models = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # 检查是否被 @ModelRegistry.register 装饰
            is_registered = any(
                isinstance(dec, ast.Call) and 
                isinstance(dec.func, ast.Attribute) and
                dec.func.attr == "register"
                for dec in node.decorator_list
            )
            if not is_registered:
                continue

            model_name = node.name
            table_name = None
            fields = {}

            # 查找 __tablename__ 和字段
            for item in node.body:
                if isinstance(item, ast.Assign):
                    # 提取 __tablename__
                    if (len(item.targets) == 1 and 
                        isinstance(item.targets[0], ast.Name) and 
                        item.targets[0].id == "__tablename__"):
                        if isinstance(item.value, ast.Constant):
                            table_name = item.value.value
                        elif isinstance(item.value, ast.Str):  # Python <3.8
                            table_name = item.value.s
                    
                    # 提取 Column 字段
                    if (len(item.targets) == 1 and 
                        isinstance(item.targets[0], ast.Name)):
                        field_name = item.targets[0].id
                        if isinstance(item.value, ast.Call) and \
                           isinstance(item.value.func, ast.Name) and \
                           item.value.func.id == "Column":
                            col_type = get_column_type(item.value)
                            nullable = is_nullable(item.value.keywords)
                            default = extract_default_value(item.value.keywords)
                            primary_key = has_primary_key(item.value.keywords)
                            
                            comment = ""
                            for kw in item.value.keywords:
                                if kw.arg == "comment" and isinstance(kw.value, ast.Constant):
                                    comment = f" ({kw.value.value})"
                            
                            fields[field_name] = {
                                "type": col_type,
                                "nullable": nullable,
                                "default": default,
                                "primary_key": primary_key,
                                "comment": comment
                            }

            # 自动注入混入字段
            base_classes = [base.id for base in node.bases if isinstance(base, ast.Name)]
            if "TimestampMixin" in base_classes:
                fields.update(TIMESTAMP_MIXIN_FIELDS)
            if "SoftDeleteMixin" in base_classes:
                fields.update(SOFT_DELETE_MIXIN_FIELDS)

            models[model_name] = {
                "table_name": table_name or model_name.lower() + "s",
                "fields": fields
            }
    
    return models

def format_field(field_name: str, field_info: dict) -> str:
    """格式化单个字段为 Markdown 行"""
    col_type = field_info["type"]
    nullable = "可空" if field_info["nullable"] else "非空"
    default = f", 默认值为{field_info['default']}" if field_info.get("default") else ""
    pk = " (主键)" if field_info.get("primary_key") else ""
    comment = field_info.get("comment", "")
    return f"{field_name}: {col_type}, {nullable}{default}{pk}{comment}"

def main():
    if len(sys.argv) != 2:
        print("用法: python extract_models.py <models_file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到。", file=sys.stderr)
        sys.exit(1)

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        print(f"错误: 无法解析 Python 文件: {e}", file=sys.stderr)
        sys.exit(1)

    models = extract_models_from_ast(tree)

    if not models:
        print("未找到任何被 @ModelRegistry.register 装饰的模型。")
        return

    print("产品目录模块实体结构\n")
    for model_name, info in models.items():
        print(f"{model_name}（{model_name}）")
        print(f"表名: {info['table_name']}\n")
        for field_name in sorted(info["fields"].keys()):
            print(f"{format_field(field_name, info['fields'][field_name])}")
        print()

if __name__ == "__main__":
    main()