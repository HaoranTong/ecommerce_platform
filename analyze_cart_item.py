"""使用model_analyzer获取CartItem模型的完整字段信息"""
from pathlib import Path
from tools.test_generators.utils.model_analyzer import ModelAnalyzer

analyzer = ModelAnalyzer(Path.cwd())
models = analyzer.analyze_module_models('shopping_cart')
cart_item = models.get('CartItem')

print("=== CartItem模型完整信息 ===")
print(f"表名: {cart_item.tablename}")
print(f"\n字段列表 ({len(cart_item.fields)}个):")
for field in cart_item.fields:
    fk_info = f" -> {field.foreign_key}" if field.foreign_key else ""
    print(f"  {field.name}: {field.column_type} (nullable={field.nullable}, pk={field.primary_key}){fk_info}")

print(f"\n关系列表 ({len(cart_item.relationships)}个):")
for rel in cart_item.relationships:
    print(f"  {rel.name} -> {rel.related_model} ({rel.relationship_type})")
