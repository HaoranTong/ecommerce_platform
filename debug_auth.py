#!/usr/bin/env python3
"""调试认证依赖覆盖"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.core.auth import get_current_user, get_current_active_user, get_current_admin_user
from app.modules.user_auth.models import User

# 创建模拟用户
mock_user = User(
    id=1,
    username="admin",
    email="admin@test.com",
    role="admin",
    is_active=True
)

def override_get_db():
    pass  # 不需要数据库

async def override_get_current_user():
    print("override_get_current_user called")
    return mock_user

async def override_get_current_active_user():
    print("override_get_current_active_user called")
    return mock_user

async def override_get_current_admin_user():
    print("override_get_current_admin_user called")
    return mock_user

# 清除现有覆盖
app.dependency_overrides.clear()

# 设置覆盖
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_current_active_user] = override_get_current_active_user
app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user

print("Dependency overrides set:")
for k, v in app.dependency_overrides.items():
    print(f"  {k.__name__} -> {v.__name__}")

# 测试API调用
with TestClient(app) as client:
    print("\nTesting category creation...")
    response = client.post("/api/v1/product-catalog/categories", json={
        "name": "测试分类",
        "sort_order": 1
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

app.dependency_overrides.clear()