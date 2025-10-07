"""
Auto Generated Test - 已生成到正式目录

文件路径: tests/factories/product_catalog_factories.py
生成时间: 2025-10-07 12:05:52
生成工具: tools/generate_test_template.py v2.0
状态: GENERATED - 需要经过代码审查和测试验证

说明: 此文件已生成到正式目录，请进行代码审查和测试验证。
     审查通过后即可直接用于项目测试。
     
流程: 生成 -> 审查 -> 验证 -> 提交版本控制
"""


import factory
import factory.fuzzy
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

# 处理表重定义警告的配置
import warnings
warnings.filterwarnings('ignore', message='.*declarative base.*')
warnings.filterwarnings('ignore', message='.*Table.*already defined.*')

from app.modules.product_catalog.models import (
    Brand, Category, Product, ProductAttribute, ProductImage, ProductTag, SKU, SKUAttribute
)


class BrandFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的Brand工厂类"""
    
    class Meta:
        model = Brand
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(Brand, "name") else None

    name = factory.Sequence(lambda n: f'name_{n}')
    slug = factory.Sequence(lambda n: f'slug_{n}')
    description = factory.Faker('text', max_nb_chars=200)
    logo_url = factory.Faker('url')
    website_url = factory.Faker('url')
    is_active = True
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的Category工厂类"""
    
    class Meta:
        model = Category
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(Category, "name") else None

    name = factory.Sequence(lambda n: f'name_{n}')
    description = factory.Faker('text', max_nb_chars=200)
    parent_id = None  # 自引用字段，避免循环依赖
    sort_order = factory.Faker('random_int', min=1, max=1000)
    is_active = True
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    is_deleted = False
    deleted_at = factory.Faker('date_time_this_year')


class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的Product工厂类"""
    
    class Meta:
        model = Product
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(Product, "name") else None

    name = factory.Sequence(lambda n: f'name_{n}')
    description = factory.Faker('text', max_nb_chars=200)
    brand = factory.SubFactory(BrandFactory)
    category = factory.SubFactory(CategoryFactory)
    status = factory.Faker('word')
    published_at = factory.Faker('date_time_this_year')
    seo_title = factory.Faker('sentence', nb_words=4)
    seo_description = factory.Faker('text', max_nb_chars=200)
    seo_keywords = factory.Faker('text', max_nb_chars=200)
    sort_order = factory.Faker('random_int', min=1, max=1000)
    view_count = factory.Faker('random_int', min=1, max=1000)
    sale_count = factory.Faker('random_int', min=1, max=1000)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    is_deleted = False
    deleted_at = factory.Faker('date_time_this_year')


class ProductAttributeFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的ProductAttribute工厂类"""
    
    class Meta:
        model = ProductAttribute
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(ProductAttribute, "name") else None

    product = factory.SubFactory(ProductFactory)
    attribute_name = factory.Sequence(lambda n: f'attribute_name_{n}')
    attribute_value = factory.Faker('text', max_nb_chars=200)
    attribute_type = factory.Faker('word')
    is_searchable = factory.Faker('boolean')
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class ProductImageFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的ProductImage工厂类"""
    
    class Meta:
        model = ProductImage
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(ProductImage, "name") else None

    product = factory.SubFactory(ProductFactory)
    sku_id = None  # 可空外键，避免前向引用错误 (目标: SKUFactory)
    image_url = factory.Faker('url')
    alt_text = factory.Faker('text', max_nb_chars=200)
    sort_order = factory.Faker('random_int', min=1, max=1000)
    is_primary = factory.Faker('boolean')
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class ProductTagFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的ProductTag工厂类"""
    
    class Meta:
        model = ProductTag
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(ProductTag, "name") else None

    product = factory.SubFactory(ProductFactory)
    tag_name = factory.Sequence(lambda n: f'tag_name_{n}')
    tag_type = factory.Faker('word')
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class SKUFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的SKU工厂类"""
    
    class Meta:
        model = SKU
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(SKU, "name") else None

    product = factory.SubFactory(ProductFactory)
    sku_code = factory.Sequence(lambda n: f'SKU_CODE_{{n:06d}}')
    name = factory.Sequence(lambda n: f'name_{n}')
    price = factory.LazyAttribute(lambda obj: Decimal('99.99'))
    cost_price = factory.LazyAttribute(lambda obj: Decimal('99.99'))
    market_price = factory.LazyAttribute(lambda obj: Decimal('99.99'))
    weight = factory.LazyAttribute(lambda obj: Decimal('10.00'))
    volume = factory.LazyAttribute(lambda obj: Decimal('10.00'))
    is_active = True
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class SKUAttributeFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的SKUAttribute工厂类"""
    
    class Meta:
        model = SKUAttribute
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(SKUAttribute, "name") else None

    sku = factory.SubFactory(SKUFactory)
    attribute_name = factory.Sequence(lambda n: f'attribute_name_{n}')
    attribute_value = factory.Faker('text', max_nb_chars=200)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class ProductCatalogFactoryManager:
    """智能生成的product_catalog模块工厂管理器
    
    提供便捷的测试数据创建方法和常见业务场景的数据组合
    
    双工厂模式中的Factory Boy工厂管理器：
    - 适用于单元测试(test_services/、*_standalone.py)
    - 轻量级内存创建，不依赖真实数据库连接
    - 智能处理外键依赖，避免FOREIGN KEY constraint failed
    
    关键方法：
    - setup_factories(): 设置数据库会话
    - create_sample_data(): 按依赖顺序创建完整测试数据集
    - create_test_scenario(): 创建特定业务场景的数据
    """
    
    @staticmethod
    def setup_factories(session: Session):
        """设置所有工厂的数据库会话
        
        重要说明：
        - 必须在创建Factory实例之前调用
        - 确保所有Factory使用相同的数据库会话
        - 支持事务回滚和数据隔离
        """
        BrandFactory._meta.sqlalchemy_session = session
        CategoryFactory._meta.sqlalchemy_session = session
        ProductFactory._meta.sqlalchemy_session = session
        ProductAttributeFactory._meta.sqlalchemy_session = session
        ProductImageFactory._meta.sqlalchemy_session = session
        ProductTagFactory._meta.sqlalchemy_session = session
        SKUFactory._meta.sqlalchemy_session = session
        SKUAttributeFactory._meta.sqlalchemy_session = session

    @staticmethod
    def create_sample_data(session: Session) -> dict:
        """创建样本测试数据 - 按依赖顺序创建避免外键约束失败
        
        核心算法说明：
        1. 使用_sort_models_by_dependencies()的拓扑排序结果
        2. 按依赖顺序逐个创建Factory实例
        3. 确保被依赖模型(如User)在依赖模型(如RolePermission)之前创建
        
        解决的关键问题：
        - FOREIGN KEY constraint failed错误
        - 例如：RolePermission.granted_by引用User.id，必须先创建User
        
        返回结果：
        - dict: 包含所有创建的模型实例，key为模型名小写
        - 可以通过data['user']、data['role']等方式访问
        
        使用示例：
        >>> sample_data = factory_manager.create_sample_data(unit_test_db)
        >>> user = sample_data['user']  # 获取创建的User实例
        >>> role = sample_data['role']  # 获取创建的Role实例
        """
        ProductCatalogFactoryManager.setup_factories(session)
        
        data = {}
        data['brand'] = BrandFactory()  # 创建Brand实例
        data['category'] = CategoryFactory()  # 创建Category实例
        data['product'] = ProductFactory()  # 创建Product实例
        data['productattribute'] = ProductAttributeFactory()  # 创建ProductAttribute实例
        data['productimage'] = ProductImageFactory()  # 创建ProductImage实例
        data['producttag'] = ProductTagFactory()  # 创建ProductTag实例
        data['sku'] = SKUFactory()  # 创建SKU实例
        data['skuattribute'] = SKUAttributeFactory()  # 创建SKUAttribute实例
        
        session.commit()  # 提交所有创建的数据
        return data
        
    @staticmethod
    def create_test_scenario(session: Session, scenario: str = 'basic') -> dict:
        """创建特定测试场景的数据
        
        扩展点说明：
        - 目前默认调用create_sample_data()
        - 未来可以根据scenario参数创建不同的业务场景
        - 例如：'admin_user'、'guest_user'、'complex_permissions'等
        """
        # 可以根据具体业务需求扩展不同场景
        return ProductCatalogFactoryManager.create_sample_data(session)