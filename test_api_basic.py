#!/usr/bin/env python3
"""简单的API测试验证"""

import sys
import os
from pathlib import Path

# 添加项目根目录到sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 设置测试数据库环境变量
os.environ["DATABASE_URL"] = "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"

from fastapi.testclient import TestClient
from app.main import app

def test_api_basic():
    """测试基本API连通性"""
    with TestClient(app) as client:
        # 测试注册API
        register_data = {
            "username": "simple_test_user",
            "email": "simple@test.com",
            "password": "TestPassword123!",
            "phone": "13800138888",
            "real_name": "简单测试用户"
        }
        
        response = client.post("/api/v1/user-auth/register", json=register_data)
        print(f"Register Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Register Response: {response.text}")
            
        # 测试登录API
        login_data = {
            "username": "simple_test_user",
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/user-auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            tokens = response.json()
            print(f"Login Success: Got tokens {list(tokens.keys())}")
            return True
        else:
            print(f"Login Response: {response.text}")
            return False

if __name__ == "__main__":
    try:
        result = test_api_basic()
        print(f"✅ API基础测试: {'通过' if result else '失败'}")
    except Exception as e:
        print(f"❌ API基础测试失败: {e}")