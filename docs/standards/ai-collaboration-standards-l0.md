# AI协作开发标准L0上下文（自动同步生成）

> 本文档由tools/sync_ai_collab_l0_section.py自动生成。
> 仅包含AI启动任务时需加载的核心流程、关键规则、目录与主线。
> 修改请在ai-collaboration-standards.md的<!-- L0-START -->与<!-- L0-END -->区段内进行。

<!-- 以下内容自动同步自ai-collaboration-standards.md L0区段 -->

## L0上下文（AI启动核心）

### 触发识别
- 标准指令："按照master文档规定执行：「具体任务」"
- AI识别触发语句后，自动加载ai-collaboration-standards-l0.md作为L0上下文
- 确认已加载L0上下文后，进入标准协作流程

### 核心约束
- MASTER.md为唯一AI入口，PROJECT-FOUNDATION.md为最高权威
- 标准化执行：TODO模板+检查点卡片+分步确认
- 禁止随意创建文档，必须通过[CHECK:DOC-XXX]检查点
- 每步强制暂停，用户确认后继续

### AI协作任务流程框架
1. MASTER入口与唤起
2. 任务理解与需求澄清
3. 任务拆解与模板建议
4. 上下文加载与执行准备
5. TODO模板驱动分步执行
6. 任务完成与归档
7. 异常处理与中断恢复
