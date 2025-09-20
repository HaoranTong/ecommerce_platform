"""
User_Auth 集成测试套件

测试类型: 集成测试 (Integration)
数据策略: MySQL Docker, mysql_integration_db fixture  
生成时间: 2025-09-20 21:34:33

根据testing-standards.md第105-125行集成测试规范
"""

import pytest
import requests
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import User_AuthFactory, UserFactory

# Fixture导入
from tests.conftest import mysql_integration_db, api_client

# 被测模块导入  
from app.modules.user_auth.service import User_AuthService


@pytest.mark.integration
class TestUser_AuthIntegration:
    """集成测试 - 真实环境模拟"""
    
    def setup_method(self):
        """集成测试准备"""
        self.api_base_url = "http://localhost:8000"
        self.test_data = User_AuthFactory.build_dict()
        
    def test_user_auth_api_integration(self, api_client, mysql_integration_db: Session):
        """测试user_auth API完整集成"""
        # 创建API请求
        create_response = api_client.post(
            f"/user_auth/",
            json=self.test_data
        )
        
        # 验证创建响应
        assert create_response.status_code == 201
        created_data = create_response.json()
        assert "id" in created_data
        user_auth_id = created_data["id"]
        
        # 查询API验证
        get_response = api_client.get(f"/user_auth/{poll_id}")
        assert get_response.status_code == 200
        
        # 更新API验证
        update_data = {"status": "updated"}
        update_response = api_client.put(
            f"/user_auth/{poll_id}",
            json=update_data
        )
        assert update_response.status_code == 200
        
        # 删除API验证
        delete_response = api_client.delete(f"/user_auth/{poll_id}")
        assert delete_response.status_code == 204
        
    def test_user_auth_database_integration(self, mysql_integration_db: Session):
        """测试user_auth数据库集成"""
        service = User_AuthService(mysql_integration_db)
        
        # 测试数据库事务完整性
        created = service.create(self.test_data)
        assert created is not None
        
        # 验证数据库持久化
        mysql_integration_db.commit()
        found = service.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        
    def test_user_auth_external_service_integration(self, mysql_integration_db: Session):
        """测试user_auth外部服务集成"""
        service = User_AuthService(mysql_integration_db)
        
        # 模拟外部服务调用
        with pytest.raises((ConnectionError, TimeoutError), match="external"):
            # 这里应该是真实的外部服务调用测试
            pass
            
    @pytest.mark.slow
    def test_user_auth_performance_integration(self, mysql_integration_db: Session):
        """测试user_auth性能集成"""
        service = User_AuthService(mysql_integration_db)
        
        import time
        start_time = time.time()
        
        # 批量操作性能测试
        for i in range(100):
            test_data = User_AuthFactory.build_dict()
            service.create(test_data)
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 验证性能要求 (100个操作 < 5秒)
        assert execution_time < 5.0, f"Performance test failed: {execution_time:.2f}s > 5s"
