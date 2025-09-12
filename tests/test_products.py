import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
import app.data_models as models
from app.db import get_session, Base

# use in-memory sqlite for fast tests
SQLITE_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def setup_module(module):
    # create tables
    Base.metadata.create_all(bind=engine)


def override_get_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# create tables before TestClient instantiation (avoid race with TestClient server)
Base.metadata.create_all(bind=engine)

app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


def test_create_product():
    """测试创建商品"""
    response = client.post('/api/products', json={
        'name': '测试商品',
        'sku': 'TEST-001',
        'description': '这是一个测试商品',
        'price': '99.99',
        'stock_quantity': 100,
        'status': 'active'
    })
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == '测试商品'
    assert data['sku'] == 'TEST-001'
    assert float(data['price']) == 99.99
    assert data['stock_quantity'] == 100


def test_create_product_with_category():
    """测试创建带分类的商品"""
    # 先创建分类
    category_response = client.post('/api/categories', json={
        'name': '商品分类',
        'sort_order': 1
    })
    category_id = category_response.json()['id']
    
    # 创建商品
    response = client.post('/api/products', json={
        'name': '分类商品',
        'sku': 'CAT-001',
        'description': '带分类的商品',
        'category_id': category_id,
        'price': '199.99',
        'stock_quantity': 50
    })
    assert response.status_code == 201
    data = response.json()
    assert data['category_id'] == category_id


def test_list_products():
    """测试商品列表"""
    response = client.get('/api/products')
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0


def test_get_product():
    """测试获取单个商品"""
    # 先创建商品
    create_response = client.post('/api/products', json={
        'name': '单品测试',
        'sku': 'SINGLE-001',
        'price': '50.00',
        'stock_quantity': 10
    })
    product_id = create_response.json()['id']
    
    # 获取商品
    response = client.get(f'/api/products/{product_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == '单品测试'


def test_update_product():
    """测试更新商品"""
    # 先创建商品
    create_response = client.post('/api/products', json={
        'name': '待更新商品',
        'sku': 'UPDATE-001',
        'price': '100.00',
        'stock_quantity': 20
    })
    product_id = create_response.json()['id']
    
    # 更新商品
    response = client.put(f'/api/products/{product_id}', json={
        'name': '已更新商品',
        'price': '150.00',
        'stock_quantity': 30
    })
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == '已更新商品'
    assert float(data['price']) == 150.00
    assert data['stock_quantity'] == 30


def test_update_product_stock():
    """测试更新商品库存"""
    # 先创建商品
    create_response = client.post('/api/products', json={
        'name': '库存测试商品',
        'sku': 'STOCK-001',
        'price': '75.00',
        'stock_quantity': 100
    })
    product_id = create_response.json()['id']
    
    # 增加库存
    response = client.patch(f'/api/products/{product_id}/stock', json={
        'quantity_change': 50,
        'reason': '补货'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['stock_quantity'] == 150
    
    # 减少库存
    response = client.patch(f'/api/products/{product_id}/stock', json={
        'quantity_change': -30,
        'reason': '销售'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['stock_quantity'] == 120


def test_delete_product():
    """测试删除商品"""
    # 创建商品
    create_response = client.post('/api/products', json={
        'name': '待删除商品',
        'sku': 'DELETE-001',
        'price': '25.00',
        'stock_quantity': 5
    })
    product_id = create_response.json()['id']
    
    # 删除商品
    response = client.delete(f'/api/products/{product_id}')
    assert response.status_code == 204
    
    # 验证已删除
    get_response = client.get(f'/api/products/{product_id}')
    assert get_response.status_code == 404


def test_create_duplicate_sku():
    """测试创建重复SKU"""
    # 创建第一个商品
    client.post('/api/products', json={
        'name': '原始商品',
        'sku': 'DUP-001',
        'price': '50.00',
        'stock_quantity': 10
    })
    
    # 尝试创建相同SKU的商品
    response = client.post('/api/products', json={
        'name': '重复商品',
        'sku': 'DUP-001',
        'price': '60.00',
        'stock_quantity': 15
    })
    assert response.status_code == 400
    assert '已存在' in response.json()['detail']


def test_search_products():
    """测试商品搜索"""
    # 创建测试商品
    client.post('/api/products', json={
        'name': '搜索测试商品A',
        'sku': 'SEARCH-A',
        'price': '30.00',
        'stock_quantity': 5
    })
    
    client.post('/api/products', json={
        'name': '搜索测试商品B',
        'sku': 'SEARCH-B',
        'price': '40.00',
        'stock_quantity': 8
    })
    
    # 按名称搜索
    response = client.get('/api/products?search=搜索测试')
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 2
    
    # 按SKU搜索
    response = client.get('/api/products?search=SEARCH-A')
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 1
    assert any(p['sku'] == 'SEARCH-A' for p in products)
