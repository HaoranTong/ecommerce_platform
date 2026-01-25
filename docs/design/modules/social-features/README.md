<!--
文档说明：
- 内容：模块README导航模板，模块入口文档
- 作用：提供快速导航和基本信息，不包含详细内容
# social-features 社交功能模块

📋 **状态**: 设计完成（等待实现）  
👤 **负责人**: Growth Experience 团队  
🔄 **最后更新**: 2025-10-25

## 快速导航

| 文档类型 | 文档名称 | 描述 |
|---------|----------|------|
| **概览** | [overview.md](./overview.md) | 业务职责、边界、技术架构总览 |
| **需求** | [requirements.md](./requirements.md) | REQ清单、验收标准与非功能约束 |
| **设计** | [design.md](./design.md) | A8标准的技术设计与决策说明 |
| **API规范** | [api-spec.md](./api-spec.md) | A10标准接口契约、请求响应定义 |
| **API实施** | [api-implementation.md](./api-implementation.md) | 规范与代码实现映射、落地状态 |
| **实现记录** | [implementation.md](./implementation.md) | 代码实施计划、测试与风险记录 |

## 模块简介

social-features 模块隶属于营销域，负责承载社交传播、推荐有礼、邀请奖励等增长玩法的后端能力。模块通过“分享→互动→转化→奖励”闭环，统一管理分享链接、邀请关系、奖励兑现与指标统计，为 product_catalog、marketing_campaigns 等上游提供插件化的社交增长能力，同时保持与订单、会员积分等核心域解耦。

### 核心能力

- 生成带追踪参数的分享链接，按资源类型（商品、活动、落地页）管理生命周期
- 采集分享点击、注册、首单等转化事件，形成可审计的分享链路
- 维护邀请人与被邀请人的关联关系，驱动奖励条件判断
- 协调奖励发放，触发积分、优惠券等跨模块动作并记录发放状态
- 输出日常监控指标和运营看板数据接口，支撑精细化运营决策

### 技术栈与依赖

- **基础技术**: FastAPI 0.104.1、SQLAlchemy 2.0.23、Pydantic 2.5.0、Alembic、Redis（缓存与幂等控制预留）
- **安全与日志**: JWT 鉴权、RBAC 权限模型、security_logger 审计通道
- **跨模块依赖**:
	- `user_auth`：验证分享人与操作者身份
	- `product_catalog` / `marketing_campaigns`：校验被分享资源合法性、读取元数据
	- `member_system`：调用积分发放接口
	- `marketing_campaigns`：触发优惠券发放
	- `order_management`：消费首单完成事件（通过事件总线）

### 业务上下游关系

- **上游触发方**: 前端分享入口、运营活动配置、订单/注册事件流
- **下游消费方**: 数据分析平台、营销活动模块（用于奖励履约）、通知服务（发送奖励通知）
- **外部通道**: 微信/短链等分享渠道由前端或专用适配器生成，模块保存追踪参数与统计数据

> 更多实现细节与上线计划请参阅 `implementation.md`，接口契约详见 `api-spec.md`。
- [API设计规范](../../standards/api-standards.md)
