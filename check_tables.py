#!/usr/bin/env python3
"""
数据库表结构检查工具

功能说明：
    验证数据库表结构与SQLAlchemy模型定义的一致性，特别关注软删除字段的存在性。
    主要用于调试集成测试中的数据库模式同步问题。

主要功能：
    ✅ 检查指定表是否存在
    ✅ 验证软删除字段(is_deleted, deleted_at)的存在性  
    ✅ 列出表的所有字段结构
    ✅ 提供可视化的检查结果输出

使用场景：
    - 集成测试前验证数据库表结构
    - 调试"Unknown column 'is_deleted'"类型错误
    - 确认数据库迁移或表重建是否生效
    - 验证SoftDeleteMixin继承模型的表结构

使用方法：
    1. 确保MySQL测试容器运行: docker-compose up -d mysql_test
    2. 直接运行: python check_tables.py
    3. 查看输出结果，确认软删除字段状态

输出格式：
    brands: ✅ 软删除字段
      字段: ['id', 'name', 'description', 'logo_url', 'website_url', 'is_active', 'sort_order', 'created_at', 'updated_at', 'is_deleted', 'deleted_at']

注意事项：
    - 需要MySQL测试容器运行在localhost:3308
    - 使用与tests/conftest.py相同的数据库连接配置
    - 检查结果仅针对当前数据库状态，不修改任何数据

作者：GitHub Copilot
版本：v1.0
创建时间：2025-10-10
依赖：sqlalchemy, pymysql
"""

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