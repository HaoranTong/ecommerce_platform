"""
集成测试：用户管理API测试
使用conftest.py中的标准MySQL集成测试配置
"""
import pytest
from app.modules.user_auth.models import User


@pytest.mark.integration
def test_create_and_list_user(integration_test_client):
    """测试用户创建和列表API - 使用标准集成测试环境"""
    # 创建用户
    response = integration_test_client.post('/api/v1/user-auth/users', json={
        'username': 'testu', 
        'email': 'testu@example.com'
    })
    assert response.status_code == 201
    data = response.json()
    assert data['username'] == 'testu'
    
    # 获取用户列表
    response2 = integration_test_client.get('/api/v1/user-auth/users')
    assert response2.status_code == 200
    users = response2.json()
    assert any(u['username'] == 'testu' for u in users)
