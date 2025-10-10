# Pre-commit Hook 使用指南

## 📋 概述

项目配置了Git Pre-commit Hook来自动进行代码质量检查，确保提交的代码符合质量标准。

**Hook位置**: `.git/hooks/pre-commit`

**版本**: v2.0  
**更新时间**: 2025-10-10

## 🔍 检查项目

Pre-commit Hook会自动执行以下3项检查：

### 1. sku_id数据类型检查
- **目的**: 防止sku_id使用字符串类型
- **要求**: sku_id必须是Integer类型
- **示例错误**: 
  ```python
  # ❌ 错误
  data = {"sku_id": "123"}
  
  # ✅ 正确
  sku = SKU(...)
  data = {"sku_id": sku.id}
  ```

### 2. 测试生成器代码质量检查
- **目的**: 防止测试生成器代码包含硬编码和质量问题
- **范围**: `tools/test_generators/` 目录下的所有`.py`文件
- **检查内容**:
  - 硬编码的测试数据（如 `"test_value"`, `"test@example.com"`）
  - 硬编码的邮箱、密码、用户名
  - 业务逻辑硬编码
  
- **常见问题修复**:
  ```python
  # ❌ 错误：硬编码
  param_parts.append('"test_value"')
  email = "test@example.com"
  
  # ✅ 正确：使用动态生成
  param_parts.append(f'entity.{param_name}')
  email = self._generate_test_email(suffix)
  ```

### 3. Python语法检查
- **目的**: 确保所有Python文件语法正确
- **范围**: 所有暂存的`.py`文件
- **检查方式**: 使用`python -m py_compile`

## ✅ 正常工作流

当你提交代码时，Hook会自动运行：

```bash
git add <files>
git commit -m "your commit message"
```

**输出示例（成功）**:
```
🔍 开始Pre-commit代码质量检查...

📋 [1/3] 检查sku_id数据类型...
✅ sku_id数据类型检查通过

📋 [2/3] 检查测试生成器代码质量...
🔍 发现测试生成器文件变更，运行质量检查...
  检查: tools/test_generators/api_test_generator.py
✅ 测试生成器代码质量检查通过

📋 [3/3] 检查Python语法...
✅ Python语法检查通过

🎉 所有Pre-commit检查通过！

[dev abc1234] your commit message
 1 file changed, 10 insertions(+)
```

## ❌ 检查失败处理

如果检查失败，提交会被阻止：

```
❌ 质量检查失败: tools/test_generators/repository_test_generator.py
📋 发现硬编码或代码质量问题

💡 查看详细报告:
   python tools/check_quality.py --hardcode --file tools/test_generators/repository_test_generator.py

🔧 常见问题修复:
   • 避免硬编码测试数据 (如 'test_value', 'test@example.com')
   • 使用entity.{field_name}而不是字面量
   • 使用_generate_test_value()方法生成测试值

🚫 提交被阻止，请修复质量问题后重试
```

**处理步骤**:

1. **查看详细报告**:
   ```bash
   python tools/check_quality.py --hardcode --file <问题文件>
   ```

2. **修复问题**: 根据报告中的建议修复代码

3. **重新提交**:
   ```bash
   git add <修复的文件>
   git commit -m "fix: 修复代码质量问题"
   ```

## 🔧 高级用法

### 手动运行质量检查

```bash
# 检查单个文件
python tools/check_quality.py --hardcode --file <file_path>

# 检查整个目录
python tools/check_quality.py --hardcode --dir tools/test_generators/

# 运行所有检查（包括重复代码）
python tools/check_quality.py --all --dir tools/test_generators/
```

### 临时跳过Hook（不推荐）

如果确实需要跳过检查（例如紧急修复），可以使用：

```bash
git commit -m "message" --no-verify
```

**⚠️ 警告**: 
- 仅在紧急情况下使用
- 跳过检查后，必须在后续提交中修复质量问题
- 不符合质量标准的代码可能导致CI/CD失败

### 禁用Hook

如果需要临时禁用Hook：

```bash
# Windows
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled

# 恢复
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

## 📊 检查统计

你可以定期运行全项目质量检查来获取统计信息：

```bash
# 检查所有测试生成器
python tools/check_quality.py --all --dir tools/test_generators/

# 检查整个项目
python tools/check_quality.py --all --dir .
```

## 🐛 故障排除

### 问题1: Hook没有执行

**原因**: Git可能没有正确配置Hook

**解决**:
```bash
# 检查Hook文件是否存在
ls .git/hooks/pre-commit

# 确保Git配置了Hook
git config --local core.hooksPath .git/hooks
```

### 问题2: 检查工具找不到

**原因**: Python环境未激活或路径问题

**解决**:
```bash
# 确保在正确的虚拟环境中
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/Mac

# 测试检查工具
python tools/check_quality.py --help
```

### 问题3: 误报（False Positive）

**原因**: 质量检查工具的规则可能需要调整

**解决**:
1. 查看 `tools/check_quality.py` 中的忽略规则
2. 如果是合理的代码被误报，更新忽略规则
3. 提交Issue讨论规则调整

## 📚 相关文档

- [代码质量检查工具文档](../tools/check_quality.py) - 查看详细的检查规则
- [测试生成器开发指南](../docs/development/) - 了解测试生成器最佳实践
- [Git工作流规范](../docs/development/git-workflow.md) - 了解完整的提交流程

## 🔄 更新记录

- **v2.0** (2025-10-10): 
  - 添加测试生成器质量检查
  - 添加Python语法检查
  - 优化错误提示信息

- **v1.0** (2025-10-09):
  - 初始版本：sku_id数据类型检查

## 💡 最佳实践

1. **在修改测试生成器前，先运行质量检查**
   ```bash
   python tools/check_quality.py --hardcode --file <要修改的文件>
   ```

2. **修改后再次检查**
   ```bash
   python tools/check_quality.py --hardcode --file <修改的文件>
   ```

3. **提交前确保所有检查通过**
   - Hook会自动运行，但提前检查可以节省时间

4. **定期运行全项目扫描**
   - 每周运行一次全项目质量检查
   - 及时发现和修复累积的质量问题

## 🤝 贡献

如果发现检查规则的问题或有改进建议，请：
1. 在Issue中讨论
2. 提交PR更新规则
3. 更新本文档

---

**最后更新**: 2025-10-10  
**维护者**: Development Team  
**反馈**: 请在项目Issue中提交
