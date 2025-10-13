# 测试标准更新日志

**日期**: 2025-10-13  
**版本**: v2.0.0 → v2.1.0  
**更新原因**: 澄清容易引起误解的表述，增加快速参考指南

## 主要变更

### 1. 新增"快速参考"章节（文档头部）

**位置**: 文档开头，核心测试原则之前

**目的**: 
- 为AI助手提供清晰、直接的Repository层测试策略总结
- 避免每次查找标准时遗漏关键信息
- 减少理解错误和重复犯错

**内容包括**:
- 策略总览表（create测试 vs 其他测试）
- 核心概念澄清（被测实体 vs 依赖实体）
- 3个完整示例：
  - 示例1: CartItem创建测试（含跨模块外键依赖）
  - 示例2: Repository其他测试（查询/更新/删除）
  - 示例3: UserRole测试（标准证明）
- 关键要点总结（4个✅要点 + 4个❌常见错误）

**关键改进**:
- ✅ 明确"依赖实体始终使用Factory Boy"（无论create测试还是其他测试）
- ✅ 明确"最小必填字段构造"只适用于被测实体的create测试
- ✅ 提供跨模块外键依赖的典型示例（CartItem→Cart/Product）
- ✅ 纠正"手动创建"的误解

### 2. 术语标准化

**变更前**: "最小实体构造"、"手动创建最小实体"  
**变更后**: "最小必填字段构造"

**原因**:
- "手动"两个字容易引起误解（以为要手动写字段值）
- 实际上是"让ORM自动应用默认值"，不是"手动指定所有值"
- "最小必填字段"更准确描述实际操作（只填nullable=False且无default的字段）

### 3. 增强Repository层测试说明

**位置**: "2. Repository层测试 (test_repositories/)" 章节

**变更内容**:
- 2.1 创建操作测试: "最小必填字段创建" → "最小必填字段构造：被测实体只填必填字段，依赖实体使用Factory Boy"
- 数据准备原则: 新增完整的CartItem示例（含跨模块外键依赖）
- 代码示例扩展为4个：
  - 示例1: CartItem创建（跨模块依赖）
  - 示例2: User创建（无外键依赖）
  - 示例3: 查询测试
  - 示例4: 更新测试

### 4. 完善数据准备策略说明

**位置**: "双工厂架构测试数据策略" 章节

**策略1改进**:
- 标题: "最小实体构造" → "最小必填字段构造"
- 新增"适用对象"说明：
  - ✅ 被测实体（Entity Under Test）
  - ❌ 依赖实体（Dependency Entity - 始终使用Factory Boy）
- 新增"关键概念"解释
- 示例改为CartItem（更典型，有跨模块依赖）

**策略2改进**:
- 新增"说明"：所有实体（被测实体和依赖实体）都使用Factory Boy
- 新增CartItem更新测试示例

**数据准备策略总结表改进**:
- 4列 → 5列（增加"依赖实体"列）
- Repository创建测试: 明确区分被测实体和依赖实体的不同策略
- 示例更新为CartItem（更典型）

### 5. 工厂架构概览表改进

**Factory Boy工厂行**:
- "何时使用"从"Repository非创建测试<br/>Standalone完整流程"
- 改为"1. Repository非创建测试<br/>2. Repository创建测试的依赖实体<br/>3. Standalone完整流程"

**最小实体构造行**:
- "何时使用"从"Repository的create测试"
- 改为"仅用于被测实体（Entity Under Test）"

## 新增典型示例

### CartItem创建测试（跨模块外键依赖）

```python
def test_create_cart_item_minimal(unit_test_db):
    """测试创建购物车项 - 最小必填字段
    
    被测实体：CartItem
    依赖实体：Cart (同模块), Product (跨模块-产品目录模块)
    """
    # 1. 准备依赖实体 - 使用Factory Boy
    CartFactory._meta.sqlalchemy_session = unit_test_db
    cart = CartFactory.create()
    
    ProductFactory._meta.sqlalchemy_session = unit_test_db
    product = ProductFactory.create()
    
    # 2. 构造被测实体 - 只填必填字段
    cart_item = CartItem(
        cart_id=cart.id,
        sku_id=product.id,
        quantity=1,
        unit_price=Decimal("10.00")
        # 不填写有默认值的字段
    )
    
    result = CartItemRepository.create(unit_test_db, cart_item)
    
    # 3. 验证必填字段
    assert result.id is not None
    assert result.cart_id == cart.id
    
    # 4. 验证默认值是否正确应用
    assert result.created_at is not None
    assert result.updated_at is not None
```

## 为什么这些改进很重要

### 问题1: User模块示例不够典型
**旧标准**: 只用User/Role/Permission作为示例  
**问题**: User模块没有跨模块外键依赖  
**新增**: CartItem示例（依赖Cart同模块 + Product跨模块）  
**效果**: AI助手能正确理解跨模块依赖场景

### 问题2: "手动创建"容易误解
**旧表述**: "手动创建最小实体"  
**误解**: 以为要手动写具体字段值  
**新表述**: "最小必填字段构造"  
**效果**: 明确只是"选择哪些字段填写"，值还是自动生成

### 问题3: 依赖实体策略不清晰
**旧标准**: 没有明确说明依赖实体如何创建  
**误解**: AI以为依赖实体也要"最小实体构造"  
**新增**: 明确"依赖实体始终使用Factory Boy"  
**效果**: 避免错误地尝试手动创建依赖实体

### 问题4: 策略分散难以查找
**旧结构**: 策略散落在多个章节  
**问题**: AI每次都要搜索多个位置  
**新增**: 文档头部"快速参考"章节  
**效果**: 一次查找获得所有核心信息

## 关键要点强化

### ✅ 正确理解

1. **依赖实体始终使用Factory Boy**
   - 无论是create测试还是其他测试
   - 无论是同模块依赖还是跨模块依赖

2. **被测实体在create测试中使用最小必填字段构造**
   - 目的：验证默认值是否正确应用
   - 只填`nullable=False`且无`default`的字段

3. **被测实体在其他测试中使用Factory Boy**
   - 查询、更新、删除测试不关注默认值

### ❌ 常见错误

1. ❌ "最小必填字段构造"适用于所有实体
   - ✅ 只适用于被测实体的create测试

2. ❌ 依赖实体也要用最小构造
   - ✅ 依赖实体始终用Factory Boy

3. ❌ 手动构造依赖实体
   - ✅ 永远不要手动构造，用Factory

4. ❌ create测试中所有实体都不用Factory
   - ✅ 只有被测实体不用Factory，依赖实体要用Factory

## 后续建议

1. **测试生成器改进**: 
   - `_generate_minimal_entity_creation`方法需要按新标准修正
   - 依赖实体改用Factory Boy，不再手动构造

2. **文档维护**:
   - 保持"快速参考"章节与详细章节同步
   - 新增典型场景时优先考虑跨模块依赖示例

3. **AI助手使用**:
   - 优先查阅"快速参考"章节
   - 遇到不确定的场景参考完整示例
   - 避免猜测，按标准执行

## 影响范围

- ✅ 测试标准文档更新
- ⚠️ 测试生成器代码需要相应调整
- ⚠️ 已生成的测试代码可能需要重新生成

## 检查清单

使用新标准前请确认：
- [ ] 理解"被测实体"和"依赖实体"的区别
- [ ] 理解"最小必填字段构造"的适用范围
- [ ] 理解依赖实体始终使用Factory Boy
- [ ] 查看CartItem示例理解跨模块依赖场景
- [ ] 不再使用"手动创建"这个表述
