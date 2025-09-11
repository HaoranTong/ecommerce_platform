<!--
文档说明：
- 内容：API文档的导航和使用说明
- 使用方法：API文档的入口，提供完整的API文档导航
- 更新方法：新增API模块时更新导航链接
- 引用关系：被开发团队、前端团队、测试团队引用
- 更新频率：新模块API文档创建时
-->

# API文档中心

## 📋 文档导航

### 🎯 API设计规范
- **[API设计标准](standards.md)** - API设计原则、URL规范、认证授权标准
- **[OpenAPI规范](openapi.yaml)** - 完整的API规范文件，支持代码生成

### 🔧 模块API文档

#### 核心交易模块
- **[购物车API](modules/cart/api-spec.md)** - 购物车管理接口
- **[用户认证API](modules/user-auth/api-spec.md)** - 用户登录注册接口 *(规划中)*
- **[商品管理API](modules/product/api-spec.md)** - 商品CRUD接口 *(规划中)*
- **[订单管理API](modules/order/api-spec.md)** - 订单处理接口 *(规划中)*
- **[支付系统API](modules/payment/api-spec.md)** - 支付集成接口 *(规划中)*

#### 农产品特色模块
- **[批次溯源API](modules/batch-trace/api-spec.md)** - 农产品溯源接口 *(规划中)*
- **[分销商API](modules/distributor/api-spec.md)** - 分销商管理接口 *(规划中)*

#### 营销和服务模块
- **[会员系统API](modules/member/api-spec.md)** - 会员等级积分接口 *(规划中)*
- **[营销活动API](modules/marketing/api-spec.md)** - 优惠券促销接口 *(规划中)*
- **[通知服务API](modules/notification/api-spec.md)** - 消息推送接口 *(规划中)*

#### 管理和分析模块
- **[库存管理API](modules/inventory/api-spec.md)** - 库存管理接口 *(规划中)*
- **[数据分析API](modules/analytics/api-spec.md)** - 数据分析接口 *(规划中)*

## 🚀 快速开始

### 开发人员
1. 首先阅读 [API设计标准](standards.md) 了解设计原则
2. 查看 [OpenAPI规范](openapi.yaml) 获取完整API定义
3. 根据需要查阅具体模块的API文档

### 前端开发
1. 使用 [OpenAPI规范](openapi.yaml) 生成客户端SDK
2. 参考各模块API文档了解接口详情和示例
3. 遵循统一的错误处理和认证方式

### 测试团队
1. 基于各模块API文档创建测试用例
2. 使用OpenAPI规范进行自动化API测试
3. 验证API响应格式和错误处理

## 📡 API基础信息

### 服务地址
- **开发环境**: `http://localhost:8000`
- **测试环境**: `https://test-api.example.com`
- **生产环境**: `https://api.example.com`

### 通用配置
- **API版本**: v1
- **基础路径**: `/api/v1`
- **认证方式**: Bearer Token (JWT)
- **内容类型**: `application/json`
- **字符编码**: UTF-8

### 通用HTTP状态码
| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | 请求成功 | 查询、更新成功 |
| 201 | 创建成功 | 资源创建成功 |
| 400 | 请求错误 | 参数验证失败 |
| 401 | 未认证 | Token无效或过期 |
| 403 | 权限不足 | 访问被拒绝 |
| 404 | 资源不存在 | 查询资源不存在 |
| 500 | 服务器错误 | 内部服务器错误 |

## 🔒 认证授权

所有API请求都需要在请求头中包含有效的JWT Token：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

## 📝 API文档维护

### 文档更新流程
1. **功能开发** - 开发新功能时同步更新API文档
2. **文档审查** - 技术负责人审查API设计和文档
3. **测试验证** - 基于文档进行API测试
4. **文档发布** - 合并到主分支并发布

### 文档规范要求
- 遵循 [API设计标准](standards.md) 的设计原则
- 包含完整的请求/响应示例
- 提供错误处理说明
- 保持与代码实现同步

---

📚 **相关文档**: [架构总览](../architecture/overview.md) | [功能需求](../requirements/functional.md) | [开发规范](../development/standards.md)
