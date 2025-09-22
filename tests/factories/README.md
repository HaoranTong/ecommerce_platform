# 测试数据工厂目录

## 📋 目录说明

本目录包含统一的测试数据工厂，用于生成各种测试实体和测试场景数据。采用Factory Boy模式，确保测试数据的一致性和可维护性。

## 📁 文件结构

```
factories/
├── README.md              # 本说明文档
└── test_data_factory.py   # 统一测试数据工厂
```

## 🎯 主要功能

### 核心数据工厂
- **用户数据工厂**: 生成测试用户、角色和权限数据
- **商品数据工厂**: 生成测试分类、品牌、商品和SKU数据
- **库存数据工厂**: 生成库存、预占和事务测试数据
- **购物车数据工厂**: 生成购物车和购物车项目数据
- **订单数据工厂**: 生成测试订单和订单项数据
- **统一配置**: 数据库会话管理和Factory Boy配置

## 🛠️ 使用方法

详细的使用方法和代码示例请参考：
- **[测试数据工厂使用手册](../../docs/tools/test-factory-usage-guide.md)** - 完整使用指南和代码示例

### 快速开始
```python
from tests.factories.test_data_factory import StandardTestDataFactory

# 创建完整数据链
user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(db)
```

## 📚 相关文档

- **[测试标准文档](../../docs/standards/testing-standards.md)** - Factory Boy使用规范
- **[测试使用指南](../../docs/tools/testing-tools.md)** - 数据工厂配置说明
- **[测试数据工厂使用手册](../../docs/tools/test-factory-usage-guide.md)** - 详细使用指南