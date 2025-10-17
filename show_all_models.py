"""使用model_analyzer获取所有模型信息"""
from pathlib import Path
from tools.test_generators.utils.model_analyzer import ModelAnalyzer

analyzer = ModelAnalyzer(Path.cwd())
all_models = analyzer.analyze_all_modules()

print("=== 所有模块的模型 ===")
for module_name, models in all_models.items():
    print(f"\n【{module_name}】")
    for model_name, model_info in models.items():
        print(f"  {model_name} ({model_info.tablename})")

print("\n\n=== CartItem详细信息 ===")
cart_item = all_models['shopping_cart']['CartItem']
print(f"表名: {cart_item.tablename}")
print(f"\n字段:")
for field in cart_item.fields:
    fk = f" FK->{field.foreign_key}" if field.foreign_key else ""
    print(f"  {field.name}: {field.column_type} (nullable={field.nullable}){fk}")

print("\n\n=== Product详细信息 ===")
product = all_models['product_catalog']['Product']
print(f"表名: {product.tablename}")
print(f"主键: {product.primary_keys}")

print("\n\n=== SKU详细信息 ===")
sku = all_models['product_catalog']['SKU']
print(f"表名: {sku.tablename}")
print(f"\n字段:")
for field in sku.fields:
    fk = f" FK->{field.foreign_key}" if field.foreign_key else ""
    print(f"  {field.name}: {field.column_type} (nullable={field.nullable}){fk}")
