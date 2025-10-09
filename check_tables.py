#!/usr/bin/env python3
"""检查数据库表结构"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import inspect, create_engine

def main():
    # 使用测试环境的正确数据库URL - 与conftest.py一致
    database_url = "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"
    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    tables = ['users', 'brands', 'categories', 'products', 'product_skus']
    
    for table in tables:
        if inspector.has_table(table):
            columns = [col['name'] for col in inspector.get_columns(table)]
            has_soft = 'is_deleted' in columns and 'deleted_at' in columns
            status = "✅" if has_soft else "❌"
            print(f'{table}: {status} 软删除字段')
            print(f'  字段: {columns}')
            print()
        else:
            print(f'{table}: 表不存在')

if __name__ == '__main__':
    main()