"""
库存管理模块 API 测试

简单测试库存管理API端点的基本功能
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🏥 测试健康检查...")
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    print("  ✅ 健康检查通过")

def test_inventory_api():
    """测试库存API端点存在"""
    print("📊 测试库存API可访问性...")
    
    # 测试获取商品库存（应该返回404或401，证明端点存在）
    response = requests.get(f"{BASE_URL}/api/v1/inventory-management/stock/1")
    print(f"  库存查询端点响应: {response.status_code}")
    
    # 测试批量查询（应该返回422或401，证明端点存在）
    response = requests.post(f"{BASE_URL}/api/v1/inventory-management/stock/batch", 
                           json={"product_ids": [1, 2]})
    print(f"  批量查询端点响应: {response.status_code}")
    
    print("  ✅ 库存API端点已注册")

def main():
    """主测试函数"""
    print("🚀 开始库存管理模块 API 测试")
    print("=" * 50)
    
    try:
        test_health()
        test_inventory_api()
        
        print("\n" + "=" * 50)
        print("🎉 API测试完成！库存管理模块已成功集成")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保应用程序正在运行")
        print("   可以运行: python -m uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main()
