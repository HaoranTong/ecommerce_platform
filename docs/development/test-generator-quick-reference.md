# 智能测试生成工具 - 快速参考

## 🚀 快速开始

```bash
# 基础使用 - 生成完整测试套件
python scripts/generate_test_template.py user_auth --type all --validate

# 端到端验证 - 确保工具链完整可用
python scripts/e2e_test_verification.py
```

## 📋 命令参考

### 基本命令格式
```bash
python scripts/generate_test_template.py <module_name> [options]
```

### 参数选项

| 参数 | 说明 | 示例 |
|------|------|------|
| `module_name` | 要生成测试的模块名 | `user_auth`, `shopping_cart` |
| `--type` | 测试类型 | `all`, `unit`, `integration` |
| `--dry-run` | 预览模式，不写入文件 | `--dry-run` |
| `--validate` | 执行质量验证 | `--validate` (默认启用) |
| `--detailed` | 显示详细分析信息 | `--detailed` |

### 使用示例

```bash
# 1. 生成单元测试
python scripts/generate_test_template.py product_catalog --type unit

# 2. 预览生成结果
python scripts/generate_test_template.py inventory_management --dry-run

# 3. 详细分析模式
python scripts/generate_test_template.py order_management --detailed

# 4. 完整验证流程
python scripts/generate_test_template.py payment_service --type all --validate
```

## 📊 生成结果

### 文件结构
```
tests/
├── factories/
│   └── {module}_factories.py          # 智能数据工厂
├── unit/
│   ├── test_models/
│   │   └── test_{module}_models.py    # 模型测试
│   ├── test_services/
│   │   └── test_{module}_service.py   # 服务测试
│   └── test_{module}_workflow.py      # 业务流程测试
docs/
└── analysis/
    ├── {module}_test_validation_report_*.md  # 验证报告
    └── e2e_verification_report_*.md          # 端到端报告
```

### 生成统计 (以user_auth为例)
- **工厂类**: 6个Factory类，52个智能字段
- **测试方法**: 143个测试方法，2457行代码
- **覆盖范围**: 字段验证、约束测试、关系测试、业务逻辑

## ✅ 验证检查

### 质量验证项目
- ✅ **语法检查**: Python语法正确性
- ✅ **导入验证**: 依赖包可用性
- ✅ **pytest收集**: 测试发现和收集
- ✅ **依赖检查**: 工厂类完整性
- ✅ **执行测试**: 基础执行成功率

### 验证通过标准
- 语法检查: 100%通过
- 导入验证: 100%通过  
- 整体评分: ≥75%为优秀

## 🐛 常见问题

### 问题1: ImportError
```bash
# 检查依赖
python -c "import pytest, factory, sqlalchemy"

# 安装缺失包
pip install pytest factory-boy sqlalchemy
```

### 问题2: 外键约束失败  
```python
# 使用SubFactory自动处理关系
session = SessionFactory(user=UserFactory())
```

### 问题3: pytest收集失败
```bash
# 使用简化conftest
cp tests/conftest_e2e.py tests/conftest_temp.py
```

## 📈 最佳实践

### 1. 模型命名规范
- 使用清晰的字段名: `username` 而非 `name`
- Email字段命名为 `email`
- 密码字段命名为 `password_hash`
- 时间字段使用 `created_at`, `updated_at`

### 2. 关系定义规范
- 始终使用 `back_populates`
- 明确指定 `secondary` 表名
- 避免循环依赖复杂关系

### 3. 测试使用规范
```python
# 推荐：使用工厂管理器
UserAuthFactoryManager.setup_factories(session)
user = UserFactory()

# 避免：手动创建复杂数据
user = User(username="test", email="test@example.com", ...)
```

## 🔧 故障排查

### 快速诊断
```bash
# 1. 检查语法
python -m py_compile tests/factories/{module}_factories.py

# 2. 测试导入
python -c "from tests.factories.{module}_factories import *"

# 3. 运行验证
python scripts/e2e_test_verification.py
```

### 日志分析
- 检查 `docs/analysis/` 目录下的验证报告
- 查看具体的错误信息和改进建议
- 关注整体质量评分和各项通过率

## 📞 支持信息

### 相关文档
- 完整使用指南: `docs/development/intelligent-test-generator-guide.md`
- 测试标准: `docs/standards/testing-standards.md`
- 工作状态: `docs/status/current-work-status.md`

### 检查点标准
- [CHECK:TEST-001] 测试代码生成标准
- [CHECK:TEST-002] Factory Boy数据工厂标准
- [CHECK:TEST-008] 测试质量自动验证标准  
- [CHECK:DEV-009] 代码生成质量标准
- [CHECK:DOC-001] 文档标准

---
*版本: v2.0 | 更新时间: 2025-09-20 | 遵循标准: [CHECK:DOC-001] [CHECK:DEV-009]*