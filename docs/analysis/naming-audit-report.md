# 现有代码命名规范审计报告 (历史文档)

> ⚠️ **注意**：此文档反映的是2025-09-11时的项目状态，当时采用的是app/api/*_routes.py架构。
> 项目现已迁移到模块化单体架构(app/modules/*/router.py)，此报告仅作为历史记录保存。
> 当前架构请参考：[架构总览](../architecture/overview.md)

## 📋 审计概述

**审计日期**: 2025-09-11  
**审计范围**: 全代码仓库命名规范符合性 (历史状态)  
**审计标准**: [命名规范总纲](../standards/naming-conventions-standards.md)  
**架构状态**: app/api/ 路由架构 (已废弃)

## 🗄️ 数据库层命名审计 (历史架构)

> 以下审计结果基于2025-09-11的项目状态，当前数据库架构已迁移到app/shared/models.py统一管理。

### ✅ 符合规范的命名

#### 表命名 (✅ 优秀)
```python
# models.py - 表命名完全符合规范
users           # user模块 + 复数形式  
categories      # category模块 + 复数形式
products        # product模块 + 复数形式  
orders          # order模块 + 复数形式
order_items     # order_item复合名称 + 复数形式
```

#### 字段命名 (✅ 优秀)
```python
# 主键字段 - 统一使用 id
id = Column(Integer, primary_key=True, index=True)

# 外键字段 - 统一使用 {表名单数}_id 模式
user_id = Column(Integer, ForeignKey('users.id'))
category_id = Column(Integer, ForeignKey('categories.id'))  
product_id = Column(Integer, ForeignKey('products.id'))

# 时间字段 - 统一使用 {动作}_at 模式
created_at = Column(DateTime, server_default=func.now())
updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# 布尔字段 - 统一使用 is_{状态} 模式
is_active = Column(Boolean, default=True)

# 数量字段 - 统一使用 {名称}_quantity 模式  
stock_quantity = Column(Integer, nullable=False, default=0)

# 金额字段 - 使用清晰的语义命名
subtotal = Column(DECIMAL(10, 2), nullable=False, default=0.00)
shipping_fee = Column(DECIMAL(10, 2), nullable=False, default=0.00)
discount_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)
```

#### JSON字段命名 (✅ 良好)
```python
# JSON存储字段 - 语义清晰
attributes = Column(Text, nullable=True)  # 商品属性JSON
images = Column(Text, nullable=True)      # 图片URL数组JSON
```

### 📊 数据库命名合规率: 95% (优秀)

## 🌐 API层命名审计

### ✅ 符合规范的API端点

#### 用户认证API (✅ 优秀)
```python
# user_routes.py - 完全符合认证API规范
POST /auth/register         # 用户注册
POST /auth/login           # 用户登录  
POST /auth/refresh         # 刷新令牌
GET  /auth/me             # 获取当前用户
PUT  /auth/me             # 更新当前用户
POST /auth/logout         # 用户登出
POST /auth/change-password # 修改密码
GET  /auth/users          # 用户列表 (管理员)
GET  /auth/users/{user_id} # 用户详情 (管理员)
```

### ⚠️ 需要规范化的API端点

#### 购物车API (⚠️ 部分不规范)
```python
# cart_routes.py - 需要调整为RESTful风格
❌ POST /cart/add          → ✅ POST /cart/items
❌ PUT /cart/update        → ✅ PUT /cart/items/{item_id}  
❌ DELETE /cart/remove     → ✅ DELETE /cart/items/{item_id}
✅ GET /cart              → ✅ GET /cart (符合规范)
✅ DELETE /cart/clear     → ✅ DELETE /cart (符合规范)
```

#### 商品API (⚠️ 部分不规范)  
```python
# product_routes.py - 基本符合但需要优化
✅ POST /products         → ✅ POST /products
✅ GET /products          → ✅ GET /products  
✅ GET /products/{id}     → ✅ GET /products/{product_id}  (参数名优化)
✅ PUT /products/{id}     → ✅ PUT /products/{product_id}   (参数名优化)
✅ DELETE /products/{id}  → ✅ DELETE /products/{product_id} (参数名优化)
```

### 📊 API命名合规率: 75% (需要改进)

## 🔧 代码文件命名审计

### ✅ 符合规范的文件命名

#### 应用核心文件 (✅ 优秀)
```
app/
├── main.py              # ✅ 应用入口，符合惯例
├── models.py            # ✅ 统一模型文件，符合规范  
├── database.py          # ✅ 数据库配置，语义清晰
├── redis_client.py      # ✅ Redis客户端，语义清晰
├── auth.py              # ✅ 认证功能，语义清晰
└── api/
    ├── routes.py        # ✅ 主路由文件，符合规范
    ├── schemas.py       # ✅ 统一Schema文件，符合规范
    ├── user_routes.py   # ✅ 用户路由，符合 {module}_routes.py
    ├── cart_routes.py   # ✅ 购物车路由，符合规范
    ├── product_routes.py # ✅ 商品路由，符合规范
    ├── order_routes.py  # ✅ 订单路由，符合规范
    └── category_routes.py # ✅ 分类路由，符合规范
```

### 📊 代码文件命名合规率: 100% (优秀)

## 📚 文档结构命名审计

### ❌ 存在严重不规范问题

#### 文档目录命名冲突
```
❌ 重复和冲突的目录结构 (历史状态，已解决):
docs/api/modules/          # API规范文档目录 (已废弃)
docs/modules/api/          # API路由文档目录 (已废弃)

❌ 模块命名不一致 (历史状态，已解决):
docs/modules/shopping-cart/     vs    app/modules/shopping_cart/
docs/modules/user-auth/         vs    app/modules/user_auth/
docs/modules/product-catalog/   vs    app/modules/product_catalog/
docs/modules/order-management/  vs    app/modules/order_management/

✅ 当前架构已统一为模块化单体架构，详见: [架构总览](../architecture/overview.md)
```

#### 文档内容重复  
```
❌ 重复的API文档:
docs/api/modules/cart/api-spec.md          (379行)
docs/modules/api/cart-routes/overview.md   (763行)
```

### 📊 文档命名合规率: 40% (急需改进)

## 🔧 函数和类命名审计

### ✅ 符合规范的命名

#### API路由函数 (✅ 良好)
```python
# user_routes.py - 函数命名基本符合规范
async def register_user(...)        # 注册用户
async def login_user(...)           # 用户登录
async def refresh_token(...)        # 刷新令牌  
async def get_current_user_info(...) # 获取当前用户信息
async def update_current_user(...)   # 更新当前用户
async def change_password(...)       # 修改密码
async def logout_user(...)          # 用户登出
```

#### Schema类命名 (✅ 优秀)
```python
# schemas.py - 类命名完全符合规范
class UserRegister(BaseModel):      # 用户注册Schema
class UserLogin(BaseModel):         # 用户登录Schema
class UserUpdate(BaseModel):        # 用户更新Schema
class UserRead(BaseModel):          # 用户读取Schema
class ProductCreate(BaseModel):     # 商品创建Schema
class ProductUpdate(BaseModel):     # 商品更新Schema
class ProductRead(BaseModel):       # 商品读取Schema
```

### ⚠️ 需要优化的命名

#### 部分函数命名可以更规范
```python
# 当前命名 → 建议命名
get_current_user_info() → get_current_user()  # 简化函数名
list_users()           → get_users()          # 统一动词使用
```

### 📊 函数/类命名合规率: 85% (良好)

## 📊 总体命名合规性评估

| 层级 | 合规率 | 评级 | 主要问题 |
|------|--------|------|----------|
| 数据库 | 95% | 优秀 | 基本无问题 |
| API路由 | 75% | 良好 | 购物车API需要RESTful化 |
| 代码文件 | 100% | 优秀 | 完全符合规范 |
| 函数/类 | 85% | 良好 | 个别函数名可优化 |
| 文档结构 | 40% | 差 | 存在重复和冲突 |

**整体合规率: 79% (良好，但需要改进)**

## 🚨 优先修复问题清单

### P0 (紧急) - 文档结构冲突
1. **删除重复API文档** - 按照MASTER.md流程执行
2. **统一模块命名** - 建立模块名称映射关系
3. **整合文档内容** - 避免信息重复记录

### P1 (重要) - API规范化  
1. **购物车API RESTful化** - 调整为标准REST端点
2. **商品API参数优化** - 统一使用{resource}_id命名
3. **建立API版本管理** - 为未来扩展做准备

### P2 (一般) - 细节优化
1. **函数命名优化** - 统一动词使用规范
2. **参数命名标准化** - 确保所有参数遵循规范
3. **注释和文档字符串** - 添加规范的代码注释

## 🔧 修复执行计划

### Phase 1: 建立标准 (✅ 已完成)
- [x] 创建命名规范总纲
- [x] 建立模块名称映射表
- [x] 制定检查机制

### Phase 2: 文档结构修复 (🔄 进行中)
- [ ] 删除重复文档，按照MASTER.md流程
- [ ] 统一模块目录命名
- [ ] 建立正确的引用关系

### Phase 3: API规范化 (⏳ 待开始)
- [ ] 重构购物车API为RESTful风格
- [ ] 统一所有API参数命名
- [ ] 更新API文档

### Phase 4: 代码细节优化 (⏳ 待开始)  
- [ ] 优化函数命名
- [ ] 标准化参数命名
- [ ] 完善代码注释

### Phase 5: 自动化检查 (⏳ 待开始)
- [ ] 开发命名规范检查脚本
- [ ] 集成到CI/CD流程
- [ ] 建立持续监控机制

## 📈 成功标准

修复完成后应达到:
- **数据库命名**: 100% 合规
- **API命名**: 95% 合规  
- **代码文件命名**: 100% 合规
- **函数/类命名**: 95% 合规
- **文档结构**: 95% 合规
- **整体合规率**: 95% 以上

---

**下一步**: 等待确认后开始执行Phase 2文档结构修复计划
