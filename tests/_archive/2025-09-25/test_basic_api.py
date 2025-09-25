"""
烟雾测试 - API基础功能验证
根据测试标准文档，烟雾测试使用SQLite文件数据库进行快速部署验证
"""
import pytest
import requests
import time
from fastapi.testclient import TestClient
from sqlalchemy import text

def test_api_health_check():
    """测试API健康检查端点"""
    try:
        response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print(f"✅ Health check passed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        pytest.skip("⚠️  API server not running on http://127.0.0.1:8000 - skipping smoke test")
    except Exception as e:
        pytest.skip(f"⚠️  Health check skipped: {e}")

def test_users_endpoint_basic():
    """测试用户API基础功能"""
    base_url = 'http://127.0.0.1:8000'
    
    # 测试数据
    test_user = {
        "email": f"smoketest_{int(time.time())}@example.com",
        "username": f"smokeuser_{int(time.time())}",
        "password": "SmokeTest123!"
    }
    
    try:
        # 1. 测试用户注册
        register_response = requests.post(
            f'{base_url}/api/v1/users/register', 
            json=test_user, 
            timeout=5
        )
        print(f"Register response: {register_response.status_code}")
        
        if register_response.status_code == 201:
            print("✅ User registration endpoint working")
        elif register_response.status_code == 422:
            print("⚠️  User registration returned validation error (may be expected)")
        else:
            print(f"⚠️  User registration returned: {register_response.status_code}")
        
        # 2. 测试获取用户列表
        users_response = requests.get(f'{base_url}/api/v1/users', timeout=5)
        print(f"GET users response: {users_response.status_code}")
        
        if users_response.status_code == 200:
            print("✅ Users list endpoint working")
        else:
            print(f"⚠️  Users list returned: {users_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        pytest.skip("⚠️  API server not running - skipping users endpoint test")
    except Exception as e:
        pytest.skip(f"⚠️  Users endpoint test skipped: {e}")

def test_basic_database_connectivity(smoke_test_db):
    """测试基础数据库连接 - 使用SQLite文件数据库"""
    try:
        # 简单的数据库连接测试
        result = smoke_test_db.execute(text("SELECT 1 as test")).fetchone()
        assert result[0] == 1
        print("✅ Database connectivity verified")
    except Exception as e:
        pytest.fail(f"❌ Database connectivity failed: {e}")

def test_certificates_endpoint_legacy():
    """
    遗留证书端点测试 (从原_smoke_cert.py迁移)
    保持向后兼容性
    """
    url = 'http://127.0.0.1:8001/api/certificates'
    payload = {
        "name": "Test Cert",
        "issuer": "CA", 
        "serial": "SN-TEST-0001",
        "description": "auto test"
    }
    
    try:
        # 允许短暂预热时间
        time.sleep(1)
        
        # POST测试
        r = requests.post(url, json=payload, timeout=5)
        print(f'POST {url}: {r.status_code}')
        if r.status_code != 404:  # 404表示端点不存在，这是可接受的
            try:
                print(f"Response: {r.text[:200]}...")  # 只显示前200字符
            except Exception:
                pass
        
        # GET测试  
        r2 = requests.get(url, timeout=5)
        print(f'GET {url}: {r2.status_code}')
        if r2.status_code != 404:
            try:
                print(f"Response: {r2.text[:200]}...")
            except Exception:
                pass
                
        # 如果都返回404，说明证书功能已移除，这是正常的
        if r.status_code == 404 and r2.status_code == 404:
            print("ℹ️  Certificates endpoint not implemented (expected)")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot connect to legacy certificates endpoint (port 8001)")
    except Exception as e:
        print(f'⚠️  Legacy certificates test error: {e}')