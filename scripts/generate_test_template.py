#!/usr/bin/env python3
"""
测试代码生成工具 - 基于实际模型自动生成标准测试代码

解决问题：
- 避免Pydantic V2兼容性错误
- 避免字段类型不匹配问题  
- 避免属性名称错误问题
- 提供标准化的Mock对象模板

使用方法：
python scripts/generate_test_template.py --model inventory_management --schema SKUInventoryRead
"""

import ast
import sys
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional
import importlib.util


class ModelAnalyzer:
    """模型分析器 - 分析实际的数据模型结构"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
    def analyze_model(self, module_name: str, model_name: str) -> Dict[str, Any]:
        """分析模型字段和类型"""
        try:
            # 动态导入模型
            model_path = self.project_root / "app" / "modules" / module_name / "models.py"
            spec = importlib.util.spec_from_file_location("models", model_path)
            models_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(models_module)
            
            # 获取模型类
            model_class = getattr(models_module, model_name)
            
            # 分析字段
            fields = {}
            if hasattr(model_class, '__table__'):
                # SQLAlchemy 模型
                for column in model_class.__table__.columns:
                    fields[column.name] = {
                        'type': str(column.type),
                        'nullable': column.nullable,
                        'primary_key': column.primary_key,
                        'foreign_key': bool(column.foreign_keys)
                    }
            
            return {
                'model_name': model_name,
                'fields': fields,
                'module_name': module_name
            }
            
        except Exception as e:
            print(f"❌ 模型分析失败: {e}")
            return {}
    
    def analyze_schema(self, module_name: str, schema_name: str) -> Dict[str, Any]:
        """分析Pydantic Schema结构"""
        try:
            # 动态导入schema
            schema_path = self.project_root / "app" / "modules" / module_name / "schemas.py"
            spec = importlib.util.spec_from_file_location("schemas", schema_path)
            schemas_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(schemas_module)
            
            # 获取schema类
            schema_class = getattr(schemas_module, schema_name)
            
            # 分析字段（Pydantic V2）
            fields = {}
            if hasattr(schema_class, 'model_fields'):
                for field_name, field_info in schema_class.model_fields.items():
                    fields[field_name] = {
                        'type': str(field_info.annotation),
                        'required': field_info.is_required(),
                        'default': getattr(field_info, 'default', None)
                    }
            
            return {
                'schema_name': schema_name,
                'fields': fields,
                'module_name': module_name
            }
            
        except Exception as e:
            print(f"❌ Schema分析失败: {e}")
            return {}


class TestTemplateGenerator:
    """测试模板生成器 - 生成符合实际模型的测试代码"""
    
    def __init__(self, analyzer: ModelAnalyzer):
        self.analyzer = analyzer
        
    def generate_mock_object_template(self, model_info: Dict[str, Any]) -> str:
        """生成Mock对象模板"""
        if not model_info:
            return "# ❌ 模型信息获取失败"
            
        fields = model_info.get('fields', {})
        model_name = model_info.get('model_name', 'UnknownModel')
        
        lines = [
            f"# ✅ 基于实际{model_name}模型生成的Mock对象模板",
            f"def create_mock_{model_name.lower()}():",
            f"    \"\"\"创建符合{model_name}模型的Mock对象\"\"\"",
            f"    mock_obj = Mock()"
        ]
        
        # 生成字段赋值
        for field_name, field_info in fields.items():
            field_type = field_info['type']
            sample_value = self._generate_sample_value(field_name, field_type)
            lines.append(f"    mock_obj.{field_name} = {sample_value}  # {field_type}")
            
        lines.extend([
            "    return mock_obj",
            ""
        ])
        
        return "\n".join(lines)
    
    def generate_pydantic_test_template(self, schema_info: Dict[str, Any]) -> str:
        """生成Pydantic测试模板"""
        if not schema_info:
            return "# ❌ Schema信息获取失败"
            
        fields = schema_info.get('fields', {})
        schema_name = schema_info.get('schema_name', 'UnknownSchema')
        
        lines = [
            f"# ✅ 基于实际{schema_name} Schema生成的测试模板",
            f"def test_{schema_name.lower()}_validation():",
            f"    \"\"\"测试{schema_name}的Pydantic V2验证\"\"\"",
            "    # 准备测试数据",
            "    test_data = {"
        ]
        
        # 生成测试数据
        for field_name, field_info in fields.items():
            field_type = field_info['type']
            sample_value = self._generate_sample_value(field_name, field_type)
            lines.append(f"        '{field_name}': {sample_value},  # {field_type}")
            
        lines.extend([
            "    }",
            "",
            f"    # Pydantic V2验证",
            f"    result = {schema_name}.model_validate(test_data)",
            "",
            "    # 断言验证",
        ])
        
        # 生成断言
        for field_name in fields.keys():
            lines.append(f"    assert result.{field_name} == test_data['{field_name}']")
            
        return "\n".join(lines)
    
    def _generate_sample_value(self, field_name: str, field_type: str) -> str:
        """根据字段类型生成示例值"""
        field_type_lower = field_type.lower()
        
        # ID类型字段
        if 'id' in field_name.lower():
            return "1"
            
        # 时间类型
        if 'datetime' in field_type_lower or 'timestamp' in field_name.lower():
            return "datetime.now(timezone.utc)"
            
        # 数值类型  
        if 'integer' in field_type_lower or 'int' in field_type_lower:
            if 'quantity' in field_name.lower():
                return "100"
            elif 'threshold' in field_name.lower():
                return "10"
            else:
                return "1"
                
        # 布尔类型
        if 'boolean' in field_type_lower or 'bool' in field_type_lower:
            if 'is_active' in field_name.lower():
                return "True"
            elif 'is_deleted' in field_name.lower():
                return "False"
            else:
                return "False"
                
        # 字符串类型
        if 'varchar' in field_type_lower or 'string' in field_type_lower or 'str' in field_type_lower:
            if 'email' in field_name.lower():
                return '"test@example.com"'
            elif 'name' in field_name.lower():
                return '"测试名称"'
            elif 'code' in field_name.lower():
                return '"TEST001"'
            else:
                return '"test_value"'
                
        # 小数类型
        if 'decimal' in field_type_lower or 'numeric' in field_type_lower:
            return "Decimal('99.99')"
            
        # 默认值
        return "None"


def main():
    """主函数"""
    if len(sys.argv) < 4:
        print("使用方法: python generate_test_template.py <module_name> <model_name> <schema_name>")
        print("示例: python generate_test_template.py inventory_management InventoryStock SKUInventoryRead")
        return
        
    module_name = sys.argv[1]
    model_name = sys.argv[2]  
    schema_name = sys.argv[3]
    
    # 初始化分析器
    project_root = Path(__file__).parent.parent
    analyzer = ModelAnalyzer(str(project_root))
    generator = TestTemplateGenerator(analyzer)
    
    print(f"🔍 分析模块: {module_name}")
    print(f"🔍 分析模型: {model_name}")
    print(f"🔍 分析Schema: {schema_name}")
    print("=" * 60)
    
    # 分析模型
    model_info = analyzer.analyze_model(module_name, model_name)
    if model_info:
        print("📋 模型分析结果:")
        for field, info in model_info['fields'].items():
            print(f"  {field}: {info['type']}")
        print()
        
        # 生成Mock模板
        mock_template = generator.generate_mock_object_template(model_info)
        print("🛠️  Mock对象模板:")
        print(mock_template)
        print()
    
    # 分析Schema
    schema_info = analyzer.analyze_schema(module_name, schema_name)
    if schema_info:
        print("📋 Schema分析结果:")
        for field, info in schema_info['fields'].items():
            print(f"  {field}: {info['type']} (required: {info['required']})")
        print()
        
        # 生成测试模板
        test_template = generator.generate_pydantic_test_template(schema_info)
        print("🧪 Pydantic测试模板:")
        print(test_template)


if __name__ == "__main__":
    main()