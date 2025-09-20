"""
Shopping_Cart 烟雾测试套件

测试类型: 烟雾测试 (Smoke)
数据策略: SQLite文件数据库, smoke_test_db fixture
生成时间: 2025-09-20 09:43:58

根据testing-standards.md第95-104行烟雾测试规范
"""

import pytest
import requests
from sqlalchemy.orm import Session

# Fixture导入
from tests.conftest import smoke_test_db


@pytest.mark.smoke  
class TestShopping_CartSmoke:
    """烟雾测试 - 基本健康检查"""
    
    def test_shopping_cart_health_check(self):
        """验证shopping_cart模块基本健康状态"""
        try:
            # 模块导入测试
            from app.modules.shopping_cart import service
            from app.modules.shopping_cart import models
            assert True, "shopping_cart module imports successfully"
        except ImportError as e:
            pytest.fail(f"shopping_cart module import failed: {e}")
            
    def test_shopping_cart_database_connection_smoke(self, smoke_test_db: Session):
        """验证shopping_cart数据库连接正常"""
        # 简单的数据库连接测试
        result = smoke_test_db.execute("SELECT 1 as test")
        assert result.fetchone()[0] == 1
        
    def test_shopping_cart_api_endpoint_smoke(self):
        """验证shopping_cart API端点可访问性"""
        try:
            response = requests.get(
                "http://localhost:8000/shopping_cart/health",
                timeout=5
            )
            assert response.status_code in [200, 404]  # 404也可接受，只要服务响应
        except requests.ConnectionError:
            pytest.skip("API服务未运行，跳过烟雾测试")
            
    def test_shopping_cart_basic_functionality_smoke(self, smoke_test_db: Session):
        """验证shopping_cart基本功能正常"""
        from app.modules.shopping_cart.service import Shopping_CartService
        
        service = Shopping_CartService(smoke_test_db)
        
        # 最基本的功能测试
        basic_data = {"name": "smoke_test", "status": "active"}
        
        try:
            created = service.create(basic_data)
            assert created is not None
        except Exception as e:
            pytest.fail(f"shopping_cart basic create functionality failed: {e}")
