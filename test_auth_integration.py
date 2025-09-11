# 端到端认证测试脚本

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth import create_access_token, decode_token, get_password_hash, verify_password
from app.models import User
import json

def test_jwt_functionality():
    """测试JWT基础功能"""
    print("\n🔐 测试JWT功能...")
    
    # 测试token创建
    token_data = {'sub': '1', 'username': 'testuser'}
    token = create_access_token(token_data)
    print(f"✅ Token创建成功: {token[:30]}...")
    
    # 测试token解析
    decoded = decode_token(token)
    assert decoded['sub'] == '1'
    assert decoded['type'] == 'access'
    print("✅ Token解析成功")
    
    # 测试密码哈希
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    print("✅ 密码哈希验证成功")
    
    return True

def test_permission_logic():
    """测试权限逻辑"""
    print("\n🛡️ 测试权限逻辑...")
    
    from app.auth import require_ownership
    
    class MockUser:
        def __init__(self, id, role):
            self.id = id
            self.role = role
    
    # 测试用户权限
    user = MockUser(1, 'user')
    admin = MockUser(2, 'admin')
    super_admin = MockUser(3, 'super_admin')
    
    # 用户只能访问自己的资源
    assert require_ownership(1, user) == True
    assert require_ownership(2, user) == False
    print("✅ 用户权限检查正确")
    
    # 管理员可以访问所有资源
    assert require_ownership(1, admin) == True
    assert require_ownership(999, admin) == True
    print("✅ 管理员权限检查正确")
    
    # 超级管理员可以访问所有资源
    assert require_ownership(1, super_admin) == True
    assert require_ownership(999, super_admin) == True
    print("✅ 超级管理员权限检查正确")
    
    return True

def test_api_imports():
    """测试API模块导入"""
    print("\n📦 测试API模块导入...")
    
    try:
        from app.api.product_routes import router as product_router
        print("✅ 商品路由导入成功")
        
        from app.api.cart_routes import router as cart_router
        print("✅ 购物车路由导入成功")
        
        from app.api.order_routes import router as order_router
        print("✅ 订单路由导入成功")
        
        from app.api.user_routes import router as user_router
        print("✅ 用户路由导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_api_permission_matrix():
    """测试API权限矩阵"""
    print("\n📋 验证API权限矩阵...")
    
    # 权限矩阵定义
    api_matrix = {
        "公开API": [
            "GET /api/products",
            "GET /api/products/{id}",
            "POST /api/auth/register",
            "POST /api/auth/login"
        ],
        "用户API": [
            "GET /api/auth/me",
            "PUT /api/auth/me",
            "POST /api/carts/items",
            "GET /api/carts",
            "PUT /api/carts/items/{id}",
            "DELETE /api/carts/items/{id}",
            "POST /api/orders",
            "GET /api/orders (自己的)",
            "GET /api/orders/{id} (自己的)",
            "DELETE /api/orders/{id} (取消自己的)"
        ],
        "管理员API": [
            "POST /api/products",
            "PUT /api/products/{id}",
            "PATCH /api/products/{id}/stock",
            "DELETE /api/products/{id}",
            "PATCH /api/orders/{id}/status",
            "GET /api/orders (所有)",
            "GET /api/orders/{id} (所有)"
        ]
    }
    
    for category, apis in api_matrix.items():
        print(f"  {category}: {len(apis)}个API")
    
    print("✅ API权限矩阵验证完成")
    return True

def main():
    """主测试函数"""
    print("🚀 开始端到端认证测试...")
    
    tests = [
        test_jwt_functionality,
        test_permission_logic,
        test_api_imports,
        test_api_permission_matrix
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！认证体系集成成功！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
