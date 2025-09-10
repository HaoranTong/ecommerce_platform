<!--
文档说明：
- 内容：数据模型设计的全局标准和规范，不包含具体表结构定义
- 使用方法：数据库设计时遵循的规范，确保数据模型一致性
- 更新方法：数据设计标准变更时更新，需要架构师确认
- 引用关系：被各模块的design.md文档引用
- 更新频率：设计标准变化时
-->

# 数据模型设计标准

## 设计原则

### 核心原则
1. **统一性** - 所有模块使用统一的字段命名和数据类型
2. **可扩展性** - 预留扩展字段，支持业务发展
3. **版本化** - 数据模型支持版本管理和迁移
4. **配置驱动** - 字段定义通过配置文件统一管理
5. **规范化** - 遵循数据库设计范式，减少冗余

### 设计约束
- **外键约束** - 使用外键保证数据完整性
- **索引策略** - 基于查询模式设计索引
- **字符集** - 统一使用 UTF8MB4 字符集
- **时区处理** - 所有时间字段使用 UTC 时区

## 命名规范

### 表命名规范
```sql
-- 表名：复数形式，下划线分隔
users                    -- 用户表
products                 -- 商品表
product_categories       -- 商品分类表
order_items             -- 订单明细表
user_addresses          -- 用户地址表
```

### 字段命名规范
```sql
-- 主键：id
id BIGINT PRIMARY KEY AUTO_INCREMENT

-- 外键：表名_id
user_id BIGINT          -- 用户ID
product_id BIGINT       -- 商品ID
category_id BIGINT      -- 分类ID

-- 布尔值：is_/has_/can_ 前缀
is_active BOOLEAN       -- 是否激活
has_stock BOOLEAN       -- 是否有库存
can_refund BOOLEAN      -- 是否可退款

-- 时间字段：_at 后缀
created_at TIMESTAMP    -- 创建时间
updated_at TIMESTAMP    -- 更新时间
deleted_at TIMESTAMP    -- 删除时间（软删除）

-- 金额字段：明确币种
price_cny DECIMAL(10,2) -- 人民币价格
amount_cny DECIMAL(10,2)-- 人民币金额
```

### 索引命名规范
```sql
-- 主键索引：pk_表名
pk_users                -- 用户表主键

-- 唯一索引：uk_表名_字段名
uk_users_email          -- 用户邮箱唯一索引
uk_products_sku         -- 商品SKU唯一索引

-- 普通索引：idx_表名_字段名
idx_products_category   -- 商品分类索引
idx_orders_user_id      -- 订单用户索引

-- 复合索引：idx_表名_字段1_字段2
idx_orders_user_status  -- 订单用户状态复合索引
```

## 数据类型标准

### 数值类型
```sql
-- 整型
TINYINT      -- 1字节，范围 -128 到 127
SMALLINT     -- 2字节，范围 -32,768 到 32,767
MEDIUMINT    -- 3字节，范围 -8,388,608 到 8,388,607
INT          -- 4字节，范围 -2^31 到 2^31-1
BIGINT       -- 8字节，范围 -2^63 到 2^63-1

-- 浮点型
DECIMAL(10,2)   -- 精确小数，用于金额
DECIMAL(8,4)    -- 精确小数，用于比率
FLOAT           -- 单精度浮点
DOUBLE          -- 双精度浮点
```

### 字符串类型
```sql
-- 固定长度
CHAR(32)        -- UUID 等固定长度字符串
CHAR(11)        -- 手机号

-- 可变长度
VARCHAR(50)     -- 用户名、商品名等短文本
VARCHAR(200)    -- 描述、地址等中等文本
VARCHAR(500)    -- URL、备注等长文本

-- 大文本
TEXT            -- 长文本内容
LONGTEXT        -- 超长文本内容
```

### 时间类型
```sql
-- 时间戳（推荐）
TIMESTAMP       -- 自动时区转换，范围 1970-2038
DATETIME        -- 不转换时区，范围 1000-9999

-- 日期
DATE            -- 仅日期，格式 YYYY-MM-DD
TIME            -- 仅时间，格式 HH:MM:SS
YEAR            -- 仅年份
```

### 特殊类型
```sql
-- 枚举类型
ENUM('active', 'inactive', 'deleted')   -- 状态枚举

-- JSON 类型
JSON            -- 存储 JSON 数据

-- 二进制类型
BLOB            -- 二进制大对象
LONGBLOB        -- 超大二进制对象
```

## 标准字段定义

### 通用字段
```sql
-- 所有表必须包含的字段
id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

-- 支持软删除的表添加
deleted_at TIMESTAMP NULL DEFAULT NULL COMMENT '删除时间',
is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',

-- 需要版本控制的表添加
version INT DEFAULT 1 COMMENT '版本号',

-- 需要审计的表添加
created_by BIGINT COMMENT '创建者用户ID',
updated_by BIGINT COMMENT '更新者用户ID'
```

### 业务字段模板
```sql
-- 用户相关字段
user_id BIGINT NOT NULL COMMENT '用户ID',
username VARCHAR(50) NOT NULL COMMENT '用户名',
email VARCHAR(100) UNIQUE COMMENT '邮箱',
phone CHAR(11) UNIQUE COMMENT '手机号',
password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',

-- 商品相关字段
product_id BIGINT NOT NULL COMMENT '商品ID',
sku VARCHAR(100) UNIQUE NOT NULL COMMENT '商品SKU',
name VARCHAR(200) NOT NULL COMMENT '商品名称',
price_cny DECIMAL(10,2) NOT NULL COMMENT '价格（人民币分）',
stock_quantity INT DEFAULT 0 COMMENT '库存数量',

-- 订单相关字段
order_id BIGINT NOT NULL COMMENT '订单ID',
order_no VARCHAR(32) UNIQUE NOT NULL COMMENT '订单号',
status ENUM('pending', 'paid', 'shipped', 'completed', 'cancelled') NOT NULL COMMENT '订单状态',
total_amount_cny DECIMAL(10,2) NOT NULL COMMENT '订单总金额',

-- 地址相关字段
province VARCHAR(50) NOT NULL COMMENT '省份',
city VARCHAR(50) NOT NULL COMMENT '城市',
district VARCHAR(50) NOT NULL COMMENT '区县',
address VARCHAR(200) NOT NULL COMMENT '详细地址',
postal_code CHAR(6) COMMENT '邮政编码'
```

## 索引设计规范

### 主键设计
```sql
-- 推荐：自增整型主键
id BIGINT PRIMARY KEY AUTO_INCREMENT

-- 备选：UUID 主键（分布式场景）
id CHAR(36) PRIMARY KEY DEFAULT (UUID())

-- 避免：业务字段作为主键
-- 不推荐：email 作为主键
```

### 外键设计
```sql
-- 外键约束
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,

-- 外键索引
INDEX idx_order_items_product_id (product_id),
INDEX idx_order_items_order_id (order_id)
```

### 复合索引设计
```sql
-- 查询频率高的字段组合
INDEX idx_products_category_status (category_id, status),
INDEX idx_orders_user_status_time (user_id, status, created_at),

-- 覆盖索引（包含查询所需的所有字段）
INDEX idx_products_list (category_id, status, name, price_cny)
```

## 数据约束规范

### 非空约束
```sql
-- 业务必需字段设置 NOT NULL
user_id BIGINT NOT NULL,
product_name VARCHAR(200) NOT NULL,
price_cny DECIMAL(10,2) NOT NULL,

-- 可选字段允许 NULL
description TEXT NULL,
deleted_at TIMESTAMP NULL
```

### 唯一约束
```sql
-- 单字段唯一
email VARCHAR(100) UNIQUE,
phone CHAR(11) UNIQUE,
sku VARCHAR(100) UNIQUE,

-- 复合唯一
UNIQUE KEY uk_user_product (user_id, product_id),
UNIQUE KEY uk_order_item (order_id, product_id)
```

### 检查约束
```sql
-- 数值范围检查
CHECK (price_cny >= 0),
CHECK (stock_quantity >= 0),
CHECK (discount_rate >= 0 AND discount_rate <= 1),

-- 枚举值检查
CHECK (status IN ('active', 'inactive', 'deleted')),
CHECK (gender IN ('M', 'F', 'U'))
```

## 分表分库策略

### 垂直拆分
```sql
-- 按业务模块拆分
user_db.users           -- 用户数据库
product_db.products     -- 商品数据库
order_db.orders         -- 订单数据库
```

### 水平拆分
```sql
-- 按用户ID分表
users_0, users_1, users_2, users_3  -- 用户分表

-- 按时间分表
orders_202501, orders_202502, orders_202503  -- 订单按月分表

-- 分表路由规则
table_suffix = user_id % 4              -- 用户表路由
table_suffix = DATE_FORMAT(created_at, '%Y%m')  -- 订单表路由
```

## 性能优化规范

### 查询优化
```sql
-- 避免 SELECT *
SELECT id, name, price_cny FROM products WHERE category_id = 1;

-- 使用 LIMIT 限制结果集
SELECT * FROM products ORDER BY created_at DESC LIMIT 20;

-- 使用合适的索引
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';
-- 需要索引：idx_orders_user_status (user_id, status)
```

### 写入优化
```sql
-- 批量插入
INSERT INTO products (name, price_cny, category_id) VALUES
('商品1', 99.99, 1),
('商品2', 199.99, 1),
('商品3', 299.99, 2);

-- 使用事务
START TRANSACTION;
INSERT INTO orders (...) VALUES (...);
INSERT INTO order_items (...) VALUES (...);
COMMIT;
```

## 数据迁移规范

### 版本管理
```python
# Alembic 迁移文件命名
2025_09_10_001_create_users_table.py
2025_09_10_002_add_phone_to_users.py
2025_09_10_003_create_products_table.py
```

### 迁移策略
```sql
-- 新增字段（向前兼容）
ALTER TABLE users ADD COLUMN phone CHAR(11) NULL;

-- 修改字段（需要数据迁移）
-- 1. 添加新字段
-- 2. 数据迁移
-- 3. 删除旧字段

-- 索引变更
CREATE INDEX idx_users_phone ON users(phone);
DROP INDEX idx_users_old_field;
```

### 回滚策略
```python
# Alembic 回滚操作
def downgrade():
    op.drop_column('users', 'phone')
    op.drop_index('idx_users_phone')
```

## 数据安全规范

### 敏感数据保护
```sql
-- 密码字段
password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值',

-- 加密字段
encrypted_data TEXT COMMENT 'AES加密数据',
encryption_key_id INT COMMENT '加密密钥ID',

-- 脱敏处理
phone_masked CHAR(11) GENERATED ALWAYS AS (
    CONCAT(LEFT(phone, 3), '****', RIGHT(phone, 4))
) STORED COMMENT '脱敏手机号'
```

### 审计日志
```sql
-- 操作日志表
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(50) NOT NULL COMMENT '表名',
    record_id BIGINT NOT NULL COMMENT '记录ID',
    operation ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL COMMENT '操作类型',
    old_values JSON COMMENT '变更前数据',
    new_values JSON COMMENT '变更后数据',
    user_id BIGINT COMMENT '操作用户ID',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间'
);
```
