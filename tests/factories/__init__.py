"""
测试数据工厂模块初始化

统一导入所有Factory类和管理器，提供标准化访问接口
符合[CHECK:TEST-002]测试数据工厂标准
"""

# 从data_factory导入通用工厂
from .data_factory import StandardTestDataFactory

# 从user_auth_factories导入特定工厂
from .user_auth_factories import (
    UserFactory, RoleFactory, PermissionFactory,
    SessionFactory, UserRoleFactory, RolePermissionFactory,
    UserAuthFactoryManager
)

# 从product_catalog_factories导入特定工厂（如果存在）
try:
    from .product_catalog_factories import (
        ProductFactory, CategoryFactory, BrandFactory, SKUFactory,
        ProductCatalogFactoryManager
    )
except ImportError:
    pass  # product_catalog模块尚未生成

# 从shopping_cart_factories导入特定工厂（如果存在）
try:
    from .shopping_cart_factories import (
        CartFactory, CartItemFactory,
        ShoppingCartFactoryManager
    )
except ImportError:
    pass  # shopping_cart模块尚未生成

# 从inventory_management_factories导入特定工厂（如果存在）
try:
    from .inventory_management_factories import (
        InventoryStockFactory, InventoryTransactionFactory, InventoryReservationFactory,
        InventoryManagementFactoryManager
    )
except ImportError:
    pass  # inventory_management模块尚未生成

# 为兼容性提供别名映射
TestDataFactory = StandardTestDataFactory  # 别名映射

# 导出所有工厂类
__all__ = [
    "StandardTestDataFactory",
    "TestDataFactory",  # 别名
    "UserFactory",
    "RoleFactory", 
    "PermissionFactory",
    "SessionFactory",
    "UserRoleFactory",
    "RolePermissionFactory",
    "UserAuthFactoryManager",
    "ProductFactory",
    "CategoryFactory",
    "BrandFactory",
    "SKUFactory",
    "ProductCatalogFactoryManager",
    "CartFactory",
    "CartItemFactory",
    "ShoppingCartFactoryManager",
    "InventoryStockFactory",
    "InventoryTransactionFactory",
    "InventoryReservationFactory",
    "InventoryManagementFactoryManager",
]
