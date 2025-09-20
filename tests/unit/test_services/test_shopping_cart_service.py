"""
Shopping_Cart 服务层测试套件

测试类型: 单元测试 (Service)
数据策略: SQLite内存数据库, unit_test_db fixture
生成时间: 2025-09-20 09:43:58

根据testing-standards.md第54-68行服务测试规范
"""

import pytest
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import Shopping_CartFactory, UserFactory

# Fixture导入
from tests.conftest import unit_test_db

# 被测模块导入
from app.modules.shopping_cart.service import Shopping_CartService
from app.modules.shopping_cart.models import Shopping_Cart


class TestShopping_CartService:
    """服务层业务逻辑测试"""
    
    def setup_method(self):
        """测试准备"""
        self.test_data = Shopping_CartFactory.build_dict()
        
    def test_create_shopping_cart_with_valid_data(self, unit_test_db: Session):
        """测试创建shopping_cart - 有效数据"""
        # Arrange
        service = Shopping_CartService(unit_test_db)
        create_data = self.test_data
        
        # Act
        created_shopping_cart = service.create(create_data)
        
        # Assert
        assert created_shopping_cart is not None
        assert created_shopping_cart.id is not None
        assert hasattr(created_shopping_cart, 'created_at')
        
        # 验证数据库存储
        db_shopping_cart = unit_test_db.query(Shopping_Cart).filter_by(
            id=created_shopping_cart.id
        ).first()
        assert db_shopping_cart is not None
        
    def test_get_shopping_cart_by_id_exists(self, unit_test_db: Session):
        """测试按ID查询shopping_cart - 存在"""
        # 准备测试数据
        shopping_cart_data = Shopping_CartFactory.create_dict()
        service = Shopping_CartService(unit_test_db)
        created = service.create(shopping_cart_data)
        
        # 执行查询
        found_shopping_cart = service.get_by_id(created.id)
        
        # 验证结果
        assert found_shopping_cart is not None
        assert found_shopping_cart.id == created.id
        
    def test_get_shopping_cart_by_id_not_exists(self, unit_test_db: Session):
        """测试按ID查询shopping_cart - 不存在"""
        service = Shopping_CartService(unit_test_db)
        
        # 查询不存在的ID
        result = service.get_by_id(99999)
        
        # 验证返回None
        assert result is None
        
    def test_update_shopping_cart_success(self, unit_test_db: Session):
        """测试更新shopping_cart - 成功"""
        # 创建测试数据
        service = Shopping_CartService(unit_test_db)
        created = service.create(self.test_data)
        
        # 准备更新数据
        update_data = {"status": "updated"}
        
        # 执行更新
        updated = service.update(created.id, update_data)
        
        # 验证更新结果
        assert updated is not None
        assert updated.status == "updated"
        assert hasattr(updated, 'updated_at')
        
    def test_delete_shopping_cart_success(self, unit_test_db: Session):
        """测试删除shopping_cart - 成功"""
        # 创建测试数据
        service = Shopping_CartService(unit_test_db)
        created = service.create(self.test_data)
        
        # 执行删除
        result = service.delete(created.id)
        
        # 验证删除结果
        assert result is True
        
        # 验证数据库中已删除
        deleted = service.get_by_id(created.id)
        assert deleted is None
