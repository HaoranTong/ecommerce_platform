# 检查点目录 (Checkpoint Directory)

针对每个子场景，定义唯一 ID 并明确触发条件、检查重点、导航路径、执行脚本。

| 子场景           | 检查点 ID    | 触发条件                       | 检查重点                     | 精准导航                                   | 执行脚本                                              |
|------------------|-------------|-------------------------------|------------------------------|--------------------------------------------|------------------------------------------------------|
| 项目启动         | REQ-001     | 新功能开发或项目初始化         | 业务背景、用户场景、成功指标 | `docs/requirements/business.md` 12-45 行   | `tools/validate_business_requirements.ps1`            |
| 功能需求分析     | REQ-002     | 设计功能或模块划分             | 功能完整性、优先级、验收标准 | `docs/requirements/functional.md` 1-80 行    | `tools/validate_functional_requirements.ps1`          |
| 数据模型设计     | DEV-003     | 修改或新增 models.py           | 字段类型、关系完整性、命名规范 | `docs/standards/database-standards.md` 45-70 行 | `tools/validate_data_model.ps1 -Module {module}`     |
| API 路由规范     | DEV-004     | 创建或修改 router.py           | RESTful 设计、认证授权、格式 | `docs/standards/api-standards.md` 15-40 行  | `tools/validate_api_design.ps1 -Module {module}`      |
| 异常处理实现     | DEV-007     | 实现异常捕获或错误响应设计     | 覆盖率、日志记录、状态码     | `docs/standards/api-standards.md` 200-240 行| `tools/validate_error_handling.ps1 -Module {module}`  |
| 单元测试         | TEST-002    | 运行测试脚本或提交单测改动     | 覆盖率、Mock 一致性           | `tests/unit/` 文件夹                        | `python tools/validate_test_config.py`                |
| 部署文档         | DOC-004     | 发布前或环境变更               | 部署流程、环境变量、命令行    | `docs/standards/deployment-standards.md` 50-80 行 | `tools/validate_deployment_docs.ps1` (待实现)         |

*其他子场景请依此格式补充。*