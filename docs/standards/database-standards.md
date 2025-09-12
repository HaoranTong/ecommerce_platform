# 数据库设计规范

此文档定义数据库表、字段、关系的命名和设计标准。

## 表命名规范

### 基础规则
- 使用复数形式：`users`, `products`, `orders`
- 小写字母+下划线：`order_items`, `user_profiles`
- 避免缩写，使用完整单词

### 关联表命名
- 多对多关系：`user_roles`, `product_categories`
- 中间表：按字母顺序排列实体名

## 字段命名规范

### 主键字段
- 统一使用：`id` (BIGINT AUTO_INCREMENT)
- 类型：BIGINT，支持大数据量

### 外键字段  
- 格式：`{表名}_id`
- 示例：`user_id`, `product_id`, `order_id`

### 通用字段
- 创建时间：`created_at` (TIMESTAMP)
- 更新时间：`updated_at` (TIMESTAMP)  
- 软删除：`deleted_at` (TIMESTAMP NULL)
- 状态字段：`status` (VARCHAR 或 ENUM)

### 业务字段
- 数量字段：`quantity`, `amount`
- 金额字段：`price`, `total_amount` (DECIMAL)
- 描述字段：`description`, `note`
- 名称字段：`name`, `title`

## 数据类型标准

### 字符串类型
- 短文本：`VARCHAR(255)`
- 长文本：`TEXT`
- 固定长度：`CHAR(n)`

### 数值类型  
- 整数：`INT`, `BIGINT`
- 金额：`DECIMAL(10,2)`
- 百分比：`DECIMAL(5,2)`

### 时间类型
- 时间戳：`TIMESTAMP` (默认值 CURRENT_TIMESTAMP)
- 日期：`DATE`
- 时间：`TIME`

## 索引规范

### 命名规则
- 主键：`PRIMARY`
- 唯一索引：`uk_{表名}_{字段名}` 
- 普通索引：`idx_{表名}_{字段名}` 或 `idx_{表名}_{字段1}_{字段2}`
- 外键索引：`fk_{表名}_{外键字段名}`
- 复合索引：`idx_{表名}_{字段1}_{字段2}_{字段3}`

### 索引命名示例
```sql
-- 唯一索引
uk_users_email          -- users表的email唯一索引
uk_products_sku         -- products表的sku唯一索引

-- 普通索引  
idx_orders_user_id      -- orders表的user_id索引
idx_orders_status       -- orders表的status索引
idx_orders_user_status  -- orders表的user_id+status复合索引
idx_payments_status_created -- payments表的status+created_at复合索引

-- 外键索引
fk_orders_user_id       -- orders表指向users表的外键索引
fk_order_items_product_id -- order_items表指向products表的外键索引
```

### 创建原则
- 外键字段必须有索引
- 经常查询的字段添加索引
- 联合索引按选择性排序

## 关系设计

### 外键约束
- 使用 `ON DELETE CASCADE` 或 `ON DELETE SET NULL`
- 根据业务需求选择删除策略

### 关系类型
- 一对一：使用外键关联
- 一对多：在"多"的一方添加外键
- 多对多：使用中间表

## 迁移文件规范

### 文件命名
- 格式：`{时间戳}_{操作描述}.py`
- 操作描述使用下划线分隔的英文

### 迁移内容
- 每个迁移文件只做一类操作
- 提供 upgrade 和 downgrade 方法
- 添加详细的注释说明

## 示例

### 标准表结构
```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    category_id BIGINT,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);
```

## 禁止行为

- 使用中文字段名
- 不加索引的外键字段
- 不一致的命名模式
- 缺少时间戳字段