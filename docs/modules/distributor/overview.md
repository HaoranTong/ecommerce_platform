# 分销商管理模块 (Distributor Management Module)

## 模块概述

### 功能定位
分销商管理模块支持多级分销体系，允许合作伙伴通过推广获得佣金，扩大销售渠道，实现业务快速增长。

### 核心价值
- **渠道扩展**: 通过分销商网络快速扩大市场覆盖
- **成本控制**: 基于效果付费，降低营销成本
- **关系管理**: 完善的分销商关系和等级管理
- **数据透明**: 实时的推广效果和佣金统计

## 业务需求

### 核心功能
1. **分销商管理**
   - 分销商注册和审核
   - 等级体系管理（普通、银牌、金牌、钻石）
   - 个人信息和资质管理

2. **推广工具**
   - 专属推广链接生成
   - 推广二维码生成
   - 推广素材库管理
   - 自定义推广页面

3. **佣金管理**
   - 佣金规则配置（比例、阶梯、特殊商品）
   - 佣金计算和结算
   - 佣金提现和支付
   - 佣金统计和报表

4. **团队管理**
   - 下级分销商邀请
   - 团队业绩统计
   - 团队佣金分配
   - 团队管理工具

## 技术设计

### 数据模型设计

#### 分销商表 (distributors)
```sql
CREATE TABLE distributors (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '关联用户ID',
    distributor_code VARCHAR(20) UNIQUE NOT NULL COMMENT '分销商编码',
    level ENUM('bronze', 'silver', 'gold', 'diamond') DEFAULT 'bronze',
    parent_id BIGINT COMMENT '上级分销商ID',
    status ENUM('pending', 'active', 'suspended', 'disabled') DEFAULT 'pending',
    join_date DATE NOT NULL,
    total_sales DECIMAL(12,2) DEFAULT 0 COMMENT '累计销售额',
    total_commission DECIMAL(10,2) DEFAULT 0 COMMENT '累计佣金',
    qualification_info JSON COMMENT '资质信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES distributors(id),
    INDEX idx_distributor_code (distributor_code),
    INDEX idx_parent_level (parent_id, level),
    INDEX idx_status_join (status, join_date)
);
```

#### 推广记录表 (promotion_records)
```sql
CREATE TABLE promotion_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    distributor_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    promotion_link VARCHAR(255) COMMENT '推广链接',
    visit_time TIMESTAMP COMMENT '访问时间',
    order_time TIMESTAMP COMMENT '下单时间',
    order_amount DECIMAL(10,2) NOT NULL COMMENT '订单金额',
    commission_rate DECIMAL(5,4) NOT NULL COMMENT '佣金比例',
    commission_amount DECIMAL(10,2) NOT NULL COMMENT '佣金金额',
    status ENUM('pending', 'confirmed', 'paid', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (distributor_id) REFERENCES distributors(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_distributor_status (distributor_id, status),
    INDEX idx_order_time (order_time),
    INDEX idx_promotion_link (promotion_link)
);
```

#### 佣金结算表 (commission_settlements)
```sql
CREATE TABLE commission_settlements (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    distributor_id BIGINT NOT NULL,
    settlement_period VARCHAR(20) NOT NULL COMMENT '结算周期 YYYY-MM',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '结算总额',
    order_count INT NOT NULL COMMENT '订单数量',
    settlement_status ENUM('calculating', 'pending', 'processing', 'completed', 'failed') DEFAULT 'calculating',
    payment_method ENUM('alipay', 'wechat', 'bank_transfer') COMMENT '提现方式',
    payment_account VARCHAR(100) COMMENT '提现账户',
    payment_time TIMESTAMP COMMENT '支付时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (distributor_id) REFERENCES distributors(id),
    INDEX idx_distributor_period (distributor_id, settlement_period),
    INDEX idx_settlement_status (settlement_status)
);
```

### API设计

#### 分销商管理API
```python
# 申请成为分销商
POST /api/distributors/apply
{
    "qualification_info": {
        "real_name": "张三",
        "id_card": "110101199001011234",
        "phone": "13800138000",
        "address": "北京市朝阳区...",
        "business_license": "可选，企业用户"
    }
}

# 分销商信息查询
GET /api/distributors/profile
Response:
{
    "id": 123,
    "distributor_code": "D20240901001",
    "level": "silver",
    "status": "active",
    "total_sales": 50000.00,
    "total_commission": 2500.00,
    "team_count": 8,
    "current_month_sales": 8000.00
}

# 邀请下级分销商
POST /api/distributors/invite
{
    "phone": "13900139000",
    "message": "邀请你成为我的分销伙伴"
}
```

#### 推广工具API
```python
# 生成推广链接
POST /api/distributors/promotion-links
{
    "product_id": 456,
    "campaign": "spring_sale",
    "custom_params": {"source": "wechat"}
}
Response:
{
    "link": "https://mall.example.com/product/456?ref=D20240901001&utm_source=wechat",
    "qr_code": "https://api.example.com/qr/generate?data=...",
    "short_link": "https://s.example.com/abc123"
}

# 推广素材获取
GET /api/distributors/materials?category=product&product_id=456
Response:
{
    "images": [
        {"url": "https://oss.../product_poster1.jpg", "size": "1080x1080"},
        {"url": "https://oss.../product_banner.jpg", "size": "750x300"}
    ],
    "texts": [
        "五常大米，品质保证！现在购买立享9折优惠！",
        "来自东北黑土地的天然好米，营养丰富，口感香甜！"
    ]
}
```

#### 佣金管理API
```python
# 佣金统计查询
GET /api/distributors/commission/stats?period=current_month
Response:
{
    "total_commission": 1200.50,
    "pending_commission": 300.00,
    "paid_commission": 900.50,
    "order_count": 25,
    "conversion_rate": 0.08,
    "top_products": [
        {"product_name": "五常大米5kg", "commission": 450.00},
        {"product_name": "有机小米2kg", "commission": 280.00}
    ]
}

# 申请提现
POST /api/distributors/withdraw
{
    "amount": 1000.00,
    "payment_method": "alipay",
    "payment_account": "138****8000",
    "notes": "月度佣金提现"
}

# 团队业绩查询
GET /api/distributors/team/performance
Response:
{
    "team_size": 12,
    "direct_members": 5,
    "total_team_sales": 25000.00,
    "team_commission": 1250.00,
    "active_members": 8,
    "top_performers": [...]
}
```

### 业务规则

#### 佣金计算规则
```python
class CommissionCalculator:
    """佣金计算规则"""
    
    # 基础佣金比例（按分销商等级）
    BASE_RATES = {
        'bronze': 0.05,    # 5%
        'silver': 0.08,    # 8%
        'gold': 0.12,      # 12%
        'diamond': 0.15    # 15%
    }
    
    # 特殊商品佣金
    SPECIAL_PRODUCT_RATES = {
        'category_1': 0.10,  # 高端产品
        'category_2': 0.03,  # 薄利产品
    }
    
    # 团队佣金（上级从下级销售中获得）
    TEAM_RATES = {
        'level_1': 0.02,  # 直推 2%
        'level_2': 0.01,  # 二级 1%
    }
```

#### 等级升级规则
```python
UPGRADE_RULES = {
    'bronze_to_silver': {
        'min_sales': 10000,      # 最低销售额
        'min_orders': 50,        # 最低订单数
        'min_team_size': 3       # 最低团队人数
    },
    'silver_to_gold': {
        'min_sales': 50000,
        'min_orders': 200,
        'min_team_size': 10,
        'min_active_team': 5     # 活跃团队成员
    },
    'gold_to_diamond': {
        'min_sales': 200000,
        'min_orders': 800,
        'min_team_size': 30,
        'min_active_team': 15,
        'min_team_sales': 100000  # 团队总销售额
    }
}
```

## 集成设计

### 与其他模块集成
1. **用户模块**: 分销商身份验证和权限
2. **订单模块**: 推广订单跟踪和佣金计算
3. **支付模块**: 佣金提现和结算
4. **商品模块**: 推广商品信息获取
5. **营销模块**: 优惠券和活动集成

### 外部集成
1. **支付宝/微信**: 佣金提现
2. **短信服务**: 邀请和通知
3. **数据分析**: 推广效果分析

## 实施计划

### 第一阶段 (MVP)
- [ ] 基础分销商注册和管理
- [ ] 简单推广链接生成
- [ ] 基础佣金计算和统计

### 第二阶段
- [ ] 多级分销体系
- [ ] 佣金提现功能
- [ ] 推广素材管理

### 第三阶段
- [ ] 高级推广工具
- [ ] 智能推广分析
- [ ] 分销商培训体系

## 风险控制

### 合规风险
- 避免传销模式（限制层级、关注商品销售）
- 遵循相关法律法规
- 建立完善的审计机制

### 技术风险
- 防刷佣金机制
- 数据安全保护
- 系统性能优化
