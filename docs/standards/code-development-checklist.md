# 代码开发强制检查清单

## 🚨 强制执行原则

**任何代码编写前必须完成对应的标准检查，违反此原则立即停止操作！**

## 📋 代码文件创建检查清单

### 创建Python文件前必须检查 ✅

#### IF create_file *.py THEN 强制执行以下检查：

1. **🔍 文件命名检查**
   - ✅ `read_file docs/standards/naming-conventions.md 35 60` (文件命名规则)
   - ✅ `read_file docs/standards/code-standards.md 30 50` (模块文件命名)
   - ✅ 确认文件名符合：`{module}_{type}.py` 格式

2. **🏗️ 目录结构检查**
   - ✅ `read_file docs/standards/code-standards.md 10 35` (项目结构标准)
   - ✅ 确认文件位置符合标准目录结构
   - ✅ 确认不违反模块划分原则

3. **📝 功能定位检查**
   - ✅ `read_file docs/standards/document-standards.md` (相关模块)
   - ✅ 确认功能不重复现有文件
   - ✅ 确认符合单一职责原则

## 📊 数据库相关代码检查清单

### 创建/修改数据库模型前必须检查 ✅

#### IF 涉及数据库操作 THEN 强制执行：

1. **🗄️ 表名字段名检查**
   - ✅ `read_file docs/standards/database-standards.md 10 30` (表命名规范)
   - ✅ `read_file docs/standards/database-standards.md 35 65` (字段命名规范)
   - ✅ `read_file docs/standards/naming-conventions.md 70 100` (数据库命名)

2. **🔗 关系设计检查**
   - ✅ `read_file docs/standards/database-standards.md 80 116` (关系和约束)
   - ✅ 确认外键命名：`{表名}_id`
   - ✅ 确认时间戳字段：`created_at`, `updated_at`

## 🌐 API开发检查清单

### 创建API路由前必须检查 ✅

#### IF create_file *_routes.py OR 添加API端点 THEN 强制执行：

1. **🛣️ API路径检查**
   - ✅ `read_file docs/standards/api-standards.md 45 80` (URL设计规范)
   - ✅ `read_file docs/standards/naming-conventions.md 105 130` (API命名规范)
   - ✅ 确认RESTful风格：复数资源名

2. **📝 API设计检查**
   - ✅ `read_file docs/standards/api-standards.md 1 45` (设计原则)
   - ✅ `read_file docs/standards/api-standards.md 160 200` (响应格式)
   - ✅ 确认HTTP状态码使用规范

3. **🔐 安全性检查**
   - ✅ `read_file docs/standards/api-standards.md 250 290` (认证授权)
   - ✅ 确认输入验证和权限控制

## 🧪 测试文件检查清单

### 创建测试文件前必须检查 ✅

#### IF create_file test_*.py THEN 强制执行：

1. **📁 测试组织检查**
   - ✅ `read_file docs/standards/testing-standards.md 40 80` (测试文件组织)
   - ✅ `read_file docs/standards/testing-standards.md 90 120` (测试命名规范)
   - ✅ 确认测试文件位置和命名正确

2. **🎯 测试策略检查**
   - ✅ `read_file docs/standards/testing-standards.md 150 200` (测试示例)
   - ✅ 确认测试覆盖关键场景
   - ✅ 确认测试函数命名：`test_{功能}_{场景}`

## 🔤 命名操作检查清单

### 任何命名操作前必须检查 ✅

#### IF 创建类/函数/变量名称 THEN 强制执行：

1. **📛 命名规范检查**
   - ✅ `read_file docs/standards/naming-conventions.md 180 220` (代码命名规范)
   - ✅ `read_file docs/standards/code-standards.md 50 80` (类和函数命名)
   - ✅ 确认命名风格一致性

2. **🎯 命名语义检查**
   - ✅ 确认名称自解释，避免缩写
   - ✅ 确认符合模块命名约定
   - ✅ 确认与现有命名一致

## ⚡ 强制执行流程

### 执行顺序（严格遵守）：
1. **📋 检查清单确认** - 识别需要执行的检查项
2. **📖 标准文档阅读** - 逐项read_file相关规范
3. **✅ 规范符合确认** - 明确说明遵循的具体规则
4. **🚫 开始代码编写** - 只有在完成所有检查后才能开始

### 违规处理：
- 发现未按清单检查 → 立即停止操作
- 发现违反标准 → 重新设计符合规范
- 养成习惯性直接编码 → 强制重新阅读本清单

## 📝 检查记录模板

每次检查必须记录：
```
🔍 检查点触发：{具体操作，如：创建user_routes.py}
📋 执行的检查项：
  - ✅ 文件命名检查 - 遵循{具体规则}
  - ✅ API路径检查 - 遵循{具体规则}  
  - ✅ 安全性检查 - 遵循{具体规则}
✅ 验证确认：所有检查通过，符合标准
🚫 执行操作：开始编写代码
```