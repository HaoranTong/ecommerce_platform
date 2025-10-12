"""
直接复制安全测试的逻辑，添加详细调试
"""
import pytest
import asyncio
import sys
sys.path.append('.')

@pytest.mark.asyncio
async def test_debug_malicious_input(async_api_client):
    """复制安全测试逻辑，添加调试信息"""
    
    # 获取admin token（复制安全测试的逻辑）
    admin_token, admin_user = await async_api_client.authenticate_as_admin()
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    print(f"Admin token: {admin_token[:50]}...")
    print(f"Admin user: {admin_user.email}")
    
    # 测试正常输入
    print("\n=== 测试正常输入 ===")
    normal_data = {
        "name": "正常分类名称",
        "description": "正常描述"
    }
    
    response = await async_api_client.post(
        "/api/v1/product-catalog/categories",
        json=normal_data,
        headers=headers
    )
    print(f"正常输入响应: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"创建成功: {result}")
    else:
        print(f"错误响应: {response.text}")
    
    # 测试超长输入（复制安全测试的确切逻辑）
    print("\n=== 测试超长输入 ===")
    long_name = "A" * 10000
    test_data = {
        "name": long_name,
        "description": long_name,
    }
    
    print(f"发送超长输入: name长度={len(test_data['name'])}, description长度={len(test_data['description'])}")
    
    response = await async_api_client.post(
        "/api/v1/product-catalog/categories",
        json=test_data,
        headers=headers
    )
    
    print(f"超长输入响应: {response.status_code}")
    print(f"响应内容: {response.text[:500]}...")
    
    if response.status_code == 422:
        print("✅ 验证正常工作")
        error_detail = response.json()
        print(f"验证错误详情: {error_detail}")
    elif response.status_code == 201:
        print("❌ 验证失败 - 接受了超长输入")
        result = response.json()
        print(f"意外创建的记录: {result}")
        print(f"实际存储的name长度: {len(result.get('name', ''))}")
    else:
        print(f"其他状态码: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_debug_malicious_input())