#!/usr/bin/env python3
"""
智能模型分析器 - 自动解析SQLAlchemy模型结构

核心功能：
1. 自动解析models.py中的所有模型类
2. 分析字段类型、约束、关系
3. 生成模型测试所需的完整元数据
4. 支持复杂关系和混入(Mixin)分析

使用方法:
    python tools/model_analyzer.py user_auth
    python tools/model_analyzer.py shopping_cart --detailed
"""

import argparse
import ast
import importlib.util
import inspect
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class FieldInfo:
    """字段信息数据类"""

    name: str
    column_type: str
    python_type: str
    nullable: bool
    primary_key: bool
    foreign_key: Optional[str]
    unique: bool
    default: Any
    constraints: List[str]


@dataclass
class RelationshipInfo:
    """关系信息数据类"""

    name: str
    related_model: str
    relationship_type: str  # one-to-one, one-to-many, many-to-many
    back_populates: Optional[str]
    cascade: Optional[str]
    foreign_keys: List[str]


@dataclass
class ModelInfo:
    """模型信息数据类"""

    name: str
    tablename: str
    fields: List[FieldInfo]
    relationships: List[RelationshipInfo]
    mixins: List[str]
    docstring: Optional[str]
    primary_keys: List[str]
    unique_constraints: List[List[str]]


class SQLAlchemyModelAnalyzer:
    """SQLAlchemy模型智能分析器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.models_cache = {}

    def analyze_module(self, module_name: str) -> Dict[str, ModelInfo]:
        """分析指定模块中的所有模型"""
        print(f"🔍 开始分析模块: {module_name}")

        # 1. 定位模块文件
        models_file = self.project_root / f"app/modules/{module_name}/models.py"
        if not models_file.exists():
            raise FileNotFoundError(f"模型文件不存在: {models_file}")

        # 2. AST语法分析
        ast_models = self._analyze_ast(models_file)
        print(f"📋 AST分析发现 {len(ast_models)} 个模型类")

        # 3. 运行时分析（导入模块获取完整信息）
        runtime_models = self._analyze_runtime(module_name)
        print(f"🏃 运行时分析发现 {len(runtime_models)} 个模型类")

        # 4. 合并分析结果
        merged_models = self._merge_analysis_results(ast_models, runtime_models)
        print(f"✅ 合并完成，共分析 {len(merged_models)} 个模型")

        return merged_models

    def _analyze_ast(self, models_file: Path) -> Dict[str, Dict]:
        """AST语法分析 - 获取源代码结构"""
        with open(models_file, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        models = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否是SQLAlchemy模型类
                if self._is_sqlalchemy_model(node):
                    model_info = self._extract_model_info_from_ast(node)
                    models[node.name] = model_info

        return models

    def _is_sqlalchemy_model(self, class_node: ast.ClassDef) -> bool:
        """检查类是否是SQLAlchemy模型"""
        # 检查是否继承自Base或包含__tablename__
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "Base":
                return True

        # 检查是否有__tablename__属性
        for item in class_node.body:
            if isinstance(item, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "__tablename__"
                for target in item.targets
            ):
                return True

        return False

    def _extract_model_info_from_ast(self, class_node: ast.ClassDef) -> Dict:
        """从AST节点提取模型信息"""
        model_info = {
            "name": class_node.name,
            "tablename": None,
            "fields": [],
            "relationships": [],
            "mixins": [],
            "docstring": ast.get_docstring(class_node),
        }

        # 提取基类(混入)
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                model_info["mixins"].append(base.id)

        # 分析类体内容
        for item in class_node.body:
            if isinstance(item, ast.Assign):
                self._analyze_assignment(item, model_info)

        return model_info

    def _analyze_assignment(self, assign_node: ast.Assign, model_info: Dict):
        """分析赋值语句 - 提取字段和关系定义"""
        for target in assign_node.targets:
            if isinstance(target, ast.Name):
                attr_name = target.id

                if attr_name == "__tablename__":
                    # 提取表名
                    if isinstance(assign_node.value, ast.Constant):
                        model_info["tablename"] = assign_node.value.value

                elif isinstance(assign_node.value, ast.Call):
                    # 分析函数调用 - Column或relationship
                    func_name = self._get_function_name(assign_node.value.func)

                    if func_name == "Column":
                        field_info = self._analyze_column_definition(
                            attr_name, assign_node.value
                        )
                        model_info["fields"].append(field_info)

                    elif func_name == "relationship":
                        rel_info = self._analyze_relationship_definition(
                            attr_name, assign_node.value
                        )
                        model_info["relationships"].append(rel_info)

    def _get_function_name(self, func_node) -> str:
        """获取函数名称"""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        return ""

    def _analyze_column_definition(self, field_name: str, call_node: ast.Call) -> Dict:
        """分析Column定义"""
        field_info = {
            "name": field_name,
            "column_type": None,
            "nullable": True,  # SQLAlchemy默认
            "primary_key": False,
            "foreign_key": None,
            "unique": False,
            "default": None,
            "constraints": [],
        }

        # 分析位置参数 - 通常第一个是类型
        if call_node.args:
            type_arg = call_node.args[0]
            field_info["column_type"] = self._extract_column_type(type_arg)

        # 分析关键字参数
        for keyword in call_node.keywords:
            if keyword.arg == "nullable":
                field_info["nullable"] = self._extract_boolean_value(keyword.value)
            elif keyword.arg == "primary_key":
                field_info["primary_key"] = self._extract_boolean_value(keyword.value)
            elif keyword.arg == "unique":
                field_info["unique"] = self._extract_boolean_value(keyword.value)
            elif keyword.arg == "default":
                field_info["default"] = self._extract_default_value(keyword.value)

        return field_info

    def _extract_column_type(self, type_node) -> str:
        """提取列类型"""
        if isinstance(type_node, ast.Name):
            return type_node.id
        elif isinstance(type_node, ast.Call):
            return self._get_function_name(type_node.func)
        return "Unknown"

    def _extract_boolean_value(self, value_node) -> bool:
        """提取布尔值"""
        if isinstance(value_node, ast.Constant):
            return bool(value_node.value)
        elif isinstance(value_node, ast.NameConstant):  # Python < 3.8
            return bool(value_node.value)
        return False

    def _extract_default_value(self, value_node) -> Any:
        """提取默认值"""
        if isinstance(value_node, ast.Constant):
            return value_node.value
        elif isinstance(value_node, ast.NameConstant):  # Python < 3.8
            return value_node.value
        return None

    def _analyze_relationship_definition(
        self, rel_name: str, call_node: ast.Call
    ) -> Dict:
        """分析relationship定义"""
        rel_info = {
            "name": rel_name,
            "related_model": None,
            "back_populates": None,
            "cascade": None,
        }

        # 分析位置参数 - 通常第一个是相关模型
        if call_node.args:
            model_arg = call_node.args[0]
            if isinstance(model_arg, ast.Constant):
                rel_info["related_model"] = model_arg.value

        # 分析关键字参数
        for keyword in call_node.keywords:
            if keyword.arg == "back_populates":
                if isinstance(keyword.value, ast.Constant):
                    rel_info["back_populates"] = keyword.value.value
            elif keyword.arg == "cascade":
                if isinstance(keyword.value, ast.Constant):
                    rel_info["cascade"] = keyword.value.value

        return rel_info

    def _analyze_runtime(self, module_name: str) -> Dict[str, Any]:
        """运行时分析 - 导入模块获取完整类信息"""
        try:
            # 动态导入模块
            module_path = f"app.modules.{module_name}.models"
            spec = importlib.util.spec_from_file_location(
                module_path, self.project_root / f"app/modules/{module_name}/models.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            models = {}

            # 获取模块中的所有类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, "__tablename__") and hasattr(obj, "__table__"):
                    models[name] = self._extract_runtime_model_info(obj)

            return models

        except Exception as e:
            print(f"⚠️ 运行时分析失败: {e}")
            return {}

    def _extract_runtime_model_info(self, model_class) -> Dict:
        """从运行时模型类提取信息"""
        table = model_class.__table__

        model_info = {
            "name": model_class.__name__,
            "tablename": table.name,
            "fields": [],
            "relationships": [],
            "primary_keys": [col.name for col in table.primary_key.columns],
            "unique_constraints": [],
        }

        # 分析字段
        for column in table.columns:
            field_info = FieldInfo(
                name=column.name,
                column_type=str(column.type),
                python_type=(
                    column.type.python_type.__name__
                    if hasattr(column.type, "python_type")
                    else "str"
                ),
                nullable=column.nullable,
                primary_key=column.primary_key,
                foreign_key=(
                    str(list(column.foreign_keys)[0].target_fullname)
                    if column.foreign_keys
                    else None
                ),
                unique=column.unique,
                default=column.default.arg if column.default else None,
                constraints=[],
            )
            model_info["fields"].append(field_info)

        # 分析关系
        if hasattr(model_class, "__mapper__"):
            for rel_name, relationship in model_class.__mapper__.relationships.items():
                rel_info = RelationshipInfo(
                    name=rel_name,
                    related_model=relationship.mapper.class_.__name__,
                    relationship_type=self._determine_relationship_type(relationship),
                    back_populates=relationship.back_populates,
                    cascade=str(relationship.cascade) if relationship.cascade else None,
                    foreign_keys=[
                        str(fk.parent.name) for fk in relationship.foreign_keys
                    ],
                )
                model_info["relationships"].append(rel_info)

        return model_info

    def _determine_relationship_type(self, relationship) -> str:
        """确定关系类型"""
        if relationship.uselist:
            return "one-to-many" if not relationship.secondary else "many-to-many"
        else:
            return "one-to-one"

    def _merge_analysis_results(
        self, ast_models: Dict, runtime_models: Dict
    ) -> Dict[str, ModelInfo]:
        """合并AST和运行时分析结果"""
        merged = {}

        # 以运行时分析为准，AST分析补充
        for model_name, runtime_info in runtime_models.items():
            ast_info = ast_models.get(model_name, {})

            merged[model_name] = ModelInfo(
                name=model_name,
                tablename=runtime_info["tablename"],
                fields=runtime_info["fields"],
                relationships=runtime_info["relationships"],
                mixins=ast_info.get("mixins", []),
                docstring=ast_info.get("docstring"),
                primary_keys=runtime_info.get("primary_keys", []),
                unique_constraints=runtime_info.get("unique_constraints", []),
            )

        return merged

    def generate_analysis_report(self, models: Dict[str, ModelInfo]) -> str:
        """生成分析报告"""
        report = []
        report.append("# 模型分析报告\n")

        for model_name, model in models.items():
            report.append(f"## {model_name} 模型")
            report.append(f"- **表名**: {model.tablename}")
            report.append(f"- **字段数量**: {len(model.fields)}")
            report.append(f"- **关系数量**: {len(model.relationships)}")
            report.append(
                f"- **混入**: {', '.join(model.mixins) if model.mixins else '无'}"
            )
            report.append("")

            # 字段详情
            report.append("### 字段详情")
            for field in model.fields:
                constraints = []
                if field.primary_key:
                    constraints.append("主键")
                if not field.nullable:
                    constraints.append("非空")
                if field.unique:
                    constraints.append("唯一")
                if field.foreign_key:
                    constraints.append(f"外键:{field.foreign_key}")

                constraint_text = f" [{', '.join(constraints)}]" if constraints else ""
                report.append(
                    f"- **{field.name}**: {field.column_type}{constraint_text}"
                )

            # 关系详情
            if model.relationships:
                report.append("\n### 关系详情")
                for rel in model.relationships:
                    report.append(
                        f"- **{rel.name}**: {rel.relationship_type} -> {rel.related_model}"
                    )

            report.append("\n---\n")

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="SQLAlchemy模型智能分析器")
    parser.add_argument("module_name", help="要分析的模块名称")
    parser.add_argument("--detailed", action="store_true", help="生成详细报告")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    analyzer = SQLAlchemyModelAnalyzer()

    try:
        models = analyzer.analyze_module(args.module_name)

        if args.detailed:
            report = analyzer.generate_analysis_report(models)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(report)
                print(f"📄 详细报告已保存到: {args.output}")
            else:
                print("\n" + report)
        else:
            # 简单输出
            for model_name, model in models.items():
                print(
                    f"✅ {model_name}: {len(model.fields)}字段, {len(model.relationships)}关系"
                )

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
