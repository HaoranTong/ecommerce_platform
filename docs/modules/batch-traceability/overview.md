# 批次管理与溯源模块 (Batch Management & Traceability Module)

## 模块概述

### 功能定位
批次管理与溯源模块是农产品电商平台的核心差异化功能，负责产品从生产到销售全链路的批次管理和溯源信息记录，确保产品质量可追溯、真实性可验证。

### 核心价值
- **全链路溯源**: 从种植/生产 → 加工 → 仓储 → 物流 → 销售的完整追溯
- **质量保证**: 每个批次的质量检测、认证信息完整记录
- **风险控制**: 出现质量问题时可快速定位影响范围
- **品牌建设**: 透明的溯源信息提升消费者信任度

## 业务需求

### 核心功能
1. **批次生命周期管理**
   - 批次创建和唯一标识生成
   - 批次状态跟踪（生产中、加工中、入库、出库、销售中、已售完）
   - 批次分割和合并操作

2. **溯源信息记录**
   - 生产信息（产地、种植时间、环境数据）
   - 加工信息（加工时间、工艺参数、操作人员）
   - 检测信息（质量检测报告、认证证书）
   - 物流信息（运输轨迹、温湿度监控）

3. **溯源查询服务**
   - 消费者端溯源查询（扫码查询、订单查询）
   - 管理端溯源分析（批次分析、质量统计）
   - 监管端溯源审计（合规检查、质量追溯）

## 技术设计

### 数据模型设计

#### 批次主表 (batches)
```sql
CREATE TABLE batches (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    batch_code VARCHAR(32) UNIQUE NOT NULL COMMENT '批次编码',
    product_id BIGINT NOT NULL COMMENT '关联商品ID',
    production_date DATE NOT NULL COMMENT '生产日期',
    expiry_date DATE COMMENT '过期日期',
    quantity DECIMAL(10,2) NOT NULL COMMENT '批次数量',
    unit VARCHAR(10) NOT NULL COMMENT '单位',
    status ENUM('producing', 'processing', 'warehoused', 'shipping', 'selling', 'sold_out') NOT NULL,
    origin_location JSON COMMENT '产地信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_batch_code (batch_code),
    INDEX idx_product_status (product_id, status),
    INDEX idx_production_date (production_date)
);
```

#### 溯源记录表 (traceability_records)
```sql
CREATE TABLE traceability_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    batch_id BIGINT NOT NULL,
    record_type ENUM('production', 'processing', 'quality_check', 'logistics', 'certificate') NOT NULL,
    record_time TIMESTAMP NOT NULL,
    operator_id BIGINT COMMENT '操作人员ID',
    location JSON COMMENT '操作地点',
    data JSON NOT NULL COMMENT '记录数据',
    attachments JSON COMMENT '附件信息',
    blockchain_hash VARCHAR(64) COMMENT '区块链哈希（未来扩展）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches(id),
    INDEX idx_batch_type (batch_id, record_type),
    INDEX idx_record_time (record_time)
);
```

### API设计

#### 批次管理API
```python
# 创建批次
POST /api/batches
{
    "product_id": 123,
    "production_date": "2024-09-01",
    "quantity": 1000.0,
    "unit": "kg",
    "origin_location": {
        "province": "黑龙江",
        "city": "五常市",
        "farm": "XX合作社"
    }
}

# 批次状态更新
PUT /api/batches/{batch_id}/status
{
    "status": "warehoused",
    "operator_id": 456,
    "location": {"warehouse": "北京仓库A"},
    "notes": "入库完成，质检合格"
}

# 批次分割
POST /api/batches/{batch_id}/split
{
    "quantities": [300.0, 700.0],
    "target_locations": ["仓库A", "仓库B"]
}
```

#### 溯源记录API
```python
# 添加溯源记录
POST /api/batches/{batch_id}/traceability
{
    "record_type": "quality_check",
    "record_time": "2024-09-02T10:00:00Z",
    "operator_id": 789,
    "data": {
        "test_items": ["重金属检测", "农残检测"],
        "results": ["合格", "合格"],
        "report_number": "QC20240902001"
    },
    "attachments": [
        {"type": "report", "url": "https://oss.../report.pdf"}
    ]
}

# 溯源查询
GET /api/traceability/{batch_code}
Response:
{
    "batch_info": {...},
    "traceability_chain": [
        {
            "step": "生产",
            "time": "2024-09-01",
            "location": "五常市XX合作社",
            "data": {...}
        },
        {...}
    ]
}
```

### 集成设计

#### 与其他模块集成
1. **商品模块**: 批次与商品的关联关系
2. **库存模块**: 批次库存的实时同步
3. **订单模块**: 订单商品的批次分配
4. **物流模块**: 批次运输状态同步

#### 第三方集成
1. **区块链服务**: 关键溯源信息上链存证
2. **IoT传感器**: 生产、运输环境数据采集
3. **检测机构**: 质检报告自动获取
4. **监管平台**: 溯源数据上报

## 实施计划

### 第一阶段 (MVP)
- [ ] 基础批次管理功能
- [ ] 简单溯源信息录入
- [ ] 消费者溯源查询

### 第二阶段
- [ ] 批次分割/合并功能
- [ ] 详细溯源链展示
- [ ] 管理端溯源分析

### 第三阶段
- [ ] 区块链集成
- [ ] IoT数据集成
- [ ] 智能溯源分析

## 合规要求

### 法规遵循
- 《食品安全法》溯源要求
- 《农产品质量安全法》相关规定
- 行业标准和认证要求

### 数据安全
- 溯源数据加密存储
- 访问权限严格控制
- 数据备份和恢复机制
