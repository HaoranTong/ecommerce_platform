---
title: "product-catalog - API规范文档"
version: "1.0.0"
status: "draft"
created: "2025-10-06"
updated: "2025-10-06"
owner: "待填写"
dependencies:
  - "../../standards/document-management-standards.md"
  - "../../standards/api-standards.md"
  - "../../standards/naming-conventions-standards.md"
labels:
  - module: product-catalog
  - layer: L2
---

# product-catalog - API规范文档

## 依赖标准
- [文档管理标准](../../standards/document-management-standards.md)
- [应用架构](../../architecture/application-architecture.md)
- [API 标准](../../standards/api-standards.md)
- [命名规范标准](../../standards/naming-conventions-standards.md)

## 概述
本文档定义product-catalog模块的API接口规范，包括端点定义、请求响应格式和错误处理。

## 具体标准

### API设计标准
- 基础路径统一为 `/api/v1/product-catalog/`
- HTTP方法遵循REST语义：GET查询、POST创建、PUT更新、DELETE删除
- 认证使用JWT Bearer Token，权限控制基于角色
- 响应格式统一，错误码标准化
- 分页参数使用page和size，默认限制每页50条

## API端点定义

### 基础信息
- **模块名**: product-catalog
- **API前缀**: /api/v1/product-catalog/
- **认证**: JWT Bearer Token

### 端点列表

| 方法   | 路径                                      | 功能                                    | 请求参数                                                         | 响应模型           |
|--------|-------------------------------------------|-----------------------------------------|------------------------------------------------------------------|--------------------|
| GET    | /api/v1/product-catalog/products          | 查询商品列表                              | `search`、`category_id`、`brand_id`、`status`、`skip`、`limit`     | List[ProductRead]  |
| GET    | /api/v1/product-catalog/products/{id}     | 查询商品详情                              | `id`                                                             | ProductRead        |
| POST   | /api/v1/product-catalog/products          | 创建商品（需要管理员权限）                 | ProductCreate                                                  | ProductRead        |
| PUT    | /api/v1/product-catalog/products/{id}     | 更新商品（需要管理员权限）                 | `id`、ProductUpdate                                           | ProductRead        |
| DELETE | /api/v1/product-catalog/products/{id}     | 删除商品(软删除，需要管理员权限)           | `id`                                                             | 204 No Content     |
| GET    | /api/v1/product-catalog/categories        | 查询分类列表                              | `skip`、`limit`、`parent_id`、`is_active`                         | List[CategoryRead] |
| POST   | /api/v1/product-catalog/categories        | 创建分类（需要管理员权限）                 | CategoryCreate                                                 | CategoryRead       |
| GET    | /api/v1/product-catalog/brands            | 查询品牌列表                              | 无                                                               | List[BrandRead]    |
| POST   | /api/v1/product-catalog/brands            | 创建品牌（需要管理员权限）                 | BrandCreate                                                    | BrandRead          |
| GET    | /api/v1/product-catalog/skus              | 查询SKU列表                             | `product_id`、`is_active`                                         | List[SKURead]      |
| POST   | /api/v1/product-catalog/skus              | 创建SKU（需要管理员权限）                  | SKUCreate                                                       | SKURead            |
| DELETE | /api/v1/product-catalog/skus/{id}         | 删除SKU（软删除，需要管理员权限）           | `id`                                                             | 204 No Content     |

<!-- 其他端点同理，按需补充 -->

详细API规范请参考 [standards/openapi.yaml](../../standards/openapi.yaml)
