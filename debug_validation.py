#!/usr/bin/env python3
"""
调试FastAPI/Pydantic验证问题

根据commit 4e6cd59的发现，测试超长输入时返回201而不是422
这表明FastAPI没有正确执行Pydantic Schema的max_length验证
"""

import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.modules.product_catalog.schemas import CategoryCreate
from pydantic import ValidationError

def test_pydantic_validation_directly():
    """直接测试Pydantic Schema验证"""
    print("🔍 测试1: 直接Pydantic Schema验证")
    
    try:
        # 测试超长name（10000字符，超过max_length=100）
        long_name = "x" * 10000
        schema = CategoryCreate(
            name=long_name,
            description="test description"
        )
        print("❌ 错误：Pydantic允许了超长输入！")
        return False
    except ValidationError as e:
        print("✅ 正确：Pydantic拒绝了超长输入")
        print(f"   验证错误: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False

def test_fastapi_endpoint_validation():
    """测试FastAPI端点验证"""
    print("\n🔍 测试2: FastAPI端点验证")
    
    client = TestClient(app)
    
    # 准备测试数据
    test_data = {
        "name": "x" * 10000,  # 超长输入
        "description": "test description"
    }
    
    try:
        # 测试创建分类端点（不带认证，应该返回401或422）
        response = client.post(
            "/api/v1/product-catalog/categories",
            json=test_data
        )
        
        print(f"   响应状态码: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ 正确：FastAPI拒绝了超长输入（验证错误）")
            return True
        elif response.status_code in [401, 403]:
            print("⚠️  认证错误：需要token才能测试验证")
            return None
        elif response.status_code == 201:
            print("❌ 错误：FastAPI接受了超长输入！")
            print(f"   响应内容: {response.text[:200]}...")
            return False
        else:
            print(f"⚠️  其他状态码: {response.status_code}")
            print(f"   响应内容: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始调试FastAPI/Pydantic验证问题\n")
    
    # 测试1：直接Pydantic验证
    pydantic_works = test_pydantic_validation_directly()
    
    # 测试2：FastAPI端点验证
    fastapi_works = test_fastapi_endpoint_validation()
    
    # 总结
    print("\n📊 总结:")
    print(f"   Pydantic Schema验证: {'✅ 正常' if pydantic_works else '❌ 异常'}")
    if fastapi_works is not None:
        print(f"   FastAPI端点验证: {'✅ 正常' if fastapi_works else '❌ 异常'}")
    else:
        print(f"   FastAPI端点验证: ⚠️  需要认证token")
    
    if pydantic_works and not fastapi_works:
        print("\n🔍 问题分析:")
        print("   Pydantic Schema验证正常，但FastAPI端点接受了超长输入")
        print("   可能原因：")
        print("   1. FastAPI路由没有正确使用Schema验证")
        print("   2. 中间件或依赖注入绕过了验证")
        print("   3. 数据库约束与Schema不一致")

if __name__ == "__main__":
    main()