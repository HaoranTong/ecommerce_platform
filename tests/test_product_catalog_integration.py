"""
产品目录模块集成测试

根据docs/standards/testing-standards.md规范实现
测试覆盖：
- 完整的商品管理工作流
- 跨模块的数据关系和业务逻辑
- 真实数据库环境下的功能验证
- API接口的端到端测试

使用SQLite文件数据库，模拟真实环境
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from decimal import Decimal

from app.core.database import Base, get_db
from app.main import app
from app.modules.product_catalog.models import (
    Product, Category, Brand, SKU, ProductAttribute, ProductImage, ProductTag
)

# 集成测试数据库配置
INTEGRATION_TEST_DB_PATH = "./tests/integration_test.db"
INTEGRATION_TEST_DATABASE_URL = f"sqlite:///{INTEGRATION_TEST_DB_PATH}"


@pytest.fixture(scope="module")
def integration_test_engine():
    """集成测试数据库引擎（文件）"""
    # 清理可能存在的旧数据库文件
    if os.path.exists(INTEGRATION_TEST_DB_PATH):
        os.remove(INTEGRATION_TEST_DB_PATH)
    
    engine = create_engine(
        INTEGRATION_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    
    # 清理测试数据库文件
    engine.dispose()
    if os.path.exists(INTEGRATION_TEST_DB_PATH):
        os.remove(INTEGRATION_TEST_DB_PATH)


@pytest.fixture(scope="function")
def integration_test_db(integration_test_engine):
    """集成测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False, 
        bind=integration_test_engine
    )
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.rollback()  # 回滚事务，保持数据清洁
        database.close()


@pytest.fixture(scope="function")
def integration_test_client(integration_test_db):
    """集成测试客户端"""
    def override_get_db():
        try:
            yield integration_test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ============ 完整工作流集成测试 ============

class TestProductManagementWorkflow:
    """商品管理完整工作流测试"""

    def test_complete_product_lifecycle(self, integration_test_client, integration_test_db):
        """测试商品完整生命周期"""
        
        # 步骤1：创建品牌
        brand_data = {
            "name": "小米",
            "slug": "xiaomi",
            "description": "小米科技有限公司",
            "logo_url": "https://cdn.mi.com/logo.png",
            "is_active": True
        }
        brand_response = integration_test_client.post("/api/v1/product-catalog/brands", json=brand_data)
        assert brand_response.status_code == 201
        brand = brand_response.json()
        brand_id = brand["id"]
        
        # 步骤2：创建分类层次结构
        parent_category_data = {
            "name": "电子产品",
            "sort_order": 1,
            "is_active": True
        }
        parent_response = integration_test_client.post("/api/v1/product-catalog/categories", json=parent_category_data)
        assert parent_response.status_code == 201
        parent_category = parent_response.json()
        
        child_category_data = {
            "name": "智能手机",
            "parent_id": parent_category["id"],
            "sort_order": 1,
            "is_active": True
        }
        child_response = integration_test_client.post("/api/v1/product-catalog/categories", json=child_category_data)
        assert child_response.status_code == 201
        child_category = child_response.json()
        category_id = child_category["id"]
        
        # 步骤3：创建商品
        product_data = {
            "name": "小米13 Pro",
            "description": "小米13 Pro 高端旗舰手机，配备骁龙8 Gen 2处理器",
            "brand_id": brand_id,
            "category_id": category_id,
            "status": "draft",
            "seo_title": "小米13 Pro - 高性能旗舰手机",
            "seo_description": "小米13 Pro搭载最新骁龙处理器，专业摄影系统",
            "seo_keywords": "小米,13 Pro,旗舰手机,骁龙8",
            "sort_order": 1
        }
        product_response = integration_test_client.post("/api/v1/product-catalog/products", json=product_data)
        assert product_response.status_code == 201
        product = product_response.json()
        product_id = product["id"]
        
        # 步骤4：添加SKU规格
        sku_data = {
            "product_id": product_id,
            "sku_code": "MI13PRO-256GB-WHITE",
            "name": "小米13 Pro 256GB 陶瓷白",
            "price": 4999.00,
            "cost_price": 3500.00,
            "market_price": 5299.00,
            "weight": 0.210,
            "is_active": True
        }
        sku_response = integration_test_client.post("/api/v1/product-catalog/skus", json=sku_data)
        assert sku_response.status_code == 201
        sku = sku_response.json()
        
        # 步骤5：添加商品属性
        attributes = [
            {
                "product_id": product_id,
                "attribute_name": "处理器",
                "attribute_value": "骁龙8 Gen 2",
                "attribute_type": "text",
                "is_searchable": True
            },
            {
                "product_id": product_id,
                "attribute_name": "内存",
                "attribute_value": "12GB",
                "attribute_type": "select",
                "is_searchable": True
            }
        ]
        
        for attr_data in attributes:
            attr_response = integration_test_client.post("/api/v1/product-catalog/attributes", json=attr_data)
            assert attr_response.status_code == 201
        
        # 步骤6：添加商品图片
        images = [
            {
                "product_id": product_id,
                "image_url": "https://cdn.mi.com/mi13pro-main.jpg",
                "alt_text": "小米13 Pro主图",
                "sort_order": 1,
                "is_primary": True
            },
            {
                "product_id": product_id,
                "image_url": "https://cdn.mi.com/mi13pro-back.jpg",
                "alt_text": "小米13 Pro背面",
                "sort_order": 2,
                "is_primary": False
            }
        ]
        
        for img_data in images:
            img_response = integration_test_client.post("/api/v1/product-catalog/images", json=img_data)
            assert img_response.status_code == 201
        
        # 步骤7：添加商品标签
        tags = [
            {
                "product_id": product_id,
                "tag_name": "旗舰手机",
                "tag_type": "feature"
            },
            {
                "product_id": product_id,
                "tag_name": "新品上市",
                "tag_type": "promotion"
            }
        ]
        
        for tag_data in tags:
            tag_response = integration_test_client.post("/api/v1/product-catalog/tags", json=tag_data)
            assert tag_response.status_code == 201
        
        # 步骤8：发布商品
        publish_data = {"status": "published"}
        publish_response = integration_test_client.put(f"/api/v1/product-catalog/products/{product_id}/publish", json=publish_data)
        assert publish_response.status_code == 200
        
        # 步骤9：验证完整商品信息
        detail_response = integration_test_client.get(f"/api/v1/product-catalog/products/{product_id}")
        assert detail_response.status_code == 200
        product_detail = detail_response.json()
        
        # 验证商品基本信息
        assert product_detail["name"] == "小米13 Pro"
        assert product_detail["brand_id"] == brand_id
        assert product_detail["category_id"] == category_id
        assert product_detail["status"] == "published"
        
        # 验证SEO信息
        assert product_detail["seo_title"] == "小米13 Pro - 高性能旗舰手机"
        assert "小米,13 Pro" in product_detail["seo_keywords"]


class TestCrossFunctionalIntegration:
    """跨功能集成测试"""

    def test_brand_category_product_relationship(self, integration_test_client, integration_test_db):
        """测试品牌、分类、商品三者关系"""
        # 创建品牌
        brand_data = {"name": "华为", "slug": "huawei", "is_active": True}
        brand_response = integration_test_client.post("/api/v1/product-catalog/brands", json=brand_data)
        brand_id = brand_response.json()["id"]
        
        # 创建分类
        category_data = {"name": "笔记本电脑", "is_active": True}
        category_response = integration_test_client.post("/api/v1/product-catalog/categories", json=category_data)
        category_id = category_response.json()["id"]
        
        # 创建商品
        product_data = {
            "name": "华为MateBook X Pro",
            "brand_id": brand_id,
            "category_id": category_id,
            "status": "published"
        }
        product_response = integration_test_client.post("/api/v1/product-catalog/products", json=product_data)
        product_id = product_response.json()["id"]
        
        # 验证关系查询
        # 通过品牌查询商品
        brand_products_response = integration_test_client.get(f"/api/v1/product-catalog/products?brand_id={brand_id}")
        brand_products = brand_products_response.json()
        assert len(brand_products) == 1
        assert brand_products[0]["name"] == "华为MateBook X Pro"
        
        # 通过分类查询商品
        category_products_response = integration_test_client.get(f"/api/v1/product-catalog/products?category_id={category_id}")
        category_products = category_products_response.json()
        assert len(category_products) == 1
        assert category_products[0]["name"] == "华为MateBook X Pro"

    def test_sku_attribute_integration(self, integration_test_client, integration_test_db):
        """测试SKU与属性的集成功能"""
        # 创建商品
        product_data = {"name": "iPhone 15", "status": "published"}
        product_response = integration_test_client.post("/api/v1/product-catalog/products", json=product_data)
        product_id = product_response.json()["id"]
        
        # 创建多个SKU（不同规格）
        skus_data = [
            {
                "product_id": product_id,
                "sku_code": "IPHONE15-128GB-BLUE",
                "name": "iPhone 15 128GB 蓝色",
                "price": 5999.00
            },
            {
                "product_id": product_id,
                "sku_code": "IPHONE15-256GB-BLUE", 
                "name": "iPhone 15 256GB 蓝色",
                "price": 6999.00
            }
        ]
        
        sku_ids = []
        for sku_data in skus_data:
            sku_response = integration_test_client.post("/api/v1/product-catalog/skus", json=sku_data)
            sku_ids.append(sku_response.json()["id"])
        
        # 为每个SKU添加属性
        sku_attributes = [
            {"sku_id": sku_ids[0], "attribute_name": "存储", "attribute_value": "128GB"},
            {"sku_id": sku_ids[0], "attribute_name": "颜色", "attribute_value": "蓝色"},
            {"sku_id": sku_ids[1], "attribute_name": "存储", "attribute_value": "256GB"},
            {"sku_id": sku_ids[1], "attribute_name": "颜色", "attribute_value": "蓝色"}
        ]
        
        for attr_data in sku_attributes:
            attr_response = integration_test_client.post("/api/v1/product-catalog/sku-attributes", json=attr_data)
            assert attr_response.status_code == 201
        
        # 验证SKU属性查询
        for sku_id in sku_ids:
            sku_detail_response = integration_test_client.get(f"/api/v1/product-catalog/skus/{sku_id}")
            sku_detail = sku_detail_response.json()
            assert "attributes_rel" in sku_detail
            assert len(sku_detail["attributes_rel"]) == 2  # 每个SKU有2个属性

    def test_product_image_management(self, integration_test_client, integration_test_db):
        """测试商品图片管理集成功能"""
        # 创建商品
        product_data = {"name": "测试商品图片", "status": "published"}
        product_response = integration_test_client.post("/api/v1/product-catalog/products", json=product_data)
        product_id = product_response.json()["id"]
        
        # 添加多张图片
        images_data = [
            {
                "product_id": product_id,
                "image_url": "https://example.com/image1.jpg",
                "alt_text": "商品主图",
                "sort_order": 1,
                "is_primary": True
            },
            {
                "product_id": product_id,
                "image_url": "https://example.com/image2.jpg", 
                "alt_text": "商品副图1",
                "sort_order": 2,
                "is_primary": False
            },
            {
                "product_id": product_id,
                "image_url": "https://example.com/image3.jpg",
                "alt_text": "商品副图2", 
                "sort_order": 3,
                "is_primary": False
            }
        ]
        
        image_ids = []
        for img_data in images_data:
            img_response = integration_test_client.post("/api/v1/product-catalog/images", json=img_data)
            assert img_response.status_code == 201
            image_ids.append(img_response.json()["id"])
        
        # 验证图片排序
        product_images_response = integration_test_client.get(f"/api/v1/product-catalog/products/{product_id}/images")
        product_images = product_images_response.json()
        assert len(product_images) == 3
        
        # 验证主图设置
        primary_images = [img for img in product_images if img["is_primary"]]
        assert len(primary_images) == 1
        assert primary_images[0]["alt_text"] == "商品主图"
        
        # 验证排序顺序
        sorted_images = sorted(product_images, key=lambda x: x["sort_order"])
        assert sorted_images[0]["sort_order"] == 1
        assert sorted_images[1]["sort_order"] == 2
        assert sorted_images[2]["sort_order"] == 3


class TestPerformanceIntegration:
    """性能集成测试"""

    def test_batch_product_creation(self, integration_test_client, integration_test_db):
        """测试批量创建商品的性能"""
        import time
        
        # 创建品牌和分类
        brand_data = {"name": "批量测试品牌", "slug": "batch-test", "is_active": True}
        brand_response = integration_test_client.post("/api/v1/product-catalog/brands", json=brand_data)
        brand_id = brand_response.json()["id"]
        
        category_data = {"name": "批量测试分类", "is_active": True}
        category_response = integration_test_client.post("/api/v1/product-catalog/categories", json=category_data)
        category_id = category_response.json()["id"]
        
        # 批量创建商品
        batch_size = 10
        start_time = time.time()
        
        for i in range(batch_size):
            product_data = {
                "name": f"批量商品 {i+1}",
                "description": f"这是第{i+1}个批量创建的商品",
                "brand_id": brand_id,
                "category_id": category_id,
                "status": "published",
                "sort_order": i + 1
            }
            response = integration_test_client.post("/api/v1/product-catalog/products", json=product_data)
            assert response.status_code == 201
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # 验证性能指标（每个商品创建时间应小于0.5秒）
        average_time_per_product = creation_time / batch_size
        assert average_time_per_product < 0.5, f"商品创建时间过长: {average_time_per_product:.3f}秒/个"
        
        # 验证所有商品都被成功创建
        all_products_response = integration_test_client.get("/api/v1/product-catalog/products")
        all_products = all_products_response.json()
        batch_products = [p for p in all_products if p["name"].startswith("批量商品")]
        assert len(batch_products) == batch_size

    def test_complex_search_performance(self, integration_test_client, integration_test_db):
        """测试复杂搜索查询的性能"""
        import time
        
        # 创建测试数据
        brand_data = {"name": "搜索测试品牌", "slug": "search-test", "is_active": True}
        brand_response = integration_test_client.post("/api/v1/product-catalog/brands", json=brand_data)
        brand_id = brand_response.json()["id"]
        
        category_data = {"name": "搜索测试分类", "is_active": True}
        category_response = integration_test_client.post("/api/v1/product-catalog/categories", json=category_data)
        category_id = category_response.json()["id"]
        
        # 创建20个商品用于搜索测试
        for i in range(20):
            product_data = {
                "name": f"搜索商品 {i+1}",
                "brand_id": brand_id,
                "category_id": category_id,
                "status": "published" if i % 2 == 0 else "draft",
                "view_count": i * 10,
                "sale_count": i * 2
            }
            integration_test_client.post("/api/v1/product-catalog/products", json=product_data)
        
        # 测试复杂搜索查询性能
        search_queries = [
            f"/api/v1/product-catalog/products?brand_id={brand_id}&status=published",
            f"/api/v1/product-catalog/products?category_id={category_id}&sort_by=view_count&sort_order=desc",
            f"/api/v1/product-catalog/products?keyword=搜索商品&status=published",
            f"/api/v1/product-catalog/products?brand_id={brand_id}&category_id={category_id}&sort_by=sale_count"
        ]
        
        for query in search_queries:
            start_time = time.time()
            response = integration_test_client.get(query)
            end_time = time.time()
            
            assert response.status_code == 200
            query_time = end_time - start_time
            assert query_time < 1.0, f"搜索查询时间过长: {query_time:.3f}秒 for {query}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])