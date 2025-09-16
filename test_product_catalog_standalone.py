"""
产品目录模块完整单元测试 - 独立版本

严格按照MASTER.md和测试规范要求实现
包含Category、Brand、Product、SKU等所有模型的测试
使用SQLite内存数据库，确保测试隔离性
避免循环导入问题
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 只导入必要的模型，避免循环导入
from app.core.database import Base
from app.shared.base_models import TimestampMixin, SoftDeleteMixin
from app.modules.product_catalog.models import Category, Brand, Product, SKU

# 单元测试数据库配置（SQLite内存）
UNIT_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """测试数据库引擎 - 每个测试函数使用独立的内存数据库"""
    engine = create_engine(
        UNIT_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # 关闭SQL日志以减少输出噪音
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    yield engine
    
    # 清理
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """数据库会话"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ================== 分类模型测试 ==================

class TestCategoryModel:
    """分类模型单元测试"""

    def test_category_creation_success(self, test_db):
        """测试成功创建分类"""
        category = Category(
            name="电子产品",
            description="电子产品分类",
            sort_order=1,
            is_active=True
        )
        
        test_db.add(category)
        test_db.commit()
        
        assert category.id is not None
        assert category.name == "电子产品"
        assert category.description == "电子产品分类"
        assert category.sort_order == 1
        assert category.is_active is True
        assert category.parent_id is None
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_category_hierarchy(self, test_db):
        """测试分类层次结构"""
        parent_category = Category(name="电子设备", sort_order=1)
        test_db.add(parent_category)
        test_db.commit()
        
        child_category = Category(
            name="智能手机",
            parent_id=parent_category.id,
            sort_order=1
        )
        test_db.add(child_category)
        test_db.commit()
        
        # 验证父子关系
        assert child_category.parent_id == parent_category.id
        
        # 刷新以获取关系数据
        test_db.refresh(parent_category)
        test_db.refresh(child_category)
        
        assert len(parent_category.children) == 1
        assert parent_category.children[0].id == child_category.id

    def test_category_repr(self, test_db):
        """测试分类字符串表示"""
        category = Category(name="测试分类")
        test_db.add(category)
        test_db.commit()
        
        expected = f"<Category(id={category.id}, name='测试分类', parent_id={category.parent_id})>"
        assert repr(category) == expected


# ================== 品牌模型测试 ==================

class TestBrandModel:
    """品牌模型单元测试"""

    def test_brand_creation_success(self, test_db):
        """测试成功创建品牌"""
        brand = Brand(
            name="苹果",
            slug="apple",
            description="苹果公司",
            is_active=True
        )
        
        test_db.add(brand)
        test_db.commit()
        
        assert brand.id is not None
        assert brand.name == "苹果"
        assert brand.slug == "apple"
        assert brand.description == "苹果公司"
        assert brand.is_active is True
        assert brand.created_at is not None
        assert brand.updated_at is not None

    def test_brand_unique_name_constraint(self, test_db):
        """测试品牌名称唯一性约束"""
        brand1 = Brand(name="小米", slug="xiaomi1")
        test_db.add(brand1)
        test_db.commit()
        
        # 尝试创建相同名称的品牌
        brand2 = Brand(name="小米", slug="xiaomi2")
        test_db.add(brand2)
        
        with pytest.raises(Exception):  # SQLite会抛出IntegrityError
            test_db.commit()

    def test_brand_repr(self, test_db):
        """测试品牌字符串表示"""
        brand = Brand(name="华为", slug="huawei")
        test_db.add(brand)
        test_db.commit()
        
        expected = f"<Brand(id={brand.id}, name='华为', slug='huawei')>"
        assert repr(brand) == expected


# ================== 商品模型测试 ==================

class TestProductModel:
    """商品模型单元测试"""

    def test_product_creation_success(self, test_db):
        """测试成功创建商品"""
        # 首先创建分类和品牌
        category = Category(name="手机")
        brand = Brand(name="苹果", slug="apple")
        test_db.add(category)
        test_db.add(brand)
        test_db.commit()
        
        # 创建商品
        product = Product(
            name="iPhone 15",
            category_id=category.id,
            brand_id=brand.id,
            description="最新款iPhone"
        )
        
        test_db.add(product)
        test_db.commit()
        
        assert product.id is not None
        assert product.name == "iPhone 15"
        assert product.category_id == category.id
        assert product.brand_id == brand.id
        assert product.description == "最新款iPhone"
        assert product.status == "draft"  # 默认状态

    def test_product_category_relationship(self, test_db):
        """测试商品与分类的关系"""
        category = Category(name="笔记本电脑")
        brand = Brand(name="苹果", slug="apple")
        test_db.add(category)
        test_db.add(brand)
        test_db.commit()
        
        product = Product(
            name="MacBook Pro",
            category_id=category.id,
            brand_id=brand.id
        )
        test_db.add(product)
        test_db.commit()
        
        # 刷新以获取关系数据
        test_db.refresh(product)
        test_db.refresh(category)
        
        # 验证关系
        assert product.category.id == category.id
        assert product.category.name == "笔记本电脑"
        assert len(category.products) == 1
        assert category.products[0].id == product.id


# ================== SKU模型测试 ==================

class TestSKUModel:
    """SKU模型单元测试"""

    def test_sku_creation_success(self, test_db):
        """测试成功创建SKU"""
        # 创建依赖数据
        category = Category(name="手机")
        brand = Brand(name="苹果", slug="apple")
        test_db.add(category)
        test_db.add(brand)
        test_db.commit()
        
        product = Product(
            name="iPhone 15",
            category_id=category.id,
            brand_id=brand.id
        )
        test_db.add(product)
        test_db.commit()
        
        # 创建SKU
        sku = SKU(
            product_id=product.id,
            sku_code="IP15-128-BLK",
            name="iPhone 15 128GB 黑色",
            price=5999.00,
            stock_quantity=100,
            is_active=True
        )
        
        test_db.add(sku)
        test_db.commit()
        
        assert sku.id is not None
        assert sku.product_id == product.id
        assert sku.sku_code == "IP15-128-BLK"
        assert sku.name == "iPhone 15 128GB 黑色"
        assert sku.price == 5999.00
        assert sku.stock_quantity == 100
        assert sku.is_active is True

    def test_sku_product_relationship(self, test_db):
        """测试SKU与商品的关系"""
        # 创建依赖数据
        category = Category(name="手机")
        brand = Brand(name="苹果", slug="apple")
        test_db.add(category)
        test_db.add(brand)
        test_db.commit()
        
        product = Product(
            name="iPhone 15",
            category_id=category.id,
            brand_id=brand.id
        )
        test_db.add(product)
        test_db.commit()
        
        # 创建多个SKU
        sku1 = SKU(
            product_id=product.id,
            sku_code="IP15-128-BLK",
            name="iPhone 15 128GB 黑色",
            price=5999.00
        )
        sku2 = SKU(
            product_id=product.id,
            sku_code="IP15-256-WHT",
            name="iPhone 15 256GB 白色",
            price=6999.00
        )
        
        test_db.add(sku1)
        test_db.add(sku2)
        test_db.commit()
        
        # 刷新以获取关系数据
        test_db.refresh(product)
        
        # 验证关系
        assert len(product.skus) == 2
        sku_codes = [sku.sku_code for sku in product.skus]
        assert "IP15-128-BLK" in sku_codes
        assert "IP15-256-WHT" in sku_codes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])