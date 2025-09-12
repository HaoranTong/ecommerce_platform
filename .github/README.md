# GitHub Actions工作流

CI/CD自动化流程配置，包含代码检查、测试和部署工作流。

## 📁 目录结构

```
.github/
└── workflows/             # GitHub Actions工作流文件
    ├── ci.yml            # 持续集成工作流
    ├── test.yml          # 自动化测试工作流
    └── deploy.yml        # 部署工作流
```

## 🔧 工作流说明

| 工作流文件 | 触发条件 | 执行内容 |
|-----------|---------|---------|
| **ci.yml** | Push/PR到main/dev | 代码检查、依赖安装、构建测试 |
| **test.yml** | Push到任意分支 | 运行单元测试、集成测试 |
| **deploy.yml** | Release发布 | 自动部署到生产环境 |

## 🔗 相关文档

- [工作流程规范](../docs/standards/workflow-standards.md)
- [测试标准规范](../docs/standards/testing-standards.md)
- [部署指南](../docs/operations/deployment.md)