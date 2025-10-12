#!/usr/bin/env python3
"""
使用认证token调试FastAPI验证问题
"""

import asyncio
import pytest
from tests.conftest import get_async_api_client

async def debug_with_auth():
    """使用认证token测试FastAPI验证"""
    print("🔍 使用认证token测试FastAPI验证\n")
    
    # 获取异步API客户端
    client = get_async_api_client()
    
    try:
        # 获取admin token
        print("📝 获取admin认证token...")
        admin_token, admin_user_id, admin_user = await client.authenticate_as_admin()
        print(f"✅ 获取token成功: {admin_token[:20]}...")
        
        # 准备测试数据
        test_data = {
            "name": "x" * 10000,  # 超长输入，超过max_length=100
            "description": "test description"
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 测试分类创建端点
        print("📝 测试分类创建端点...")
        response = await client.post(
            "/api/v1/product-catalog/categories",
            json=test_data,
            headers=headers
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ 正确：FastAPI拒绝了超长输入（验证错误）")
            print("   Pydantic验证正常工作")
        elif response.status_code == 201:
            print("❌ 问题确认：FastAPI接受了超长输入！")
            print("   这是一个真实的安全漏洞")
            print(f"   响应内容: {response.text[:300]}...")
            
            # 尝试解析响应内容
            try:
                response_data = response.json()
                if 'name' in response_data:
                    actual_name_length = len(response_data['name'])
                    print(f"   实际保存的name长度: {actual_name_length}")
                    if actual_name_length > 100:
                        print("   ⚠️  数据库保存了超过100字符的name！")
            except:
                pass
        else:
            print(f"⚠️  其他状态码: {response.status_code}")
            print(f"   响应内容: {response.text[:300]}...")
        
        return response.status_code
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await client.close()

if __name__ == "__main__":
    result = asyncio.run(debug_with_auth())