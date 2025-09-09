# 数据模型规范

## 📊 全局数据模型架构

### 设计原则
1. **统一性**: 所有模块使用统一的字段命名和数据类型
2. **可扩展性**: 预留扩展字段，支持业务发展
3. **版本化**: 数据模型支持版本管理和迁移
4. **配置驱动**: 字段定义通过配置文件统一管理

## 🏗️ 核心实体模型

### 用户模型 (User)
```python
# 配置文件: config/models/user.yaml
user:
  table_name: "users"
  fields:
    id:
      type: "UUID"
      primary_key: true
      description: "用户唯一标识"
    username:
      type: "VARCHAR(50)"
      unique: true
      required: true
      description: "用户名"
    email:
      type: "VARCHAR(200)"
      unique: true
      required: true
      description: "邮箱地址"
    password_hash:
      type: "VARCHAR(255)"
      required: true
      description: "密码哈希"
    phone:
      type: "VARCHAR(20)"
      description: "手机号码"
    real_name:
      type: "VARCHAR(100)"
      description: "真实姓名"
    status:
      type: "ENUM"
      values: ["active", "inactive", "suspended"]
      default: "active"
      description: "用户状态"
    created_at:
      type: "TIMESTAMP"
      default: "CURRENT_TIMESTAMP"
    updated_at:
      type: "TIMESTAMP"
      default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
```

### 商品模型 (Product)
```python
# 配置文件: config/models/product.yaml
product:
  table_name: "products"
  fields:
    id:
      type: "INTEGER"
      primary_key: true
      auto_increment: true
    name:
      type: "VARCHAR(200)"
      required: true
      description: "商品名称"
    sku:
      type: "VARCHAR(100)"
      unique: true
      required: true
      description: "商品SKU编码"
    description:
      type: "TEXT"
      description: "商品描述"
    category_id:
      type: "INTEGER"
      foreign_key: "categories.id"
      description: "分类ID"
    price:
      type: "DECIMAL(10,2)"
      required: true
      min_value: 0
      description: "商品价格"
    stock_quantity:
      type: "INTEGER"
      required: true
      min_value: 0
      description: "库存数量"
    status:
      type: "ENUM"
      values: ["active", "inactive", "out_of_stock"]
      default: "active"
      description: "商品状态"
    image_url:
      type: "VARCHAR(500)"
      description: "主图URL"
    attributes:
      type: "JSON"
      description: "商品属性(JSON格式)"
    created_at:
      type: "TIMESTAMP"
      default: "CURRENT_TIMESTAMP"
    updated_at:
      type: "TIMESTAMP"
      default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
```

### 订单模型 (Order)
```python
# 配置文件: config/models/order.yaml
order:
  table_name: "orders"
  fields:
    id:
      type: "INTEGER"
      primary_key: true
      auto_increment: true
    order_no:
      type: "VARCHAR(32)"
      unique: true
      required: true
      description: "订单号"
    user_id:
      type: "UUID"
      foreign_key: "users.id"
      required: true
      description: "用户ID"
    status:
      type: "ENUM"
      values: ["pending", "paid", "shipped", "delivered", "cancelled"]
      default: "pending"
      description: "订单状态"
    total_amount:
      type: "DECIMAL(10,2)"
      required: true
      min_value: 0
      description: "订单总金额"
    shipping_fee:
      type: "DECIMAL(10,2)"
      default: 0
      description: "运费"
    discount_amount:
      type: "DECIMAL(10,2)"
      default: 0
      description: "优惠金额"
    payment_method:
      type: "VARCHAR(50)"
      description: "支付方式"
    shipping_address:
      type: "JSON"
      description: "收货地址(JSON格式)"
    remark:
      type: "TEXT"
      description: "订单备注"
    created_at:
      type: "TIMESTAMP"
      default: "CURRENT_TIMESTAMP"
    updated_at:
      type: "TIMESTAMP"
      default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
    paid_at:
      type: "TIMESTAMP"
      description: "支付时间"
    shipped_at:
      type: "TIMESTAMP"
      description: "发货时间"
    delivered_at:
      type: "TIMESTAMP"
      description: "收货时间"
```

## 🔄 状态机定义

### 订单状态机
```yaml
# 配置文件: config/state_machines/order.yaml
order_states:
  initial: "pending"
  states:
    pending:
      description: "待付款"
      allowed_transitions: ["paid", "cancelled"]
      timeout: 1800  # 30分钟自动取消
    paid:
      description: "已付款"
      allowed_transitions: ["shipped", "cancelled"]
    shipped:
      description: "已发货"
      allowed_transitions: ["delivered"]
    delivered:
      description: "已完成"
      allowed_transitions: []  # 终态
    cancelled:
      description: "已取消"
      allowed_transitions: []  # 终态
```

### 用户状态机
```yaml
# 配置文件: config/state_machines/user.yaml
user_states:
  initial: "active"
  states:
    active:
      description: "正常状态"
      allowed_transitions: ["inactive", "suspended"]
    inactive:
      description: "未激活"
      allowed_transitions: ["active"]
    suspended:
      description: "已暂停"
      allowed_transitions: ["active"]
```

## 📏 字段命名规范

### 主键字段
- **统一命名**: `id`
- **数据类型**: `INTEGER AUTO_INCREMENT` 或 `UUID`
- **索引**: 自动创建主键索引

### 外键字段
- **命名规范**: `{关联表单数}_id`
- **示例**: `user_id`, `category_id`, `product_id`
- **约束**: 必须定义外键约束和级联规则

### 时间字段
- **创建时间**: `created_at` (TIMESTAMP)
- **更新时间**: `updated_at` (TIMESTAMP)
- **业务时间**: `{业务}_at` (如 `paid_at`, `shipped_at`)

### 状态字段
- **统一命名**: `status`
- **数据类型**: `ENUM` 或 `VARCHAR`
- **默认值**: 必须定义默认状态

### 金额字段
- **数据类型**: `DECIMAL(10,2)`
- **命名规范**: `{用途}_amount` 或 `{用途}_fee`
- **约束**: 非负数检查

### 数量字段
- **数据类型**: `INTEGER`
- **命名规范**: `{用途}_quantity` 或 `{用途}_count`
- **约束**: 非负数检查

## 🔧 配置驱动实现

### 模型配置加载器
```python
# app/core/model_config.py
import yaml
from pathlib import Path
from typing import Dict, Any

class ModelConfigLoader:
    def __init__(self, config_dir: str = "config/models"):
        self.config_dir = Path(config_dir)
        self._configs = {}
    
    def load_model_config(self, model_name: str) -> Dict[str, Any]:
        """加载模型配置"""
        if model_name not in self._configs:
            config_file = self.config_dir / f"{model_name}.yaml"
            with open(config_file, 'r', encoding='utf-8') as f:
                self._configs[model_name] = yaml.safe_load(f)
        return self._configs[model_name]
    
    def get_field_config(self, model_name: str, field_name: str) -> Dict[str, Any]:
        """获取字段配置"""
        model_config = self.load_model_config(model_name)
        return model_config[model_name]["fields"][field_name]
```

### 动态模型生成器
```python
# app/core/model_generator.py
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base

class DynamicModelGenerator:
    TYPE_MAPPING = {
        "INTEGER": Integer,
        "VARCHAR": String,
        "TEXT": Text,
        "DECIMAL": DECIMAL,
        "TIMESTAMP": DateTime,
        "BOOLEAN": Boolean,
        "ENUM": Enum,
        "JSON": Text  # MySQL JSON存储为Text
    }
    
    def generate_model(self, model_name: str, config: Dict[str, Any]):
        """根据配置生成SQLAlchemy模型"""
        attrs = {}
        table_config = config[model_name]
        
        for field_name, field_config in table_config["fields"].items():
            column_type = self._get_column_type(field_config)
            column_kwargs = self._get_column_kwargs(field_config)
            attrs[field_name] = Column(column_type, **column_kwargs)
        
        attrs["__tablename__"] = table_config["table_name"]
        
        return type(model_name.title(), (Base,), attrs)
```

### API字段验证器
```python
# app/core/validators.py
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Type

class ConfigDrivenValidator:
    def __init__(self, config_loader: ModelConfigLoader):
        self.config_loader = config_loader
    
    def create_pydantic_model(self, model_name: str, operation: str = "create") -> Type[BaseModel]:
        """根据配置创建Pydantic验证模型"""
        config = self.config_loader.load_model_config(model_name)
        fields = {}
        
        for field_name, field_config in config[model_name]["fields"].items():
            if self._should_include_field(field_config, operation):
                field_type = self._get_pydantic_type(field_config)
                field_constraints = self._get_field_constraints(field_config)
                fields[field_name] = (field_type, Field(**field_constraints))
        
        return type(f"{model_name.title()}{operation.title()}", (BaseModel,), fields)
```

## 📖 使用示例

### 在模型定义中使用
```python
# app/models.py
from app.core.model_config import ModelConfigLoader
from app.core.model_generator import DynamicModelGenerator

config_loader = ModelConfigLoader()
model_generator = DynamicModelGenerator()

# 动态生成User模型
user_config = config_loader.load_model_config("user")
User = model_generator.generate_model("user", user_config)

# 动态生成Product模型
product_config = config_loader.load_model_config("product")
Product = model_generator.generate_model("product", product_config)
```

### 在API中使用
```python
# app/api/schemas.py
from app.core.validators import ConfigDrivenValidator

validator = ConfigDrivenValidator(config_loader)

# 动态生成Pydantic模型
UserCreate = validator.create_pydantic_model("user", "create")
UserRead = validator.create_pydantic_model("user", "read")
UserUpdate = validator.create_pydantic_model("user", "update")

ProductCreate = validator.create_pydantic_model("product", "create")
ProductRead = validator.create_pydantic_model("product", "read")
```

## 🎯 优势总结

1. **统一性**: 所有字段定义在配置文件中，确保一致性
2. **可维护性**: 修改字段只需更新配置文件
3. **可扩展性**: 新增模型和字段无需修改代码
4. **版本化**: 配置文件可以版本管理
5. **自动化**: 自动生成SQL、模型和验证器
6. **类型安全**: 配置错误在启动时即可发现
