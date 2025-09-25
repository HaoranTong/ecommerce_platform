import pytest
from app.modules.product_catalog.models import Category
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator


def test_create_category(integration_test_client):
    """测试创建分类"""
    response = integration_test_client.post('/api/v1/product-catalog/categories', json={
        'name': '测试分类',
        'sort_order': 1
    })
    if response.status_code != 201:
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == '测试分类'
    assert data['sort_order'] == 1
    assert data['parent_id'] is None
    assert data['is_active'] is True


def test_create_subcategory(integration_test_client):
    """测试创建子分类"""
    # 先创建父分类
    parent_response = integration_test_client.post('/api/v1/product-catalog/categories', json={
        'name': '父分类',
        'sort_order': 1
    })
    parent_id = parent_response.json()['id']
    
    # 创建子分类
    response = integration_test_client.post('/api/v1/product-catalog/categories', json={
        'name': '子分类',
        'parent_id': parent_id,
        'sort_order': 1
    })
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == '子分类'
    assert data['parent_id'] == parent_id


def test_list_categories(integration_test_client):
    """测试分类列表"""
    response = integration_test_client.get('/api/v1/product-catalog/categories')
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) > 0


def test_get_category_tree(integration_test_client):
    """测试分类树结构"""
    response = integration_test_client.get('/api/v1/product-catalog/categories/tree')
    assert response.status_code == 200
    tree = response.json()
    assert isinstance(tree, list)


def test_update_category(integration_test_client):
    """测试更新分类"""
    # 创建分类
    create_response = integration_test_client.post('/api/v1/product-catalog/categories', json={
        'name': '待更新分类',
        'sort_order': 1
    })
    category_id = create_response.json()['id']
    
    # 更新分类
    response = integration_test_client.put(f'/api/v1/product-catalog/categories/{category_id}', json={
        'name': '已更新分类',
        'sort_order': 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == '已更新分类'
    assert data['sort_order'] == 2


def test_delete_category(integration_test_client):
    """测试删除分类"""
    # 创建分类
    create_response = integration_test_client.post('/api/v1/product-catalog/categories', json={
        'name': '待删除分类',
        'sort_order': 1
    })
    category_id = create_response.json()['id']
    
    # 删除分类
    response = integration_test_client.delete(f'/api/v1/product-catalog/categories/{category_id}')
    assert response.status_code == 204
    
    # 验证已删除
    get_response = integration_test_client.get(f'/api/v1/product-catalog/categories/{category_id}')
    assert get_response.status_code == 404


def test_create_duplicate_category_name(integration_test_client):
    """测试创建重复分类名称"""
    # 创建第一个分类
    integration_test_client.post('/api/v1/product-catalog/categories', json={
        'name': '重复分类名',
        'sort_order': 1
    })
    
    # 尝试创建同名分类
    response = integration_test_client.post('/api/v1/product-catalog/categories', json={
        'name': '重复分类名',
        'sort_order': 2
    })
    assert response.status_code == 400
    assert '已存在' in response.json()['detail']


def test_create_category_with_invalid_parent(integration_test_client):
    """测试使用无效父分类创建分类"""
    response = integration_test_client.post('/api/v1/product-catalog/categories', json={
        'name': '无效父分类测试',
        'parent_id': 99999
    })
    assert response.status_code == 400
    assert '不存在' in response.json()['detail']
