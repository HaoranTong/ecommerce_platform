"""
调试FastAPI验证问题的pytest测试
"""

import pytest
import asyncio

class TestValidationDebug:
    """调试验证问题"""
    
    @pytest.fixture(autouse=True)
    async def setup(self, async_api_client):
        """设置测试"""
        # 获取admin token
        self.admin_token, self.admin_user_id, self.admin_user = await async_api_client.authenticate_as_admin()
        yield
    
    async def test_debug_validation_issue(self, async_api_client):
        """调试验证问题"""
        print("\n🔍 调试FastAPI验证问题")
        
        # 准备超长输入数据
        test_data = {
            "name": "x" * 10000,  # 超过max_length=100
            "description": "test description"
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # 测试分类创建端点
        response = await async_api_client.post(
            "/api/v1/product-catalog/categories",
            json=test_data,
            headers=headers
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ 正确：FastAPI拒绝了超长输入")
            validation_details = response.json()
            print(f"   验证错误: {validation_details}")
        elif response.status_code == 201:
            print("❌ 问题确认：FastAPI接受了超长输入！")
            response_data = response.json()
            print(f"   创建的对象: {response_data}")
            
            # 检查实际保存的数据
            if 'name' in response_data:
                actual_length = len(response_data['name'])
                print(f"   实际name长度: {actual_length}")
                if actual_length > 100:
                    print("   ⚠️  数据库保存了超长数据！")
        else:
            print(f"⚠️  其他状态码: {response.status_code}")
            print(f"   响应: {response.text}")
        
        # 不要让测试失败，我们只是在调试
        print("🔍 调试完成")