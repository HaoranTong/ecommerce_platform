"""
商品管理模块集成测试
测试完整的API端点和数据库操作
"""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
from app.main import app
from app.shared.base_models import Base
from app.core.database import get_db
from app.modules.user_auth.models import User

# 创建测试数据库引擎
def create_test_engine():
    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    test_db.close()
    engine = create_engine(f"sqlite:///{test_db.name}")
    return engine, test_db.name

@pytest.fixture(scope="session") 
def test_engine():
    engine, db_path = create_test_engine()
    yield engine
    os.unlink(db_path)

@pytest.fixture(scope="session")
def test_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="session")
def override_get_db(test_session):
    def _override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
async def client(override_get_db):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture(scope="session")
async def admin_token(client):
    """创建管理员用户并获取token"""
    # 创建管理员用户
    admin_data = {
        "username": "testadmin",
        "email": "admin@test.com", 
        "password": "adminpass123",
        "verification_code": "123456"
    }
    
    register_response = await client.post("/api/v1/user-auth/register", json=admin_data)
    assert register_response.status_code == 201
    
    # 登录获取token
    login_data = {
        "username": "testadmin",
        "password": "adminpass123"
    }
    
    login_response = await client.post("/api/v1/user-auth/login", data=login_data)
    assert login_response.status_code == 200
    
    token_data = login_response.json()
    return token_data["access_token"]

class TestProductCatalogIntegration:
    """商品管理模块集成测试"""
    
    @pytest.mark.asyncio
    async def test_category_crud_operations(self, client, admin_token):
        """测试分类的完整CRUD操作"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 创建分类
        category_data = {
            "name": "电子产品",
            "description": "电子设备和数码产品",
            "image_url": "https://example.com/electronics.jpg",
            "sort_order": 1
        }
        
        create_response = await client.post("/api/v1/product-catalog/categories", 
                                         json=category_data, headers=headers)
        assert create_response.status_code == 201
        category = create_response.json()
        assert category["name"] == "电子产品"
        category_id = category["id"]
        
        # 查询分类
        get_response = await client.get(f"/api/v1/product-catalog/categories/{category_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "电子产品"
        
        # 更新分类
        update_data = {
            "name": "电子设备",
            "description": "更新后的描述"
        }
        update_response = await client.put(f"/api/v1/product-catalog/categories/{category_id}",
                                         json=update_data, headers=headers)
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "电子设备"
        
        # 列表查询
        list_response = await client.get("/api/v1/product-catalog/categories")
        assert list_response.status_code == 200
        categories = list_response.json()
        assert len(categories) >= 1
        
        # 删除分类
        delete_response = await client.delete(f"/api/v1/product-catalog/categories/{category_id}",
                                            headers=headers)
        assert delete_response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_brand_crud_operations(self, client, admin_token):
        """测试品牌的完整CRUD操作"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 创建品牌
        brand_data = {
            "name": "Apple",
            "description": "苹果公司",
            "logo_url": "https://example.com/apple-logo.jpg",
            "website_url": "https://www.apple.com"
        }
        
        create_response = await client.post("/api/v1/product-catalog/brands",
                                          json=brand_data, headers=headers)
        assert create_response.status_code == 201
        brand = create_response.json()
        assert brand["name"] == "Apple"
        brand_id = brand["id"]
        
        # 查询品牌
        get_response = await client.get(f"/api/v1/product-catalog/brands/{brand_id}")
        assert get_response.status_code == 200
        
        # 删除品牌
        delete_response = await client.delete(f"/api/v1/product-catalog/brands/{brand_id}",
                                            headers=headers)
        assert delete_response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_product_crud_operations(self, client, admin_token):
        """测试商品的完整CRUD操作"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 先创建分类和品牌
        category_data = {
            "name": "手机",
            "description": "智能手机分类"
        }
        category_response = await client.post("/api/v1/product-catalog/categories",
                                            json=category_data, headers=headers)
        assert category_response.status_code == 201
        category_id = category_response.json()["id"]
        
        brand_data = {
            "name": "Samsung",
            "description": "三星电子"
        }
        brand_response = await client.post("/api/v1/product-catalog/brands",
                                         json=brand_data, headers=headers)
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]
        
        # 创建商品
        product_data = {
            "name": "Galaxy S23",
            "description": "三星Galaxy S23智能手机",
            "category_id": category_id,
            "brand_id": brand_id,
            "base_price": 5999.00,
            "status": "active"
        }
        
        create_response = await client.post("/api/v1/product-catalog/products",
                                          json=product_data, headers=headers)
        assert create_response.status_code == 201
        product = create_response.json()
        assert product["name"] == "Galaxy S23"
        product_id = product["id"]
        
        # 查询商品
        get_response = await client.get(f"/api/v1/product-catalog/products/{product_id}")
        assert get_response.status_code == 200
        
        # 搜索商品
        search_response = await client.get("/api/v1/product-catalog/products/search?q=Galaxy")
        assert search_response.status_code == 200
        results = search_response.json()
        assert len(results) >= 1
        
        # 清理数据
        await client.delete(f"/api/v1/product-catalog/products/{product_id}", headers=headers)
        await client.delete(f"/api/v1/product-catalog/categories/{category_id}", headers=headers)
        await client.delete(f"/api/v1/product-catalog/brands/{brand_id}", headers=headers)
    
    @pytest.mark.asyncio
    async def test_sku_operations(self, client, admin_token):
        """测试SKU操作"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 创建必要的前置数据
        category_response = await client.post("/api/v1/product-catalog/categories",
                                            json={"name": "测试分类"}, headers=headers)
        category_id = category_response.json()["id"]
        
        brand_response = await client.post("/api/v1/product-catalog/brands",
                                         json={"name": "测试品牌"}, headers=headers)
        brand_id = brand_response.json()["id"]
        
        product_response = await client.post("/api/v1/product-catalog/products", json={
            "name": "测试商品",
            "category_id": category_id,
            "brand_id": brand_id,
            "base_price": 100.00
        }, headers=headers)
        product_id = product_response.json()["id"]
        
        # 创建SKU
        sku_data = {
            "product_id": product_id,
            "sku_code": "TEST-001",
            "name": "测试SKU",
            "price": 99.00,
            "stock_quantity": 100
        }
        
        sku_response = await client.post("/api/v1/product-catalog/skus",
                                       json=sku_data, headers=headers)
        assert sku_response.status_code == 201
        sku = sku_response.json()
        assert sku["sku_code"] == "TEST-001"
        sku_id = sku["id"]
        
        # 查询SKU
        get_sku_response = await client.get(f"/api/v1/product-catalog/skus/{sku_id}")
        assert get_sku_response.status_code == 200
        
        # 清理数据
        await client.delete(f"/api/v1/product-catalog/skus/{sku_id}", headers=headers)
        await client.delete(f"/api/v1/product-catalog/products/{product_id}", headers=headers)
        await client.delete(f"/api/v1/product-catalog/categories/{category_id}", headers=headers)
        await client.delete(f"/api/v1/product-catalog/brands/{brand_id}", headers=headers)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])