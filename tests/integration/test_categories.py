import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.modules.product_catalog.models import Category

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


# create tables before TestClient instantiation 
Base.metadata.create_all(bind=engine)

app.dependency_overrides[get_db] = override_get_session
client = TestClient(app)


def test_create_category():
    """测试创建分类"""
    response = client.post('/api/categories', json={
        'name': '测试分类',
        'sort_order': 1
    })
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == '测试分类'
    assert data['sort_order'] == 1
    assert data['parent_id'] is None
    assert data['is_active'] is True


def test_create_subcategory():
    """测试创建子分类"""
    # 先创建父分类
    parent_response = client.post('/api/categories', json={
        'name': '父分类',
        'sort_order': 1
    })
    parent_id = parent_response.json()['id']
    
    # 创建子分类
    response = client.post('/api/categories', json={
        'name': '子分类',
        'parent_id': parent_id,
        'sort_order': 1
    })
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == '子分类'
    assert data['parent_id'] == parent_id


def test_list_categories():
    """测试分类列表"""
    response = client.get('/api/categories')
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) > 0


def test_get_category_tree():
    """测试分类树结构"""
    response = client.get('/api/categories/tree')
    assert response.status_code == 200
    tree = response.json()
    assert isinstance(tree, list)


def test_update_category():
    """测试更新分类"""
    # 创建分类
    create_response = client.post('/api/categories', json={
        'name': '待更新分类',
        'sort_order': 1
    })
    category_id = create_response.json()['id']
    
    # 更新分类
    response = client.put(f'/api/categories/{category_id}', json={
        'name': '已更新分类',
        'sort_order': 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == '已更新分类'
    assert data['sort_order'] == 2


def test_delete_category():
    """测试删除分类"""
    # 创建分类
    create_response = client.post('/api/categories', json={
        'name': '待删除分类',
        'sort_order': 1
    })
    category_id = create_response.json()['id']
    
    # 删除分类
    response = client.delete(f'/api/categories/{category_id}')
    assert response.status_code == 204
    
    # 验证已删除
    get_response = client.get(f'/api/categories/{category_id}')
    assert get_response.status_code == 404


def test_create_duplicate_category_name():
    """测试创建重复分类名称"""
    # 创建第一个分类
    client.post('/api/categories', json={
        'name': '重复分类名',
        'sort_order': 1
    })
    
    # 尝试创建同名分类
    response = client.post('/api/categories', json={
        'name': '重复分类名',
        'sort_order': 2
    })
    assert response.status_code == 400
    assert '已存在' in response.json()['detail']


def test_create_category_with_invalid_parent():
    """测试使用无效父分类创建分类"""
    response = client.post('/api/categories', json={
        'name': '无效父分类测试',
        'parent_id': 99999
    })
    assert response.status_code == 400
    assert '不存在' in response.json()['detail']
