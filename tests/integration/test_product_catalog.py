"""
产品目录模块单元测试

根据docs/standards/testing-standards.md规范实现
测试覆盖：
- 产品模型数据验证和关系
- 品牌管理功能
- 分类管理功能
- SKU规格管理
- 商品属性、图片、标签管理
- API接口功能测试

使用conftest.py中的标准测试配置，确保测试独立性和认证正确性
"""

import pytest
from decimal import Decimal

from app.modules.product_catalog.models import (
    Product, Category, Brand, SKU, ProductAttribute, ProductImage, ProductTag
)
from app.modules.product_catalog.schemas import (
    ProductCreate, CategoryCreate, BrandCreate, SKUCreate
)


# 使用conftest.py中的标准测试配置
# - unit_test_engine: 内存数据库引擎  
# - integration_test_db: 数据库会话
# - integration_test_client: 已配置认证mock的测试客户端
# - mock_admin_user: mock管理员用户


# ============ 模型测试 ============

class TestCategoryModel:
    """分类模型测试"""

    def test_create_category_success(self, integration_test_db):
        """测试成功创建分类"""
        category = Category(
            name="电子产品",
            sort_order=1,
            is_active=True
        )
        integration_test_db.add(category)
        integration_test_db.commit()
        integration_test_db.refresh(category)
        
        assert category.id is not None
        assert category.name == "电子产品"
        assert category.sort_order == 1
        assert category.is_active is True
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_category_hierarchy(self, integration_test_db):
        """测试分类层次结构"""
        # 创建父分类
        parent = Category(name="数码产品", sort_order=1)
        integration_test_db.add(parent)
        integration_test_db.commit()
        integration_test_db.refresh(parent)
        
        # 创建子分类
        child = Category(name="手机", parent_id=parent.id, sort_order=1)
        integration_test_db.add(child)
        integration_test_db.commit()
        integration_test_db.refresh(child)
        
        assert child.parent_id == parent.id
        assert len(parent.children) == 1
        assert parent.children[0].name == "手机"

    def test_category_soft_delete(self, integration_test_db):
        """测试分类软删除"""
        category = Category(name="测试分类")
        integration_test_db.add(category)
        integration_test_db.commit()
        
        # 执行软删除
        category.soft_delete()
        integration_test_db.commit()
        
        assert category.is_deleted is True
        assert category.deleted_at is not None


class TestBrandModel:
    """品牌模型测试"""

    def test_create_brand_success(self, integration_test_db):
        """测试成功创建品牌"""
        brand = Brand(
            name="苹果",
            slug="apple",
            description="Apple Inc. 科技公司",
            is_active=True
        )
        integration_test_db.add(brand)
        integration_test_db.commit()
        integration_test_db.refresh(brand)
        
        assert brand.id is not None
        assert brand.name == "苹果"
        assert brand.slug == "apple"
        assert brand.is_active is True

    def test_brand_unique_constraints(self, integration_test_db):
        """测试品牌唯一性约束"""
        brand1 = Brand(name="华为", slug="huawei")
        brand2 = Brand(name="华为", slug="huawei-2")
        
        integration_test_db.add(brand1)
        integration_test_db.commit()
        
        # 尝试添加重复名称的品牌
        integration_test_db.add(brand2)
        with pytest.raises(Exception):  # 应该触发唯一约束错误
            integration_test_db.commit()


class TestProductModel:
    """商品模型测试"""

    def test_create_product_success(self, integration_test_db):
        """测试成功创建商品"""
        # 创建品牌和分类
        brand = Brand(name="小米", slug="xiaomi")
        category = Category(name="手机")
        integration_test_db.add_all([brand, category])
        integration_test_db.commit()
        integration_test_db.refresh(brand)
        integration_test_db.refresh(category)
        
        # 创建商品
        product = Product(
            name="小米13 Pro",
            description="小米13 Pro 高端旗舰手机",
            brand_id=brand.id,
            category_id=category.id,
            status="published",
            seo_title="小米13 Pro - 高端旗舰手机",
            sort_order=1,
            view_count=0,
            sale_count=0
        )
        integration_test_db.add(product)
        integration_test_db.commit()
        integration_test_db.refresh(product)
        
        assert product.id is not None
        assert product.name == "小米13 Pro"
        assert product.brand_id == brand.id
        assert product.category_id == category.id
        assert product.status == "published"

    def test_product_relationships(self, integration_test_db):
        """测试商品关系"""
        # 创建品牌和分类
        brand = Brand(name="华为", slug="huawei")
        category = Category(name="笔记本")
        integration_test_db.add_all([brand, category])
        integration_test_db.commit()
        integration_test_db.refresh(brand)
        integration_test_db.refresh(category)
        
        # 创建商品
        product = Product(
            name="华为MateBook",
            brand_id=brand.id,
            category_id=category.id,
            status="published"
        )
        integration_test_db.add(product)
        integration_test_db.commit()
        integration_test_db.refresh(product)
        
        # 验证关系
        assert product.brand.name == "华为"
        assert product.category.name == "笔记本"
        assert brand.products[0].name == "华为MateBook"
        assert category.products[0].name == "华为MateBook"

    def test_product_seo_fields(self, integration_test_db):
        """测试商品SEO字段"""
        product = Product(
            name="iPhone 15",
            seo_title="iPhone 15 - 最新苹果手机",
            seo_description="iPhone 15 具有强大的A16芯片和先进的摄像系统",
            seo_keywords="iPhone,苹果,手机,A16"
        )
        integration_test_db.add(product)
        integration_test_db.commit()
        
        assert product.seo_title == "iPhone 15 - 最新苹果手机"
        assert product.seo_keywords == "iPhone,苹果,手机,A16"

    def test_product_statistics(self, integration_test_db):
        """测试商品统计字段"""
        product = Product(
            name="测试商品",
            view_count=100,
            sale_count=25,
            sort_order=5
        )
        integration_test_db.add(product)
        integration_test_db.commit()
        
        assert product.view_count == 100
        assert product.sale_count == 25
        assert product.sort_order == 5


class TestSKUModel:
    """SKU模型测试"""

    def test_create_sku_success(self, integration_test_db):
        """测试成功创建SKU"""
        # 创建商品
        product = Product(name="测试商品")
        integration_test_db.add(product)
        integration_test_db.commit()
        integration_test_db.refresh(product)
        
        # 创建SKU
        sku = SKU(
            product_id=product.id,
            sku_code="TEST-001",
            name="测试SKU",
            price=Decimal("99.99"),
            cost_price=Decimal("50.00"),
            weight=Decimal("0.5"),
            is_active=True
        )
        integration_test_db.add(sku)
        integration_test_db.commit()
        integration_test_db.refresh(sku)
        
        assert sku.id is not None
        assert sku.sku_code == "TEST-001"
        assert sku.price == Decimal("99.99")
        assert sku.cost_price == Decimal("50.00")
        assert sku.product_id == product.id

    def test_sku_unique_code(self, integration_test_db):
        """测试SKU代码唯一性"""
        product = Product(name="测试商品")
        integration_test_db.add(product)
        integration_test_db.commit()
        integration_test_db.refresh(product)
        
        sku1 = SKU(product_id=product.id, sku_code="UNIQUE-001", price=Decimal("10.00"))
        sku2 = SKU(product_id=product.id, sku_code="UNIQUE-001", price=Decimal("20.00"))
        
        integration_test_db.add(sku1)
        integration_test_db.commit()
        
        integration_test_db.add(sku2)
        with pytest.raises(Exception):  # 应该触发唯一约束错误
            integration_test_db.commit()


class TestProductAttributeModel:
    """商品属性模型测试"""

    def test_create_product_attribute(self, integration_test_db):
        """测试创建商品属性"""
        product = Product(name="测试商品")
        integration_test_db.add(product)
        integration_test_db.commit()
        integration_test_db.refresh(product)
        
        attribute = ProductAttribute(
            product_id=product.id,
            attribute_name="颜色",
            attribute_value="钛原色",
            attribute_type="select",
            is_searchable=True
        )
        integration_test_db.add(attribute)
        integration_test_db.commit()
        integration_test_db.refresh(attribute)
        
        assert attribute.product_id == product.id
        assert attribute.attribute_name == "颜色"
        assert attribute.attribute_value == "钛原色"
        assert attribute.is_searchable is True


# ============ API测试 ============

class TestCategoryAPI:
    """分类API测试"""

    def test_create_category_api(self, integration_test_client):
        """测试创建分类API"""
        category_data = {
            "name": "数码产品",
            "sort_order": 1,
            "is_active": True
        }
        response = integration_test_client.post("/api/v1/product-catalog/categories", json=category_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "数码产品"
        assert data["sort_order"] == 1

    def test_get_categories_list(self, integration_test_client):
        """测试获取分类列表"""
        # 创建测试分类
        category_data = {"name": "测试分类", "sort_order": 1}
        integration_test_client.post("/api/v1/product-catalog/categories", json=category_data)
        
        # 获取列表
        response = integration_test_client.get("/api/v1/product-catalog/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["name"] == "测试分类"


class TestBrandAPI:
    """品牌API测试"""

    def test_create_brand_api(self, integration_test_client):
        """测试创建品牌API"""
        brand_data = {
            "name": "小米",
            "slug": "xiaomi",
            "description": "小米科技",
            "is_active": True
        }
        response = integration_test_client.post("/api/v1/product-catalog/brands", json=brand_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "小米"
        assert data["slug"] == "xiaomi"


class TestProductAPI:
    """商品API测试"""

    def test_create_product_api(self, integration_test_client, integration_test_db):
        """测试创建商品API"""
        # 首先创建品牌和分类
        brand = Brand(name="苹果", slug="apple")
        category = Category(name="手机")
        integration_test_db.add_all([brand, category])
        integration_test_db.commit()
        integration_test_db.refresh(brand)
        integration_test_db.refresh(category)
        
        product_data = {
            "name": "iPhone 15 Pro",
            "description": "最新款iPhone",
            "brand_id": brand.id,
            "category_id": category.id,
            "status": "published",
            "seo_title": "iPhone 15 Pro - 苹果最新旗舰手机"
        }
        
        response = integration_test_client.post("/api/v1/product-catalog/products", json=product_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "iPhone 15 Pro"
        assert data["brand_id"] == brand.id
        assert data["category_id"] == category.id

    def test_get_products_list(self, integration_test_client, integration_test_db):
        """测试获取商品列表"""
        # 创建测试商品
        product = Product(name="测试商品", status="published")
        integration_test_db.add(product)
        integration_test_db.commit()
        
        response = integration_test_client.get("/api/v1/product-catalog/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_product_by_id(self, integration_test_client, integration_test_db):
        """测试根据ID获取商品"""
        # 创建测试商品
        product = Product(name="指定商品", status="published")
        integration_test_db.add(product)
        integration_test_db.commit()
        integration_test_db.refresh(product)
        
        response = integration_test_client.get(f"/api/v1/product-catalog/products/{product.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "指定商品"
        assert data["id"] == product.id

    def test_update_product(self, integration_test_client, integration_test_db):
        """测试更新商品"""
        # 创建测试商品
        product = Product(name="原始名称", status="draft")
        integration_test_db.add(product)
        integration_test_db.commit()
        integration_test_db.refresh(product)
        
        update_data = {
            "name": "更新名称",
            "status": "published"
        }
        
        response = integration_test_client.put(f"/api/v1/product-catalog/products/{product.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新名称"
        assert data["status"] == "published"

    def test_delete_product(self, integration_test_client, integration_test_db):
        """测试删除商品（软删除）"""
        # 创建测试商品
        product = Product(name="待删除商品")
        integration_test_db.add(product)
        integration_test_db.commit()
        integration_test_db.refresh(product)
        
        response = integration_test_client.delete(f"/api/v1/product-catalog/products/{product.id}")
        assert response.status_code == 204
        
        # 验证软删除
        integration_test_db.refresh(product)
        assert product.is_deleted is True


# ============ 业务逻辑测试 ============

class TestProductBusiness:
    """商品业务逻辑测试"""

    def test_product_search_by_category(self, integration_test_client, integration_test_db):
        """测试按分类搜索商品"""
        # 创建分类和商品
        category = Category(name="笔记本电脑")
        integration_test_db.add(category)
        integration_test_db.commit()
        integration_test_db.refresh(category)
        
        product = Product(name="ThinkPad", category_id=category.id, status="published")
        integration_test_db.add(product)
        integration_test_db.commit()
        
        response = integration_test_client.get(f"/api/v1/product-catalog/products?category_id={category.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "ThinkPad"

    def test_product_search_by_brand(self, integration_test_client, integration_test_db):
        """测试按品牌搜索商品"""
        # 创建品牌和商品
        brand = Brand(name="联想", slug="lenovo")
        integration_test_db.add(brand)
        integration_test_db.commit()
        integration_test_db.refresh(brand)
        
        product = Product(name="ThinkPad X1", brand_id=brand.id, status="published")
        integration_test_db.add(product)
        integration_test_db.commit()
        
        response = integration_test_client.get(f"/api/v1/product-catalog/products?brand_id={brand.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "ThinkPad X1"

    def test_product_status_filtering(self, integration_test_client, integration_test_db):
        """测试商品状态过滤"""
        # 创建不同状态的商品
        product_draft = Product(name="草稿商品", status="draft")
        product_published = Product(name="已发布商品", status="published")
        integration_test_db.add_all([product_draft, product_published])
        integration_test_db.commit()
        
        # 测试只获取已发布商品
        response = integration_test_client.get("/api/v1/product-catalog/products?status=published")
        assert response.status_code == 200
        data = response.json()
        published_names = [p["name"] for p in data]
        assert "已发布商品" in published_names
        assert "草稿商品" not in published_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
