"""理解sku_id字段的真实含义"""
from pathlib import Path
from tools.test_generators.utils.model_analyzer import ModelAnalyzer

analyzer = ModelAnalyzer(Path.cwd())
all_models = analyzer.analyze_all_modules()

print("=== 关键发现 ===\n")

# CartItem模型
cart_item = all_models['shopping_cart']['CartItem']
print("【CartItem模型】")
print(f"表名: {cart_item.tablename}")
for field in cart_item.fields:
    if 'sku' in field.name.lower():
        print(f"  字段: {field.name}")
        print(f"  类型: {field.column_type}")
        print(f"  外键: {field.foreign_key}")
        print(f"  ➡️ 结论: CartItem.sku_id 引用 {field.foreign_key}")

print("\n【Product模型】")
product = all_models['product_catalog']['Product']
print(f"表名: {product.tablename}")
print(f"主键字段: {[f.name for f in product.fields if f.primary_key]}")

print("\n【SKU模型】")
sku = all_models['product_catalog']['SKU']
print(f"表名: {sku.tablename}")
print(f"主键字段: {[f.name for f in sku.fields if f.primary_key]}")
for field in sku.fields:
    if field.foreign_key:
        print(f"  {field.name} -> {field.foreign_key}")

print("\n=== 命名混淆分析 ===")
print("问题：CartItem有字段叫'sku_id'，但它引用的是products.id")
print("可能的原因：")
print("  1. 字段命名错误（应该叫product_id）")
print("  2. 外键定义错误（应该引用product_skus.id）")
print("  3. 这是简化设计（购物车直接关联Product，不关联SKU）")
print("\n需要查看：实际业务代码中如何使用这个字段")
