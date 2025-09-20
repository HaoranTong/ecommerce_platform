"""
Shopping_Cart 性能测试套件

测试类型: 专项测试 (Performance)
生成时间: 2025-09-20 09:43:58

根据testing-standards.md第165-185行性能测试规范
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import Shopping_CartFactory

# Fixture导入
from tests.conftest import mysql_integration_db

# 被测模块导入
from app.modules.shopping_cart.service import Shopping_CartService


@pytest.mark.performance
@pytest.mark.slow
class TestShopping_CartPerformance:
    """性能测试"""
    
    def test_shopping_cart_create_performance(self, mysql_integration_db: Session):
        """测试shopping_cart创建操作性能"""
        service = Shopping_CartService(mysql_integration_db)
        
        # 性能基准: 1000次创建操作 < 10秒
        start_time = time.time()
        
        for i in range(1000):
            test_data = Shopping_CartFactory.build_dict()
            test_data['name'] = f"perf_test_{i}"
            service.create(test_data)
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time < 10.0, f"Create performance failed: {execution_time:.2f}s > 10s"
        
    def test_shopping_cart_query_performance(self, mysql_integration_db: Session):
        """测试shopping_cart查询操作性能"""
        service = Shopping_CartService(mysql_integration_db)
        
        # 准备测试数据
        for i in range(100):
            test_data = Shopping_CartFactory.build_dict()
            test_data['name'] = f"query_test_{i}"
            service.create(test_data)
            
        # 性能测试: 1000次查询 < 5秒
        start_time = time.time()
        
        for i in range(1000):
            results = service.get_all(limit=10)
            assert len(results) > 0
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time < 5.0, f"Query performance failed: {execution_time:.2f}s > 5s"
        
    def test_shopping_cart_concurrent_access(self, mysql_integration_db: Session):
        """测试shopping_cart并发访问性能"""
        service = Shopping_CartService(mysql_integration_db)
        
        def create_item(thread_id):
            test_data = Shopping_CartFactory.build_dict()
            test_data['name'] = f"concurrent_test_{thread_id}"
            return service.create(test_data)
            
        # 并发测试: 10个线程同时创建100个项目
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_item, i) for i in range(100)]
            results = [f.result() for f in futures]
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 验证所有操作成功
        assert all(r is not None for r in results)
        
        # 并发性能要求: 100个并发操作 < 15秒
        assert execution_time < 15.0, f"Concurrent performance failed: {execution_time:.2f}s > 15s"
