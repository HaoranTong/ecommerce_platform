# Pydantic V2 标准规范和最佳实践

## 🎯 问题背景

项目中反复出现Pydantic V1语法导致的测试失败，需要建立统一的Pydantic V2标准。

## 🔧 Pydantic V2 关键变化

### 1. 配置方式变更
```python
# ❌ Pydantic V1 (弃用)
class MyModel(BaseModel):
    class Config:
        from_attributes = True
        
# ✅ Pydantic V2 (标准)
class MyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

### 2. 验证器语法变更
```python
# ❌ Pydantic V1 (弃用)
@validator('field_name')
def validate_field(cls, v):
    return v
    
# ✅ Pydantic V2 (标准) 
@field_validator('field_name')
@classmethod
def validate_field(cls, v: str) -> str:
    return v
```

### 3. 根验证器变更
```python
# ❌ Pydantic V1 (弃用)
@root_validator(pre=True)
def validate_all(cls, values):
    return values
    
# ✅ Pydantic V2 (标准)
@model_validator(mode='before')
@classmethod  
def validate_all(cls, data: Any) -> Any:
    return data
```

### 4. 类型验证严格化
```python
# ❌ 问题：类型不匹配会直接失败
sku_id: int  # 传入 "TEST-SKU" 会失败

# ✅ 解决方案1：使用Union类型
sku_id: Union[int, str]

# ✅ 解决方案2：使用自定义验证器转换
@field_validator('sku_id', mode='before')
@classmethod
def validate_sku_id(cls, v):
    if isinstance(v, str):
        # 测试环境允许字符串SKU
        if v.startswith('TEST-') or v.startswith('SKU-'):
            return hash(v) % 1000000  # 转换为数字
    return v
```

## 🧪 测试中的数据类型统一

### 标准测试数据模式
```python
# ✅ 推荐：使用数值型SKU ID
VALID_SKU_ID = 1001
TEST_SKU_IDS = [1001, 1002, 1003]

# ✅ 测试用Mock对象标准写法
mock_inventory = Mock()
mock_inventory.id = 1
mock_inventory.sku_id = 1001  # 数值型
mock_inventory.available_quantity = 100
mock_inventory.reserved_quantity = 0
mock_inventory.warning_threshold = 10
mock_inventory.critical_threshold = 5
mock_inventory.is_low_stock = False
mock_inventory.is_critical_stock = False
mock_inventory.is_out_of_stock = False
mock_inventory.is_active = True
mock_inventory.updated_at = datetime.now()
```

## 📋 强制性修复清单

### 1. Schema文件检查点
- [ ] 所有`class Config:`改为`model_config = ConfigDict()`
- [ ] 所有`@validator`改为`@field_validator`  
- [ ] 所有`@root_validator`改为`@model_validator`
- [ ] 检查类型定义与数据库模型一致性

### 2. 测试文件检查点  
- [ ] Mock对象属性类型与Schema一致
- [ ] 测试数据使用正确的数据类型
- [ ] 避免使用字符串类型的数值字段

### 3. Service文件检查点
- [ ] `model_validate`调用前确保数据类型正确
- [ ] 数据库查询结果与Schema类型匹配

## 🚀 自动化修复脚本

```python
# scripts/fix_pydantic_v2.py
import re
import os

def fix_config_syntax(content):
    """修复Config语法"""
    # 查找并替换Config类
    pattern = r'class Config:\s*\n\s*from_attributes\s*=\s*True'
    replacement = 'model_config = ConfigDict(from_attributes=True)'
    return re.sub(pattern, replacement, content)

def fix_validator_syntax(content):
    """修复validator语法"""
    # @validator -> @field_validator
    content = re.sub(r'@validator\(', '@field_validator(', content)
    return content
```

## 📝 提交前检查表

每次提交前必须检查：
- [ ] 运行 `python scripts/fix_pydantic_v2.py` 
- [ ] 执行 `pytest tests/unit/test_services/ -v` 确保无类型错误
- [ ] 确认所有Mock对象使用正确数据类型
- [ ] 验证Schema定义与模型字段类型一致

**强制要求：任何Pydantic相关修改必须同时更新此文档并在团队内同步。**