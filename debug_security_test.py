"""
调试安全测试 - 查看到底发生了什么
"""
import asyncio
import sys
sys.path.append('.')

async def debug_security_test():
    import pytest_asyncio
    from tests.conftest import async_api_client, mysql_integration_db
    from sqlalchemy.orm import Session
    from app.core.database import get_db
    from app.modules.product_catalog.schemas import CategoryCreate
    from pydantic import ValidationError
    
    # 首先测试Schema验证
    print("=== 1. 测试Schema验证 ===")
    try:
        long_name = "x" * 10000
        schema = CategoryCreate(
            name=long_name,
            description="test"
        )
        print(f"❌ Schema验证失败 - 允许了超长输入: {len(long_name)}字符")
    except ValidationError as e:
        print(f"✅ Schema验证正常 - 拒绝了超长输入: {str(e)[:100]}...")
    
    # 测试实际API
    print("\n=== 2. 测试实际API ===")
    
    # 设置测试数据库
    import pytest
    from tests.conftest import TestEnvironment
    
    # 创建异步客户端
    async with TestEnvironment() as env:
        client = env.async_client
        
        # 获取admin token
        admin_token, admin_user_id, admin_user = await client.authenticate_as_admin()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 测试超长输入
        test_data = {
            "name": "x" * 10000,
            "description": "test"
        }
        
        print(f"发送请求: name长度={len(test_data['name'])}, description长度={len(test_data['description'])}")
        
        response = await client.post(
            "/api/v1/product-catalog/categories",
            json=test_data,
            headers=headers
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:300]}...")
        
        if response.status_code == 422:
            print("✅ API验证正常 - 拒绝了超长输入")
        elif response.status_code == 201:
            print("❌ API验证失败 - 接受了超长输入")
            # 检查创建的记录
            response_data = response.json()
            print(f"创建的记录: id={response_data.get('id')}, name长度={len(response_data.get('name', ''))}")
        else:
            print(f"❓ 意外状态码: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(debug_security_test())