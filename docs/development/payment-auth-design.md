# 支付模块认证集成设计

## 文档说明
- **内容**: 支付模块的认证集成设计和安全规范
- **使用方法**: 支付API开发的认证指导文档
- **更新方法**: 支付策略和安全要求变更时更新
- **引用关系**: 基于认证集成设计文档，指导支付模块开发
- **更新频率**: 支付安全策略调整时

## 支付安全设计原则

### 核心安全要求
1. **严格认证**: 所有支付相关操作必须经过用户认证
2. **权限验证**: 用户只能操作自己的支付订单
3. **管理员监控**: 管理员可以查看和管理所有支付记录
4. **敏感信息保护**: 支付凭据和个人信息加密存储
5. **操作审计**: 所有支付操作必须记录审计日志

### 支付权限矩阵

| 支付API端点 | 匿名用户 | 普通用户 | 管理员 | 说明 |
|------------|---------|---------|--------|------|
| **支付方式查询** | ✅ | ✅ | ✅ | 获取可用支付方式 |
| **创建支付订单** | ❌ | ✅(自己) | ✅(任意) | 为订单创建支付 |
| **查询支付状态** | ❌ | ✅(自己) | ✅(所有) | 支付状态查询 |
| **支付回调处理** | 🔒 | 🔒 | 🔒 | 仅支付平台回调 |
| **支付记录查询** | ❌ | ✅(自己) | ✅(所有) | 历史支付记录 |
| **退款申请** | ❌ | ✅(自己) | ✅(任意) | 申请退款 |
| **退款处理** | ❌ | ❌ | ✅ | 处理退款申请 |
| **支付配置管理** | ❌ | ❌ | ✅ | 支付渠道配置 |

## V1.0 Mini-MVP支付认证范围

### 第一版本支付功能
**目标**: 实现基础的微信支付集成，满足Mini-MVP需求

#### 必需API端点
1. **POST /api/payments** - 创建支付订单
   - **权限**: 用户认证 + 订单所有权验证
   - **功能**: 为已创建的订单生成支付单

2. **GET /api/payments/{payment_id}** - 查询支付状态
   - **权限**: 用户认证 + 支付单所有权验证
   - **功能**: 查询支付进度和状态

3. **POST /api/payments/callback/wechat** - 微信支付回调
   - **权限**: 微信签名验证（无需用户认证）
   - **功能**: 处理微信支付结果通知

4. **GET /api/payments** - 支付记录查询
   - **权限**: 用户认证 + 数据隔离
   - **功能**: 查询个人支付历史

#### 管理员API端点
1. **GET /api/admin/payments** - 所有支付记录
   - **权限**: 管理员认证
   - **功能**: 管理员查看所有支付记录

2. **POST /api/admin/payments/{payment_id}/refund** - 处理退款
   - **权限**: 管理员认证
   - **功能**: 管理员处理退款申请

## 认证集成实现

### 1. 支付API认证依赖
```python
# 支付模块认证依赖
from app.auth import (
    get_current_active_user,     # 用户认证
    get_current_admin_user,      # 管理员认证  
    require_ownership,           # 所有权验证
    check_resource_ownership     # 资源所有权依赖
)
```

### 2. 支付单所有权验证
```python
def verify_payment_ownership(payment_id: int, current_user: User, db: Session):
    """验证支付单所有权"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(404, "支付单不存在")
    
    # 通过订单验证所有权
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not require_ownership(order.user_id, current_user):
        raise HTTPException(403, "无权访问此支付单")
    
    return payment
```

### 3. 支付回调安全验证
```python
def verify_wechat_signature(data: dict, signature: str) -> bool:
    """验证微信支付回调签名"""
    # 实现微信支付签名验证逻辑
    # 不需要用户认证，但需要验证来源
    pass
```

## 数据模型设计

### Payment模型安全字段
```python
class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 所有权字段
    
    # 支付信息
    payment_method = Column(String(50), nullable=False)  # 'wechat', 'alipay'
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='CNY')
    
    # 状态字段
    status = Column(String(20), default='pending')  # 'pending', 'paid', 'failed', 'refunded'
    
    # 第三方信息（加密存储）
    external_payment_id = Column(String(200))  # 微信订单号
    external_transaction_id = Column(String(200))  # 微信交易号
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime, nullable=True)
    
    # 关系
    order = relationship("Order", back_populates="payments")
    user = relationship("User", back_populates="payments")
```

## 安全措施

### 1. 敏感信息保护
- 支付凭据加密存储
- 个人信息脱敏显示
- 日志中不记录敏感信息

### 2. 防重放攻击
- 支付回调幂等性检查
- 请求时间戳验证
- 订单状态锁定机制

### 3. 金额验证
- 订单金额与支付金额一致性检查
- 防止金额篡改
- 币种一致性验证

### 4. 审计日志
```python
class PaymentAuditLog(Base):
    __tablename__ = 'payment_audit_logs'
    
    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey('payments.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(50))  # 'create', 'pay', 'refund', 'cancel'
    old_status = Column(String(20))
    new_status = Column(String(20))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
```

## 错误处理

### 支付专用错误响应
```python
class PaymentError:
    PAYMENT_NOT_FOUND = {
        "error": "payment_not_found",
        "message": "支付单不存在",
        "code": 404
    }
    
    PAYMENT_OWNERSHIP_REQUIRED = {
        "error": "payment_ownership_required", 
        "message": "只能操作自己的支付单",
        "code": 403
    }
    
    INVALID_PAYMENT_STATUS = {
        "error": "invalid_payment_status",
        "message": "支付单状态不允许此操作", 
        "code": 400
    }
    
    PAYMENT_AMOUNT_MISMATCH = {
        "error": "payment_amount_mismatch",
        "message": "支付金额与订单金额不符",
        "code": 400
    }
```

## 实施计划

### 阶段1: 支付模型和基础认证 (1天)
- [ ] 创建Payment模型和数据库迁移
- [ ] 实现支付单所有权验证函数
- [ ] 创建支付API路由框架

### 阶段2: 微信支付集成 (2天)  
- [ ] 微信支付SDK集成
- [ ] 支付创建API + 用户认证
- [ ] 支付状态查询API + 所有权验证
- [ ] 微信支付回调处理

### 阶段3: 管理和审计功能 (1天)
- [ ] 管理员支付查询API
- [ ] 退款功能和管理员权限
- [ ] 审计日志系统

### 阶段4: 安全加固和测试 (1天)
- [ ] 敏感信息加密
- [ ] 安全测试和漏洞检查
- [ ] 端到端支付流程测试

## 验收标准

### 功能验收
- ✅ 用户可以为自己的订单创建支付
- ✅ 用户只能查看自己的支付记录
- ✅ 管理员可以查看和管理所有支付
- ✅ 支付回调正确处理状态更新
- ✅ 所有支付操作有审计记录

### 安全验收
- ✅ 无未授权支付访问漏洞
- ✅ 敏感信息不泄露
- ✅ 支付金额无法篡改
- ✅ 回调签名验证正确
- ✅ 防重放攻击机制有效

### 性能验收
- ✅ 支付创建响应时间 < 1秒
- ✅ 支付状态查询响应时间 < 500ms
- ✅ 支付回调处理时间 < 2秒
- ✅ 支持并发支付请求

---

**设计文档创建时间**: 2025-09-11  
**目标完成时间**: 支付模块开发开始前  
**下一次更新**: 支付集成实施过程中
