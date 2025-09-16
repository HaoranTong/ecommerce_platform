"""
产品目录模块完整单元测试

严格按照用户认证模块成功测试的模式实现
使用SQLite内存数据库，确保测试隔离性
参考：tests/test_user_auth_complete.py 的成功配置
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# 只导入必要的模型，避免循环导入
from app.core.database import Base
from app.modules.product_catalog.models import Category, Brand, Product, SKU

# 单元测试数据库配置（SQLite内存）
UNIT_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """测试数据库引擎 - 每个测试函数使用独立的内存数据库"""
    engine = create_engine(
        UNIT_TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """测试数据库会话 - 每个测试使用独立的session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()  # 确保测试间的数据隔离
        session.close()


# ============ Category模型测试 ============

class TestCategoryModel:
    """分类模型测试 - 参考用户认证模块的成功模式"""

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
        test_db.refresh(category)
        
        assert category.id is not None
        assert category.name == "电子产品"
        assert category.description == "电子产品分类"
        assert category.sort_order == 1
        assert category.is_active is True
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_category_hierarchy(self, test_db):
        """测试分类层次结构"""
        parent_category = Category(name="电子设备", sort_order=1)
        test_db.add(parent_category)
        test_db.commit()
        test_db.refresh(parent_category)

        child_category = Category(
            name="手机", 
            parent_id=parent_category.id,
            sort_order=1
        )
        test_db.add(child_category)
        test_db.commit()
        test_db.refresh(child_category)

        assert child_category.parent_id == parent_category.id
        assert child_category.parent == parent_category
        assert child_category in parent_category.children

    def test_category_repr(self, test_db):
        """测试分类字符串表示"""
        category = Category(name="测试分类")
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        repr_str = repr(category)
        assert "Category" in repr_str
        assert "测试分类" in repr_str
        assert str(category.id) in repr_str


# ============ Brand模型测试 ============

class TestBrandModel:
    """品牌模型测试"""

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
        test_db.refresh(brand)
        
        assert brand.id is not None
        assert brand.name == "苹果"
        assert brand.slug == "apple"
        assert brand.description == "苹果公司"
        assert brand.is_active is True

    def test_brand_unique_name_constraint(self, test_db):
        """测试品牌名称唯一性约束"""
        brand1 = Brand(name="小米", slug="xiaomi1")
        brand2 = Brand(name="小米", slug="xiaomi2")  # 同名品牌
        
        test_db.add(brand1)
        test_db.commit()
        
        test_db.add(brand2)
        with pytest.raises(Exception):  # 应该抛出唯一性约束异常
            test_db.commit()

    def test_brand_repr(self, test_db):
        """测试品牌字符串表示"""
        brand = Brand(name="华为", slug="huawei")
        test_db.add(brand)
        test_db.commit()
        test_db.refresh(brand)
        
        repr_str = repr(brand)
        assert "Brand" in repr_str
        assert "华为" in repr_str
        assert "huawei" in repr_str


# ============ Product模型测试 ============

class TestProductModel:
    """商品模型测试"""

    def test_product_creation_success(self, test_db):
        """测试成功创建商品"""
        # 首先创建分类和品牌
        category = Category(name="手机")
        brand = Brand(name="苹果", slug="apple")
        test_db.add_all([category, brand])
        test_db.commit()
        test_db.refresh(category)
        test_db.refresh(brand)

        product = Product(
            name="iPhone 15 Pro",
            description="最新款iPhone",
            category_id=category.id,
            brand_id=brand.id,
            status="published",
            is_active=True
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)
        
        assert product.id is not None
        assert product.name == "iPhone 15 Pro"
        assert product.category_id == category.id
        assert product.brand_id == brand.id
        assert product.status == "published"
        assert product.is_active is True

    def test_product_category_relationship(self, test_db):
        """测试商品与分类的关系"""
        category = Category(name="笔记本电脑")
        brand = Brand(name="联想", slug="lenovo")
        test_db.add_all([category, brand])
        test_db.commit()

        product = Product(
            name="ThinkPad X1", 
            category_id=category.id,
            brand_id=brand.id
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        assert product.category == category
        assert product.brand == brand
        assert product in category.products


if __name__ == "__main__":
    pytest.main([__file__, "-v"])