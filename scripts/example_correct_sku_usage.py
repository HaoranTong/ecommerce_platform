"""
示例：正确使用sku_id的测试文件

❌ 错误用法：
    sku_id="SKU_001"  # 字符串类型，会导致外键错误
    
✅ 正确用法：
    sku_id=sku.id     # 整数类型，正确的外键引用
"""

import pytest
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator


class TestCorrectSkuIdUsage:
    """演示正确的sku_id使用方法"""
    
    def test_create_inventory_with_correct_sku_id(self, unit_test_db):
        """✅ 正确：使用整数sku_id"""
        # 创建完整的测试数据链
        user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(unit_test_db)
        
        # ✅ 正确：使用sku.id（整数）
        inventory = StandardTestDataFactory.create_inventory_stock(
            unit_test_db,
            sku_id=sku.id,  # 🔥 关键：使用sku.id而不是sku.sku_code
            available_quantity=100
        )
        
        assert inventory.sku_id == sku.id  # 整数比较
        assert isinstance(inventory.sku_id, int)
    
    def test_create_cart_item_with_correct_sku_id(self, unit_test_db):
        """✅ 正确：购物车项目使用整数sku_id"""
        user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(unit_test_db)
        
        # ✅ 正确：使用sku.id（整数）
        cart_item = StandardTestDataFactory.create_cart_item(
            unit_test_db,
            user_id=user.id,
            sku_id=sku.id,  # 🔥 关键：整数ID
            quantity=2
        )
        
        assert cart_item.sku_id == sku.id
        assert isinstance(cart_item.sku_id, int)
    
    def test_validation_prevents_string_sku_id(self, unit_test_db):
        """✅ 验证器防止字符串sku_id错误"""
        with pytest.raises(TypeError, match="sku_id必须是整数类型"):
            TestDataValidator.validate_sku_id("SKU_001")  # 字符串会抛出错误
        
        # 整数通过验证
        TestDataValidator.validate_sku_id(123)  # 不会抛出错误
