好的！以下是为您量身定制的两份文档：

---

# 文档一：农产品电商平台前端架构设计方案（AI 友好版）

> **适用对象**：Qwen3-Codex / 通义灵码等 AI 编码模型  
> **目标**：AI 阅读后可直接生成符合规范的前端代码  
> **原则**：结构清晰、命名明确、无过度抽象、路径固定、技术栈锁定  
> **项目规模**：小型（<100 商品，低并发），单人 + AI 开发，未来可平滑扩展

---

## 1. 项目基本信息

| 项目     | 值                                                   |
| -------- | ---------------------------------------------------- |
| 项目名称 | ecommerce_platform                                   |
| 业务类型 | 农产品电商（B2C + 代理分销）                         |
| 用户端   | 消费者小程序、代理小程序                             |
| 管理端   | Web 管理后台                                         |
| 开发者   | 产品经理 + AI（无手动编码）                          |
| 部署方式 | 小程序发布至微信，后台部署至 Vercel / 阿里云静态托管 |

---

## 2. 技术栈锁定（AI 必须严格遵守）

| 模块             | 技术选型                         | 版本要求 | 说明                                                         |
| ---------------- | -------------------------------- | -------- | ------------------------------------------------------------ |
| **核心语言**     | TypeScript                       | ≥5.0     | 所有文件必须为 `.ts` 或 `.vue`（含 `<script lang="ts">`）    |
| **管理后台框架** | Vue 3                            | ≥3.4     | 使用 Composition API                                         |
| **管理后台 UI**  | Naive UI                         | ≥2.38    | 仅使用官方文档组件                                           |
| **小程序框架**   | Taro 4                           | ≥4.0     | 使用 Vue 3 语法                                              |
| **小程序 UI**    | NutUI React（Taro 版）           | ≥2.0     | **注意**：Taro 4 中 NutUI 以 React 形式提供，但支持 Vue 3 项目（通过适配层）<br>若 AI 不确定，可改用 **Taro UI 官方 Vue 组件** 或 **自定义简单样式** |
| **状态管理**     | Pinia                            | ≥2.1     | 每个功能一个 store 文件                                      |
| **HTTP 客户端**  | axios                            | ≥1.6     | 封装在 `src/api/` 下                                         |
| **构建工具**     | Vite（后台）、Taro CLI（小程序） | 默认     | 不修改构建配置                                               |

> ✅ **AI 注意**：  
> - 不得引入未列出的技术（如 zod、unocss、tailwind、vuex 等）  
> - 若需 UI 组件，优先使用 Naive UI（后台）或 NutUI/Taro UI（小程序）

---

## 3. 目录结构规范（AI 必须严格遵循路径）

```bash
frontend/
├── src/
│   ├── api/                     # 【API 层】所有后端接口调用
│   │   ├── product.ts           # 商品相关 API
│   │   ├── order.ts             # 订单相关 API
│   │   ├── user.ts              # 用户/登录相关 API
│   │   └── distribution.ts      # 分销相关 API
│   │
│   ├── types/                   # 【类型定义】手写 TypeScript 接口
│   │   └── index.ts             # 所有接口在此定义，例如：
│   │                            # export interface Product { id: number; name: string; price: number; stock: number; geo?: string; }
│   │
│   ├── stores/                  # 【状态管理】Pinia store
│   │   ├── productStore.ts      # 商品状态（如购物车、筛选条件）
│   │   ├── userStore.ts         # 用户登录状态
│   │   └── orderStore.ts        # 订单状态
│   │
│   ├── views/                   # 【页面层】所有页面组件
│   │   ├── admin/               # 管理后台页面（Vue 3 + Naive UI）
│   │   │   ├── ProductList.vue
│   │   │   ├── OrderList.vue
│   │   │   └── UserManage.vue
│   │   │
│   │   ├── consumer/            # 消费者小程序页面（Taro + Vue 3）
│   │   │   ├── ProductList.vue
│   │   │   ├── ProductDetail.vue
│   │   │   └── MyOrder.vue
│   │   │
│   │   └── agent/               # 代理小程序页面（与 consumer 高度相似）
│   │       ├── ProductList.vue
│   │       ├── MyCustomers.vue
│   │       └── Commission.vue
│   │
│   ├── components/              # 【复用组件】仅放真正跨端/跨页面复用的组件
│   │   └── GeoBadge.vue         # 地理标志徽章（后台和小程序都用）
│   │
│   ├── utils/                   # 【工具函数】纯函数，无副作用
│   │   ├── formatPrice.ts       # 格式化价格：export const formatPrice = (price: number): string => `¥${price.toFixed(2)}`
│   │   └── getTenantId.ts       # 租户识别（当前返回 'default'）
│   │
│   └── App.vue                  # 小程序入口组件（Taro 项目）
│
├── main.ts                      # 管理后台入口（Vite 项目）
├── taro.config.js               # Taro 小程序配置（使用默认模板）
├── vite.config.ts               # Vite 后台配置（使用默认模板）
└── package.json                 # 依赖按技术栈锁定版本
```

> ✅ **AI 生成规则**：
> - 新功能必须在对应目录下新建文件，**不得修改现有文件结构**
> - 页面文件名必须为 **PascalCase**（如 `ProductList.vue`）
> - 所有 `import` 路径必须为 **相对路径**（如 `../api/product`）

---

## 4. 代码风格与规范（AI 必须遵守）

### 4.1 Vue 组件结构（Composition API）

```vue
<!-- 示例：src/views/admin/ProductList.vue -->
<template>
  <n-data-table :columns="columns" :data="products" />
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { fetchProducts } from '@/api/product'
import type { Product } from '@/types'

const products = ref<Product[]>([])

onMounted(async () => {
  products.value = await fetchProducts()
})

const columns = [
  { title: '商品名', key: 'name' },
  { title: '价格', key: 'price' }
]
</script>
```

### 4.2 API 函数规范

```ts
// src/api/product.ts
import axios from 'axios'
import type { Product } from '@/types'

const BASE_URL = 'https://api.your-agri-platform.com'

export const fetchProducts = async (): Promise<Product[]> => {
  const res = await axios.get(`${BASE_URL}/products`)
  return res.data
}

export const updateProduct = async (id: number, data: Partial<Product>): Promise<Product> => {
  const res = await axios.put(`${BASE_URL}/products/${id}`, data)
  return res.data
}
```

### 4.3 类型定义规范

```ts
// src/types/index.ts
export interface Product {
  id: number
  name: string
  price: number
  stock: number
  geo?: string // 地理标志，可选
}

export interface Order {
  id: string
  productId: number
  quantity: number
  status: 'pending' | 'paid' | 'shipped'
}
```

---

## 5. 扩展性设计（未来升级无需重构）

| 未来需求             | 当前预留方式                            | AI 升级指令示例                                              |
| -------------------- | --------------------------------------- | ------------------------------------------------------------ |
| 支持多租户           | `utils/getTenantId.ts` 返回 `'default'` | “修改 getTenantId.ts，从 URL 参数 `?tenant=xxx` 读取租户 ID” |
| 增加新模块（如售后） | 在 `views/` 下新建目录                  | “在 views/admin/ 下创建 AfterSales.vue，使用 Naive UI 表格”  |
| 小程序增加新页面     | 在 `views/consumer/` 下新建 `.vue`      | “生成消费者端的商品评价页面 ProductReview.vue”               |
| 需要运行时校验       | 在 API 函数中预留注释                   | “在 fetchProducts 中加入 zod 校验，使用 ProductSchema”       |

> ✅ **关键**：所有扩展都是 **新增文件** 或 **修改单个文件**，不涉及架构调整。

---

## 6. 禁止事项（AI 不得执行）

- ❌ 不得创建 `packages/`、`domains/`、`core/` 等分层目录  
- ❌ 不得使用 Vuex、Redux、Mobx 等非 Pinia 状态管理  
- ❌ 不得引入 CSS-in-JS、Tailwind、UnoCSS 等样式方案  
- ❌ 不得修改 `vite.config.ts` 或 `taro.config.js`（除非明确要求）  
- ❌ 不得在组件中写业务逻辑（逻辑必须放在 `api/` 或 `stores/`）

---

# 文档二：VSCode + 通义灵码（Qwen3-Codex）操作指导

> **目标**：让您通过自然语言指令，高效驱动 AI 生成符合上述架构的代码

---

## 1. 前置准备

### 1.1 安装必要工具
- VSCode（最新版）
- 通义灵码插件（[官方安装指南](https://tongyi.aliyun.com/lingma/docs)）
- Node.js ≥18.0
- npm / pnpm

### 1.2 初始化项目
在终端执行：
```bash
# 创建项目目录
mkdir agri-ecom-frontend && cd agri-ecom-frontend

# 初始化（AI 会根据 package.json 安装依赖）
echo '{
  "name": "agri-ecom-frontend",
  "private": true,
  "scripts": {
    "dev:admin": "vite",
    "build:admin": "vite build",
    "dev:mini": "taro build --type weapp --watch",
    "build:mini": "taro build --type weapp"
  }
}' > package.json

# 安装依赖（按架构文档）
npm install vue@^3.4 naive-ui axios pinia
npm install -D vite @vitejs/plugin-vue
npm install @tarojs/cli @tarojs/taro @tarojs/vue3 nutui-react
```

### 1.3 创建基础目录
按 **文档一** 的目录结构，在 VSCode 中手动创建空文件夹（如 `src/api/`, `src/views/admin/` 等）

---

## 2. 使用通义灵码 Agent 生成代码

### 2.1 启动 Agent 模式
1. 在 VSCode 中打开项目根目录
2. 按 `Ctrl+Shift+P`（Windows）或 `Cmd+Shift+P`（Mac）
3. 输入 `通义灵码：启动 Agent`
4. 选择 **Qwen3-Codex** 模型

### 2.2 标准指令模板（推荐复制使用）

> ✅ **通用格式**：  
> “根据项目架构文档，在 `[路径]` 下生成 `[功能描述]`，使用 `[技术]`，包含 `[要素]`”

#### 示例 1：生成商品类型定义
```text
根据项目架构文档，在 src/types/index.ts 中定义 Product 接口，包含 id（number）、name（string）、price（number）、stock（number）、geo（可选 string）
```

#### 示例 2：生成管理后台商品列表页
```text
根据项目架构文档，在 src/views/admin/ProductList.vue 中生成商品管理页面，使用 Naive UI 的 n-data-table 展示商品列表，调用 src/api/product.ts 的 fetchProducts API，列包括：商品名、价格、库存、地理标志徽章（使用 GeoBadge 组件）
```

#### 示例 3：生成小程序商品详情页
```text
根据项目架构文档，在 src/views/consumer/ProductDetail.vue 中生成商品详情页面，使用 Taro View 和 Text 组件，显示商品名称、价格（用 formatPrice 工具函数格式化）、库存，并有一个“加入购物车”按钮（暂不实现逻辑）
```

### 2.3 关键技巧

| 场景             | 指令技巧                                                     |
| ---------------- | ------------------------------------------------------------ |
| **复用已有代码** | “参考 src/views/admin/ProductList.vue 的结构，生成 OrderList.vue” |
| **修复 AI 错误** | “刚才生成的 ProductList.vue 中，API 路径错了，应为 '@/api/product'，请修正” |
| **追加功能**     | “在 ProductList.vue 的表格中增加一列‘操作’，包含编辑和删除按钮” |
| **生成工具函数** | “在 src/utils/formatPrice.ts 中导出 formatPrice 函数，接收 number，返回 '¥xx.xx' 字符串” |

---

## 3. 验证与调试建议

1. **先生成小功能**：如先生成 `types/index.ts`，再生成 `api/product.ts`，最后生成页面
2. **运行检查**：
   - 后台：`npm run dev:admin` → 访问 `http://localhost:5173`
   - 小程序：`npm run dev:mini` → 用微信开发者工具打开 `dist/weapp`
3. **错误处理**：
   - 若 AI 生成代码报错，复制错误信息 + “请根据错误修正 XXX.vue”
   - 若路径错误，明确指定完整路径（如 `src/views/agent/MyCustomers.vue`）

---

## 4. 后续维护流程

1. **新增功能** → 用标准指令让 AI 生成新文件  
2. **修改功能** → 在对应文件中右键 → “通义灵码：解释代码” → “通义灵码：优化此代码”  
3. **升级架构** → 仅当业务复杂度显著增加时，再考虑引入 domains/ 等分层（目前不需要）

---

> 💡 **记住**：您是“AI 指挥官”，只需描述 **做什么** 和 **在哪做**，AI 负责 **怎么做**。

如需我为您生成完整的 `package.json`、`vite.config.ts` 或第一个页面代码，请随时告知！