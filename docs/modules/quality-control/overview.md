<!--
文档说明：
- 内容：质量控制模块功能概览，包括证书管理、质量认证、合规检查等核心功能
- 使用方法：质量控制模块设计和开发的指导文档，开发前必读
- 更新方法：模块功能变更时更新，需要架构师确认
- 引用关系：被其他模块文档和API规范文档引用
- 更新频率：功能迭代时
-->

# 质量控制模块 (Quality Control Module)

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## 模块概述

### 主要职责
质量控制模块负责农产品电商平台的质量认证管理，确保商品质量可追溯和消费者信任：
- **证书存储管理** - 统一管理各类质量认证证书
- **质量认证验证** - 验证第三方机构认证证书的真实性
- **合规性检查** - 确保农产品符合食品安全法规要求
- **溯源关联服务** - 为批次溯源提供质量证明支撑
- **消费者展示** - 在商品页面展示权威认证信息

### 业务价值
- **核心价值**: 通过权威认证建立消费者对农产品质量的信任
- **用户收益**: 消费者可以查看权威质检报告，放心购买农产品
- **系统收益**: 为整个电商平台建立质量保证体系，提升品牌价值

### 模块边界
- **包含功能**: 证书CRUD管理、证书验证查询、质量信息展示
- **排除功能**: 不包含质量检测过程、不负责检测机构对接
- **依赖模块**: 共享数据模型(Certificate)、批次溯源模块
- **被依赖**: 商品管理模块、订单管理模块、供应商管理模块

## 技术架构

### 架构图
```
质量控制模块架构
┌─────────────────────────────────────────────────────┐
│                 Quality Control                      │
├─────────────────────────────────────────────────────┤
│  API Layer                                          │
│  ├── POST /certificates        创建证书             │
│  ├── GET  /certificates        获取证书列表         │
│  ├── GET  /certificates/{id}   获取证书详情         │
│  └── DELETE /certificates/{id} 删除证书             │
├─────────────────────────────────────────────────────┤
│  Service Layer                                      │
│  ├── CertificateService        证书业务逻辑         │
│  ├── ValidationService         证书验证服务         │
│  └── ComplianceService         合规检查服务         │
├─────────────────────────────────────────────────────┤
│  Data Layer                                         │
│  └── Certificate Model         证书数据模型         │
└─────────────────────────────────────────────────────┘
          │                           │
          ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│  Batch Module   │         │ Product Module  │
│   批次溯源模块   │         │   商品管理模块   │
└─────────────────┘         └─────────────────┘
```

### 核心组件
```
quality_control/
├── router.py           # API路由定义
├── service.py          # 业务逻辑处理
├── models.py           # 数据模型定义（当前为空，使用共享模型）
├── schemas.py          # 请求/响应模型（待实现）
└── dependencies.py     # 模块依赖注入
```

## 数据模型

### Certificate 模型（共享模型）
```python
class Certificate(Base):
    __tablename__ = 'certificates'
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(200), nullable=False)        # 证书名称
    issuer = Column(String(200), nullable=True)       # 发证机构
    serial = Column(String(200), unique=True, nullable=False)  # 证书序列号
    description = Column(Text, nullable=True)         # 证书描述（待扩展）
    
    # 待扩展字段：
    # issue_date = Column(Date)                       # 发证日期
    # expire_date = Column(Date)                      # 过期日期
    # certificate_type = Column(String(50))           # 证书类型
    # file_url = Column(String(500))                  # 证书文件URL
    # verification_url = Column(String(500))          # 验证查询URL
```

### 支持的证书类型
- **有机认证证书** - 有机农产品认证
- **绿色食品认证** - 绿色食品标识认证
- **无公害认证** - 无公害农产品认证
- **地理标志认证** - 农产品地理标志认证
- **质检报告** - 第三方检测机构质检报告
- **ISO认证** - ISO质量管理体系认证

## API 接口

### 证书管理接口

#### 1. 创建证书
```http
POST /api/v1/quality-control/certificates
Content-Type: application/json

{
    "name": "有机认证证书",
    "issuer": "中国有机产品认证中心",
    "serial": "COFCC-R-2024-001234",
    "description": "有机蔬菜认证，有效期至2025年12月"
}
```

#### 2. 获取证书列表
```http
GET /api/v1/quality-control/certificates?skip=0&limit=100
```

#### 3. 获取证书详情
```http
GET /api/v1/quality-control/certificates/{certificate_id}
```

#### 4. 删除证书
```http
DELETE /api/v1/quality-control/certificates/{certificate_id}
```

## 业务逻辑

### 证书管理流程
1. **证书上传** - 供应商或管理员上传质量认证证书
2. **信息录入** - 录入证书基本信息（名称、发证机构、序列号等）
3. **真实性验证** - 通过发证机构官网验证证书真实性（后期功能）
4. **关联商品** - 将证书关联到对应的商品或批次
5. **消费者展示** - 在商品页面展示相关认证证书

### 质量保证体系
1. **认证层级**
   - 基础认证：无公害农产品认证
   - 中级认证：绿色食品认证
   - 高级认证：有机产品认证

2. **检测报告管理**
   - 农药残留检测报告
   - 重金属检测报告
   - 微生物检测报告
   - 营养成分检测报告

3. **合规性检查**
   - 证书有效期验证
   - 发证机构权威性验证
   - 适用范围验证

## 性能优化

### 缓存策略
- **证书列表缓存** - 使用Redis缓存热门证书列表
- **证书详情缓存** - 缓存经常查询的证书详情
- **验证结果缓存** - 缓存证书验证结果，避免重复验证

### 查询优化
- **索引优化** - 在证书序列号字段建立唯一索引
- **分页查询** - 支持大量证书的分页查询
- **关联查询** - 优化证书与商品的关联查询性能

## 集成接口

### 与其他模块的集成

#### 1. 批次溯源模块
```python
# 获取批次相关的质量证书
async def get_batch_certificates(batch_id: str) -> List[Certificate]:
    # 通过批次ID获取关联的质量证书
    pass
```

#### 2. 商品管理模块
```python
# 获取商品相关的质量证书
async def get_product_certificates(product_id: int) -> List[Certificate]:
    # 通过商品ID获取关联的质量证书
    pass
```

#### 3. 供应商管理模块
```python
# 获取供应商的资质证书
async def get_supplier_certificates(supplier_id: int) -> List[Certificate]:
    # 通过供应商ID获取相关的资质证书
    pass
```

## 部署配置

### 环境变量
```bash
# 质量控制模块配置
QUALITY_CONTROL_ENABLED=true

# 证书文件存储配置
CERTIFICATE_STORAGE_TYPE=oss  # local/oss/s3
CERTIFICATE_STORAGE_URL=https://certificates.example.com

# 第三方验证接口配置（后期功能）
COFCC_VERIFY_URL=https://www.ofcc.org.cn/verify
GREEN_FOOD_VERIFY_URL=https://www.greenfood.org.cn/verify
```

### 数据库配置
```sql
-- 证书表索引优化
CREATE INDEX idx_certificates_serial ON certificates(serial);
CREATE INDEX idx_certificates_issuer ON certificates(issuer);
CREATE INDEX idx_certificates_name ON certificates(name);
```

## 相关文档

### 架构文档
- [系统架构总览](../../architecture/overview.md)
- [API设计规范](../../standards/api-standards.md)
- [数据模型规范](../../standards/database-standards.md)

### 开发文档
- [开发规范](../../development/development-standards.md)
- [测试指南](../../development/testing.md)
- [部署指南](../../operations/deployment.md)

### 需求文档
- [业务需求](../../requirements/business.md)
- [功能需求](../../requirements/functional.md)

### 相关模块
- [批次溯源模块](../batch-traceability/overview.md)
- [商品管理模块](../product-catalog/overview.md)
- [供应商管理模块](../supplier-management/overview.md)