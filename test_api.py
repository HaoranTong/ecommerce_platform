#!/usr/bin/env python3
"""
简单的API测试脚本
用于验证商品和分类管理功能
"""

import requests
import json
import sys

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api"

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_categories():
    """测试分类管理"""
    print("\n🏷️ 测试分类管理...")
    
    # 创建顶级分类
    category_data = {
        "name": "农产品",
        "sort_order": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/categories", json=category_data)
        if response.status_code == 201:
            category = response.json()
            print(f"✅ 创建分类成功: {category['name']} (ID: {category['id']})")
            
            # 创建子分类
            sub_category_data = {
                "name": "五常大米",
                "parent_id": category['id'],
                "sort_order": 1
            }
            
            sub_response = requests.post(f"{BASE_URL}/categories", json=sub_category_data)
            if sub_response.status_code == 201:
                sub_category = sub_response.json()
                print(f"✅ 创建子分类成功: {sub_category['name']} (ID: {sub_category['id']})")
                return category['id'], sub_category['id']
            else:
                print(f"❌ 创建子分类失败: {sub_response.status_code}")
                return category['id'], None
        else:
            print(f"❌ 创建分类失败: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ 分类测试失败: {e}")
        return None, None

def test_products(category_id):
    """测试商品管理"""
    print("\n📦 测试商品管理...")
    
    if not category_id:
        print("⚠️ 跳过商品测试（分类创建失败）")
        return None
    
    # 创建商品
    product_data = {
        "name": "五常稻花香大米",
        "sku": "WC-DFX-001",
        "description": "优质五常稻花香大米，香味浓郁",
        "category_id": category_id,
        "price": 58.80,
        "stock_quantity": 100,
        "status": "active"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/products", json=product_data)
        if response.status_code == 201:
            product = response.json()
            print(f"✅ 创建商品成功: {product['name']} (ID: {product['id']})")
            
            # 测试库存更新
            stock_update = {
                "quantity_change": -10,
                "reason": "测试减库存"
            }
            
            stock_response = requests.patch(
                f"{BASE_URL}/products/{product['id']}/stock", 
                json=stock_update
            )
            
            if stock_response.status_code == 200:
                updated_product = stock_response.json()
                print(f"✅ 库存更新成功: 剩余库存 {updated_product['stock_quantity']}")
            else:
                print(f"❌ 库存更新失败: {stock_response.status_code}")
            
            return product['id']
        else:
            print(f"❌ 创建商品失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 商品测试失败: {e}")
        return None

def test_product_list():
    """测试商品列表"""
    print("\n📋 测试商品列表...")
    
    try:
        response = requests.get(f"{BASE_URL}/products")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ 获取商品列表成功: 共 {len(products)} 个商品")
            for product in products:
                print(f"  - {product['name']} (SKU: {product['sku']}, 库存: {product['stock_quantity']})")
            return True
        else:
            print(f"❌ 获取商品列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 商品列表测试失败: {e}")
        return False

def main():
    """主测试流程"""
    print("🚀 开始API功能测试...")
    
    # 健康检查
    if not test_health():
        print("💥 服务未启动或不可用，请先启动服务")
        sys.exit(1)
    
    # 分类测试
    category_id, sub_category_id = test_categories()
    
    # 商品测试
    product_id = test_products(sub_category_id or category_id)
    
    # 商品列表测试
    test_product_list()
    
    print("\n🎉 测试完成！")
    
    if category_id and product_id:
        print("\n📊 测试总结:")
        print(f"  - 创建了分类ID: {category_id}")
        if sub_category_id:
            print(f"  - 创建了子分类ID: {sub_category_id}")
        print(f"  - 创建了商品ID: {product_id}")
        print("\n💡 提示: 可以访问 http://127.0.0.1:8000/docs 查看完整API文档")

if __name__ == "__main__":
    main()
