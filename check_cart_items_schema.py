"""检查cart_items表的实际数据库结构"""
from sqlalchemy import create_engine, inspect

engine = create_engine('mysql+pymysql://root:Abc123456!!@localhost:3306/ecommerce_platform_test')
inspector = inspect(engine)

print("=== cart_items表字段 ===")
columns = inspector.get_columns('cart_items')
for col in columns:
    print(f"  {col['name']}: {col['type']} (nullable={col['nullable']})")

print("\n=== 外键约束 ===")
fks = inspector.get_foreign_keys('cart_items')
for fk in fks:
    print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
print("\n=== 索引 ===")
indexes = inspector.get_indexes('cart_items')
for idx in indexes:
    print(f"  {idx['name']}: {idx['column_names']} (unique={idx['unique']})")
