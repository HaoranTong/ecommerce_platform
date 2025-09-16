import pytest


def test_create_product(unit_test_client):
    """测试创建商品"""
    response = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '测试商品',
        'description': '这是一个测试商品',
        'status': 'published',
        'sort_order': 1
    })
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == '测试商品'
    assert data['description'] == '这是一个测试商品'
    assert data['status'] == 'published'
    assert data['sort_order'] == 1


def test_create_product_with_category(unit_test_client):
    """测试创建带分类的商品"""
    # 先创建分类
    category_response = unit_test_client.post('/api/v1/product-catalog/categories', json={
        'name': '商品分类',
        'parent_id': None,
        'sort_order': 1
    })
    # 检查分类创建是否成功
    assert category_response.status_code == 201, f"分类创建失败: {category_response.text}"
    category_data = category_response.json()
    category_id = category_data['id']
    
    # 创建商品（只包含基础信息）
    response = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '分类商品',
        'description': '带分类的商品',
        'category_id': category_id,
        'status': 'published'
    })
    assert response.status_code == 201
    data = response.json()
    assert data['category_id'] == category_id
    
    # Note: SKU creation endpoints are not yet implemented
    # This test focuses on the Product-Category relationship which now works correctly


def test_list_products(unit_test_client):
    """测试商品列表"""
    # 先创建几个测试商品
    unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '列表测试商品1',
        'description': '测试商品描述1',
        'status': 'published'
    })
    unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '列表测试商品2', 
        'description': '测试商品描述2',
        'status': 'published'
    })
    
    # 测试商品列表
    response = unit_test_client.get('/api/v1/product-catalog/products')
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 2
    assert any(product['name'] == '列表测试商品1' for product in products)
    assert any(product['name'] == '列表测试商品2' for product in products)


def test_get_product(unit_test_client):
    """测试获取单个商品"""
    # 先创建商品
    product_response = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '单品测试',
        'description': '单品测试商品',
        'brand': '测试品牌',
        'category': '测试分类'
    })
    product_id = product_response.json()['id']
    
    # 创建SKU
    sku_response = unit_test_client.post(f'/api/v1/product-catalog/products/{product_id}/skus', json={
        'sku_code': 'SINGLE-001',
        'price': '50.00',
        'stock_quantity': 10,
        'attributes': {'color': 'red', 'size': 'M'}
    })
    
    # 获取商品
    response = unit_test_client.get(f'/api/v1/product-catalog/products/{product_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == '单品测试'


def test_update_product(unit_test_client):
    """测试更新商品"""
    # 先创建商品（只包含基础信息）
    product_response = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '待更新商品',
        'description': '待更新的测试商品',
        'status': 'draft'
    })
    assert product_response.status_code == 201
    product_id = product_response.json()['id']
    
    # 创建SKU（包含价格信息）
    sku_response = unit_test_client.post(f'/api/v1/product-catalog/products/{product_id}/skus', json={
        'sku_code': 'UPDATE-001',
        'price': 100.00,
        'weight': 1.0,
        'is_active': True
    })
    assert sku_response.status_code == 201
    sku_id = sku_response.json()['id']
    
    # 更新商品基本信息
    response = unit_test_client.put(f'/api/v1/product-catalog/products/{product_id}', json={
        'name': '已更新商品',
        'description': '已更新的测试商品',
        'status': 'published'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == '已更新商品'
    assert data['status'] == 'published'
    
    # 更新SKU价格
    sku_update_response = unit_test_client.put(f'/api/v1/product-catalog/skus/{sku_id}', json={
        'price': 150.00,
        'weight': 1.5
    })
    assert sku_update_response.status_code == 200
    sku_data = sku_update_response.json()
    assert float(sku_data['price']) == 150.00
    assert float(sku_data['weight']) == 1.5


def test_update_product_stock(unit_test_client):
    """测试SKU状态管理（简化版 - 库存管理属于inventory模块）"""
    # 先创建商品
    product_response = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '库存测试商品',
        'description': '库存测试商品',
        'status': 'published'
    })
    assert product_response.status_code == 201
    product_id = product_response.json()['id']
    
    # 创建SKU
    sku_response = unit_test_client.post(f'/api/v1/product-catalog/products/{product_id}/skus', json={
        'sku_code': 'STOCK-001',
        'price': 75.00,
        'weight': 2.0,
        'is_active': True
    })
    assert sku_response.status_code == 201
    sku_id = sku_response.json()['id']
    
    # 测试SKU状态更新
    response = unit_test_client.put(f'/api/v1/product-catalog/skus/{sku_id}', json={
        'is_active': False
    })
    assert response.status_code == 200
    data = response.json()
    assert data['is_active'] == False
    
    # 重新激活SKU
    response = unit_test_client.put(f'/api/v1/product-catalog/skus/{sku_id}', json={
        'is_active': True,
        'price': 80.00
    })
    assert response.status_code == 200
    data = response.json()
    assert data['is_active'] == True
    assert float(data['price']) == 80.00


def test_delete_product(unit_test_client):
    """测试删除商品"""
    # 创建商品
    product_response = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '待删除商品',
        'description': '待删除的测试商品',
        'status': 'published'
    })
    assert product_response.status_code == 201
    product_id = product_response.json()['id']
    
    # 创建SKU
    sku_response = unit_test_client.post(f'/api/v1/product-catalog/products/{product_id}/skus', json={
        'sku_code': 'DELETE-001',
        'price': 25.00,
        'weight': 0.5,
        'is_active': True
    })
    assert sku_response.status_code == 201
    
    # 删除商品（软删除）
    response = unit_test_client.delete(f'/api/v1/product-catalog/products/{product_id}')
    assert response.status_code == 204
    
    # 验证已被软删除（应该返回404）
    get_response = unit_test_client.get(f'/api/v1/product-catalog/products/{product_id}')
    assert get_response.status_code == 404


def test_create_duplicate_sku(unit_test_client):
    """测试创建重复SKU"""
    # 创建第一个商品
    product_response1 = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '原始商品',
        'description': '原始商品描述',
        'status': 'published'
    })
    assert product_response1.status_code == 201
    product_id1 = product_response1.json()['id']
    
    # 创建第一个SKU
    sku_response1 = unit_test_client.post(f'/api/v1/product-catalog/products/{product_id1}/skus', json={
        'sku_code': 'DUP-001',
        'price': 50.00,
        'weight': 1.0,
        'is_active': True
    })
    assert sku_response1.status_code == 201
    
    # 创建第二个商品
    product_response2 = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '重复商品',
        'description': '重复商品描述',
        'status': 'published'
    })
    assert product_response2.status_code == 201
    product_id2 = product_response2.json()['id']
    
    # 尝试创建相同SKU码的SKU（应该失败）
    response = unit_test_client.post(f'/api/v1/product-catalog/products/{product_id2}/skus', json={
        'sku_code': 'DUP-001',
        'price': 60.00,
        'weight': 1.2,
        'is_active': True
    })
    assert response.status_code == 400
    assert '已存在' in response.json()['detail']


def test_search_products(unit_test_client):
    """测试商品搜索"""
    # 创建测试商品A
    product_response_a = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '搜索测试商品A',
        'description': '搜索测试商品A描述',
        'status': 'published'
    })
    assert product_response_a.status_code == 201
    product_id_a = product_response_a.json()['id']
    
    sku_response_a = unit_test_client.post(f'/api/v1/product-catalog/products/{product_id_a}/skus', json={
        'sku_code': 'SEARCH-A',
        'price': 30.00,
        'weight': 1.0,
        'is_active': True
    })
    assert sku_response_a.status_code == 201
    
    # 创建测试商品B
    product_response_b = unit_test_client.post('/api/v1/product-catalog/products', json={
        'name': '搜索测试商品B',
        'description': '搜索测试商品B描述',
        'status': 'published'
    })
    assert product_response_b.status_code == 201
    product_id_b = product_response_b.json()['id']
    
    sku_response_b = unit_test_client.post(f'/api/v1/product-catalog/products/{product_id_b}/skus', json={
        'sku_code': 'SEARCH-B',
        'price': 40.00,
        'weight': 1.5,
        'is_active': True
    })
    assert sku_response_b.status_code == 201
    
    # 按名称搜索产品
    response = unit_test_client.get('/api/v1/product-catalog/products?search=搜索测试')
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 2
    product_names = [p['name'] for p in products]
    assert '搜索测试商品A' in product_names
    assert '搜索测试商品B' in product_names
    
    # 按SKU编码搜索
    response = unit_test_client.get('/api/v1/product-catalog/skus?search=SEARCH-A')
    assert response.status_code == 200
    skus = response.json()
    assert len(skus) >= 1
    assert any(s['sku_code'] == 'SEARCH-A' for s in skus)
