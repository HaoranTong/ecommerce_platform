### 
---

# 📄 前端技术架构说明书  
**项目**：农产品电商平台 - 管理后台（Admin Dashboard）  
**最后更新**：2025年10月21日  
**适用对象**：通义灵码 Agent / 前端开发人员  

---

## 1. 项目定位
- **类型**：企业级管理后台（Web SPA）
- **用户**：平台运营人员、管理员
- **核心目标**：高效管理商品、订单、会员、内容

---

## 2. 技术栈（强制使用）

| 类别            | 技术              | 版本要求  | 说明                                                         |
| --------------- | ----------------- | --------- | ------------------------------------------------------------ |
| **核心框架**    | Vue               | `^3.4.0`  | 必须使用 Composition API + `<script setup>`                  |
| **语言**        | TypeScript        | `^5.0.0`  | 严格类型检查，禁止 `any`                                     |
| **构建工具**    | Vite              | `^5.0.0`  | 开发服务器 + 构建                                            |
| **UI 库**       | Naive UI          | `^2.38.0` | **唯一 UI 库**，禁止引入 Element Plus 等                     |
| **路由**        | Vue Router        | `^4.0.0`  | 嵌套路由 + 动态导入                                          |
| **HTTP 客户端** | axios             | `^1.6.0`  | 已配置 baseURL 和拦截器                                      |
| **状态管理**    | 无                | —         | 简单状态用 `ref`/`reactive`，复杂场景再评估 Pinia（当前禁止） |
| **代码规范**    | ESLint + Prettier | —         | 遵循 [Vue 官方风格指南](https://vuejs.org/style-guide/)      |

---

## 3. 目录结构（绝对路径）

前端代码位于：  
`ecommerce_platform/app/frontend/`

```
app/frontend/
├── public/                     # 静态资源（不经过构建）
│   ├── favicon.ico
│   └── logo.png
├── src/
│   ├── assets/                 # 项目内静态资源（图片、字体等）
│   ├── components/             # 公共组件（非页面级）
│   │   └── layout/             # 布局组件（如 Sidebar.vue, Header.vue）
│   ├── composables/            # 可组合函数（如 useDebounce, useApi）
│   ├── shared/                 # **与小程序共享的代码**
│   │   └── api/                # **API 调用函数（关键！）**
│   │       ├── product.ts      # 商品相关 API
│   │       ├── order.ts        # 订单相关 API
│   │       └── member.ts       # 会员相关 API
│   ├── views/                  # **页面组件（路由级，每个文件对应一个路由）**
│   │   ├── Dashboard.vue
│   │   ├── ProductList.vue
│   │   └── OrderList.vue
│   ├── router/                 # 路由配置
│   │   └── index.ts            # 路由定义 + 创建函数
│   ├── App.vue                 # 根组件（包含 Layout）
│   └── main.ts                 # 应用入口
├── index.html                  # 单页应用 HTML 模板
├── vite.config.ts              # Vite 配置（含代理、别名）
├── tsconfig.json               # TypeScript 配置
├── eslint.config.js            # ESLint 配置
└── package.json                # 前端依赖
```

> 🔒 **关键约束**：
> - 所有 **API 调用函数** 必须放在 `src/shared/api/`（未来小程序项目将 symlink 此目录）
> - 所有 **页面** 必须放在 `src/views/`，文件名即路由名称（如 `ProductList.vue` → `/products`）
> - **禁止** 创建 `store/`、`utils/`（用 `composables/` 替代）、`services/`（用 `shared/api/`）

---

## 4. 开发规范

### 4.1 组件规范
- 使用 `<script setup>` 语法
- Props 必须定义类型
- 样式使用 scoped CSS 或 CSS Modules
- 禁止内联样式

### 4.2 API 调用规范
```ts
// src/shared/api/product.ts 示例
import axios from 'axios';

export interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  status: 'draft' | 'published' | 'archived';
}

export const getProducts = (params: { 
  search?: string; 
  page?: number; 
  limit?: number 
}) => {
  return axios.get<Product[]>('/product-catalog/products', { params });
};
```

### 4.3 路由规范
- 使用嵌套路由（Layout 作为父路由）
- 路径小写 + 连字符（如 `/product-list` → **错误**；`/products` → **正确**）

### 4.4 代理配置（开发环境）
```ts
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000', // FastAPI 地址
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

---

## 5. 与后端集成

- **Base URL**：`/api/v1`（由 axios 拦截器自动添加）
- **认证**：登录后，Token 存入 localStorage，所有请求自动携带 `Authorization: Bearer <token>`
- **API 文档**：以 `ecommerce_platform/docs/openapi.json` 为准

---

