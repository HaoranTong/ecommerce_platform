# 文档模板

📝 **文档类型**: 模块文档创建模板集合  
📍 **作用**: 确保所有模块文档结构一致性和完整性  
🔗 **使用方法**: 创建新模块时复制对应模板

## � 目录结构

```
templates/
├── module-template.md              # 模块概述文档模板 (overview.md)
├── module-readme-template.md       # 模块导航文档模板 (README.md)
├── module-requirements-template.md # 业务需求文档模板 (requirements.md)
├── module-design-template.md       # 技术设计文档模板 (design.md)
├── module-implementation-template.md # 实现记录文档模板 (implementation.md)
└── README.md                       # 本文档
```

## 🚨 强制文档要求

每个模块**必须**包含以下7个文档（无可选项）：

| 序号 | 文档文件 | 对应模板 | 文档职责 |
|------|----------|----------|----------|
| 1 | `README.md` | `module-readme-template.md` | 模块导航入口 |
| 2 | `overview.md` | `module-template.md` | 详细技术概述 |
| 3 | `requirements.md` | `module-requirements-template.md` | 业务需求规格 |
| 4 | `design.md` | `module-design-template.md` | 技术设计决策 |
| 5 | `api-spec.md` | (已有标准) | API规范定义 |
| 6 | `api-implementation.md` | (已有标准) | API实施记录 |
| 7 | `implementation.md` | `module-implementation-template.md` | 开发实现记录 |

## 📋 使用流程

### 创建新模块文档
```bash
# 1. 创建模块目录
mkdir docs/modules/{module-name}

# 2. 复制所有必需模板
cp docs/templates/module-readme-template.md docs/modules/{module-name}/README.md
cp docs/templates/module-template.md docs/modules/{module-name}/overview.md
cp docs/templates/module-requirements-template.md docs/modules/{module-name}/requirements.md
cp docs/templates/module-design-template.md docs/modules/{module-name}/design.md
cp docs/templates/module-implementation-template.md docs/modules/{module-name}/implementation.md

# 3. API文档需要手动创建
touch docs/modules/{module-name}/api-spec.md
touch docs/modules/{module-name}/api-implementation.md
```

### 模板变量替换
所有模板中的变量需要替换为实际值：
- `{模块名称}`: 中文名称，如"用户认证模块"
- `{module-name}`: 英文名称，如"user-auth"
- `{module_name}`: 代码名称，如"user_auth"
- `{YYYY-MM-DD}`: 日期格式
- `{负责人姓名}`: 负责人信息

## 📝 模板使用流程

### 创建新模块文档
1. **复制模板** - 复制module-template.md到目标目录
2. **重命名文件** - 按照命名规范重命名为overview.md
3. **填写内容** - 按照模板格式填写具体内容
4. **检查完整性** - 确保所有章节都有相应内容
5. **提交审核** - 提交给相关负责人审核

### 模板内容规范
- **完整性** - 包含该类文档的所有必需章节
- **指导性** - 每个章节都有清晰的填写说明
- **示例性** - 提供具体的内容示例
- **一致性** - 遵循项目的文档风格和格式

## 🔧 模板维护

### 更新原则
- 基于实际使用反馈改进模板
- 保持模板的简洁性和实用性
- 确保新模板符合MASTER.md中的文档规范
- 重大模板变更需要团队评审

### 版本管理
- 模板变更需要记录变更原因和影响
- 保留模板的历史版本用于参考
- 新模板发布时需要通知相关团队成员

## 📋 模板检查清单

### 模块文档模板检查
- [ ] 包含模块概述章节
- [ ] 包含技术架构设计
- [ ] 包含API接口规范
- [ ] 包含数据模型设计
- [ ] 包含部署配置说明
- [ ] 包含测试策略
- [ ] 包含监控告警配置

### 通用文档要求
- [ ] 文档头部包含元信息注释
- [ ] 章节结构清晰合理
- [ ] 包含必要的图表和示例
- [ ] 链接引用格式正确
- [ ] 遵循Markdown格式规范

## 🎨 格式规范

### 文档结构
```markdown
# 文档标题

## 概述部分
<!-- 文档的总体介绍 -->

## 详细设计
<!-- 具体的设计内容 -->

## 实现说明
<!-- 技术实现细节 -->

## 运维配置
<!-- 部署和运维相关 -->
```

### 常用元素
- **代码块** - 使用三重反引号标记
- **表格** - 用于结构化数据展示
- **列表** - 有序列表和无序列表
- **链接** - 内部文档链接和外部链接
- **图表** - Mermaid图表和图片

## ⚠️ 使用注意事项

- 使用模板时不要删除模板中的说明性注释
- 根据实际情况调整模板内容，但保持基本结构
- 新增章节时要保持与现有章节的一致性
- 模板内容要定期与最新的文档规范同步

## 🔗 相关文档

- [MASTER.md - 文档命名规范](../MASTER.md#文档命名规范)
- [development/documentation-standards.md](../development/documentation-standards.md) - 详细文档编写标准
