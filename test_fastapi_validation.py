#!/usr/bin/env python3
"""
直接测试FastAPI验证机制
"""
import requests
import json

def test_fastapi_validation():
    base_url = "http://localhost:8000"
    
    # 首先获取admin token
    login_data = {
        "username": "admin@example.com",
        "password": "Admin123!@#"
    }
    
    try:
        # 登录获取token
        login_response = requests.post(
            f"{base_url}/api/v1/user-auth/login",
            json=login_data,  # 使用JSON格式
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.status_code} - {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print("✅ 登录成功，获取到token")
        
        # 测试超长输入
        test_data = {
            "name": "x" * 10000,  # 超长输入
            "description": "test description"
        }
        
        print(f"发送创建分类请求，name长度: {len(test_data['name'])}")
        
        response = requests.post(
            f"{base_url}/api/v1/product-catalog/categories",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ FastAPI验证正常工作 - 拒绝了超长输入")
            print(f"验证错误: {response.json()}")
        elif response.status_code == 201:
            print("❌ FastAPI验证失败 - 接受了超长输入!")
            result = response.json()
            print(f"创建的分类: id={result.get('id')}, name长度={len(result.get('name', ''))}")
        else:
            print(f"其他状态码: {response.status_code}")
            print(f"响应: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        print("可能服务器没有运行，请先启动服务器: python -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    test_fastapi_validation()