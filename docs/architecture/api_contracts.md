# API契约规范

## 🎯 设计原则

### 核心原则
1. **契约优先**: API设计先于代码实现
2. **版本化**: 所有API支持版本管理
3. **幂等性**: 写操作必须支持幂等
4. **一致性**: 统一的响应格式和错误处理
5. **文档化**: 自动生成和同步API文档

### RESTful 设计规范
- **资源导向**: URL表示资源，HTTP方法表示操作
- **状态码规范**: 严格遵循HTTP状态码语义
- **内容协商**: 支持JSON格式，预留扩展能力
- **分页标准**: 统一的分页参数和响应格式

## 📋 全局API规范

### 请求头规范
```yaml
# 必需请求头
required_headers:
  Content-Type: "application/json"
  Accept: "application/json"
  X-Request-ID: "UUID格式的请求追踪ID"
  
# 可选请求头
optional_headers:
  Authorization: "Bearer {JWT_TOKEN}"
  X-Client-Version: "客户端版本号"
  X-Platform: "web|mobile|admin"
  
# 幂等性支持
idempotency_headers:
  X-Idempotency-Key: "幂等键(写操作必需)"
```

### 响应格式规范
```yaml
# 成功响应格式
success_response:
  structure:
    data: "实际数据内容"
    meta: "元数据信息"
    timestamp: "响应时间戳"
    request_id: "请求追踪ID"

# 分页响应格式
paginated_response:
  structure:
    data: "数据数组"
    pagination:
      current_page: "当前页码"
      per_page: "每页条数"
      total: "总记录数"
      total_pages: "总页数"
      has_next: "是否有下一页"
      has_prev: "是否有上一页"

# 错误响应格式
error_response:
  structure:
    error:
      code: "错误代码"
      message: "错误信息"
      details: "详细信息"
      field_errors: "字段验证错误"
    timestamp: "错误时间戳"
    request_id: "请求追踪ID"
```

### 状态码规范
```yaml
status_codes:
  # 成功状态码
  200: "操作成功"
  201: "创建成功"
  204: "删除成功(无内容)"
  
  # 客户端错误
  400: "请求参数错误"
  401: "未认证"
  403: "权限不足"
  404: "资源不存在"
  409: "资源冲突"
  422: "数据验证失败"
  429: "请求频率限制"
  
  # 服务端错误
  500: "内部服务器错误"
  502: "网关错误"
  503: "服务不可用"
  504: "网关超时"
```

## 📚 模块API规范

### 用户认证API
```yaml
# 配置文件: config/apis/auth.yaml
auth_apis:
  base_path: "/api/auth"
  version: "v1"
  
  endpoints:
    register:
      method: "POST"
      path: "/register"
      summary: "用户注册"
      request_body:
        schema: "UserRegisterSchema"
        required: true
      responses:
        201:
          description: "注册成功"
          schema: "UserReadSchema"
        400:
          description: "注册失败"
          schema: "ErrorSchema"
      
    login:
      method: "POST"
      path: "/login"
      summary: "用户登录"
      request_body:
        schema: "UserLoginSchema"
        required: true
      responses:
        200:
          description: "登录成功"
          schema: "TokenSchema"
        401:
          description: "认证失败"
          schema: "ErrorSchema"
          
    refresh:
      method: "POST"
      path: "/refresh"
      summary: "刷新Token"
      headers:
        Authorization: "Bearer {refresh_token}"
      responses:
        200:
          description: "刷新成功"
          schema: "TokenSchema"
```

### 商品管理API
```yaml
# 配置文件: config/apis/products.yaml
product_apis:
  base_path: "/api/products"
  version: "v1"
  
  endpoints:
    create_product:
      method: "POST"
      path: "/"
      summary: "创建商品"
      security: ["BearerAuth"]
      headers:
        X-Idempotency-Key: "幂等键"
      request_body:
        schema: "ProductCreateSchema"
        required: true
      responses:
        201:
          description: "创建成功"
          schema: "ProductReadSchema"
        400:
          description: "创建失败"
          schema: "ErrorSchema"
          
    list_products:
      method: "GET"
      path: "/"
      summary: "获取商品列表"
      parameters:
        - name: "page"
          in: "query"
          type: "integer"
          default: 1
          description: "页码"
        - name: "per_page"
          in: "query"
          type: "integer"
          default: 20
          max: 100
          description: "每页条数"
        - name: "category_id"
          in: "query"
          type: "integer"
          description: "分类筛选"
        - name: "status"
          in: "query"
          type: "string"
          enum: ["active", "inactive", "out_of_stock"]
          description: "状态筛选"
        - name: "search"
          in: "query"
          type: "string"
          description: "搜索关键词"
      responses:
        200:
          description: "获取成功"
          schema: "ProductListSchema"
          
    get_product:
      method: "GET"
      path: "/{product_id}"
      summary: "获取商品详情"
      parameters:
        - name: "product_id"
          in: "path"
          type: "integer"
          required: true
      responses:
        200:
          description: "获取成功"
          schema: "ProductReadSchema"
        404:
          description: "商品不存在"
          schema: "ErrorSchema"
```

### 订单管理API
```yaml
# 配置文件: config/apis/orders.yaml
order_apis:
  base_path: "/api/orders"
  version: "v1"
  
  endpoints:
    create_order:
      method: "POST"
      path: "/"
      summary: "创建订单"
      security: ["BearerAuth"]
      headers:
        X-Idempotency-Key: "幂等键(必需)"
      request_body:
        schema: "OrderCreateSchema"
        required: true
      responses:
        201:
          description: "创建成功"
          schema: "OrderReadSchema"
        400:
          description: "创建失败"
          schema: "ErrorSchema"
          
    update_order_status:
      method: "PATCH"
      path: "/{order_id}/status"
      summary: "更新订单状态"
      security: ["BearerAuth"]
      parameters:
        - name: "order_id"
          in: "path"
          type: "integer"
          required: true
      request_body:
        schema: "OrderStatusUpdateSchema"
        required: true
      responses:
        200:
          description: "更新成功"
          schema: "OrderReadSchema"
        400:
          description: "状态转换非法"
          schema: "ErrorSchema"
```

## 🔄 API版本管理

### 版本策略
```yaml
versioning:
  strategy: "header"  # header | path | query
  header_name: "API-Version"
  default_version: "v1"
  supported_versions: ["v1", "v2"]
  
  # 版本兼容性
  compatibility:
    v1:
      deprecated: false
      sunset_date: null
    v2:
      deprecated: false
      sunset_date: null
      breaking_changes:
        - "用户ID改为UUID格式"
        - "订单状态枚举值变更"
```

### 版本迁移
```yaml
migration_guides:
  v1_to_v2:
    breaking_changes:
      user_id:
        old_format: "integer"
        new_format: "uuid"
        migration: "使用/api/v1/users/{id}/uuid获取UUID"
      order_status:
        old_values: ["pending", "paid", "shipped", "delivered"]
        new_values: ["created", "pending_payment", "paid", "processing", "shipped", "delivered"]
        mapping:
          pending: "pending_payment"
          paid: "paid"
          shipped: "shipped"
          delivered: "delivered"
```

## 🛡️ 安全规范

### 认证授权
```yaml
security:
  authentication:
    type: "Bearer"
    scheme: "JWT"
    header: "Authorization"
    
  authorization:
    type: "RBAC"  # Role-Based Access Control
    roles:
      - "user"      # 普通用户
      - "admin"     # 管理员
      - "operator"  # 运营人员
      
  rate_limiting:
    default: "100/minute"
    authenticated: "1000/minute"
    admin: "unlimited"
```

### 数据验证
```yaml
validation:
  request_size_limit: "10MB"
  file_upload_limit: "50MB"
  
  field_validation:
    email:
      pattern: "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$"
      max_length: 200
    phone:
      pattern: "^1[3-9]\\d{9}$"
      length: 11
    password:
      min_length: 6
      max_length: 128
      requirements: ["lowercase", "uppercase", "digit"]
```

## 🔧 配置驱动实现

### API配置加载器
```python
# app/core/api_config.py
import yaml
from pathlib import Path
from typing import Dict, List, Any

class APIConfigLoader:
    def __init__(self, config_dir: str = "config/apis"):
        self.config_dir = Path(config_dir)
        self._configs = {}
    
    def load_api_config(self, module_name: str) -> Dict[str, Any]:
        """加载API配置"""
        if module_name not in self._configs:
            config_file = self.config_dir / f"{module_name}.yaml"
            with open(config_file, 'r', encoding='utf-8') as f:
                self._configs[module_name] = yaml.safe_load(f)
        return self._configs[module_name]
    
    def get_endpoint_config(self, module_name: str, endpoint_name: str) -> Dict[str, Any]:
        """获取端点配置"""
        api_config = self.load_api_config(module_name)
        return api_config[f"{module_name}_apis"]["endpoints"][endpoint_name]
```

### 动态路由生成器
```python
# app/core/route_generator.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Callable

class DynamicRouteGenerator:
    def __init__(self, config_loader: APIConfigLoader):
        self.config_loader = config_loader
    
    def generate_router(self, module_name: str, handlers: Dict[str, Callable]) -> APIRouter:
        """根据配置生成FastAPI路由"""
        config = self.config_loader.load_api_config(module_name)
        api_config = config[f"{module_name}_apis"]
        
        router = APIRouter(prefix=api_config["base_path"])
        
        for endpoint_name, endpoint_config in api_config["endpoints"].items():
            if endpoint_name in handlers:
                self._add_route(router, endpoint_config, handlers[endpoint_name])
        
        return router
    
    def _add_route(self, router: APIRouter, config: Dict[str, Any], handler: Callable):
        """添加单个路由"""
        method = config["method"].lower()
        path = config["path"]
        
        # 生成路由装饰器参数
        route_kwargs = {
            "path": path,
            "methods": [config["method"]],
            "summary": config.get("summary"),
            "description": config.get("description"),
            "response_model": self._get_response_model(config),
            "status_code": self._get_status_code(config)
        }
        
        # 添加路由
        getattr(router, method)(path, **route_kwargs)(handler)
```

### 自动文档生成
```python
# app/core/doc_generator.py
from fastapi.openapi.utils import get_openapi

class APIDocumentationGenerator:
    def __init__(self, config_loader: APIConfigLoader):
        self.config_loader = config_loader
    
    def generate_openapi_spec(self, app_title: str, app_version: str) -> Dict[str, Any]:
        """生成OpenAPI规范"""
        # 基于配置文件生成完整的OpenAPI文档
        # 包含所有端点、模型、安全配置等
        pass
    
    def generate_postman_collection(self) -> Dict[str, Any]:
        """生成Postman测试集合"""
        # 基于配置文件生成Postman导入文件
        pass
```

## 📖 使用示例

### 在FastAPI应用中使用
```python
# app/main.py
from app.core.api_config import APIConfigLoader
from app.core.route_generator import DynamicRouteGenerator
from app.api import auth_handlers, product_handlers

# 初始化配置加载器
config_loader = APIConfigLoader()
route_generator = DynamicRouteGenerator(config_loader)

# 生成认证路由
auth_router = route_generator.generate_router("auth", {
    "register": auth_handlers.register,
    "login": auth_handlers.login,
    "refresh": auth_handlers.refresh_token
})

# 生成商品路由
product_router = route_generator.generate_router("products", {
    "create_product": product_handlers.create_product,
    "list_products": product_handlers.list_products,
    "get_product": product_handlers.get_product
})

# 注册路由
app.include_router(auth_router)
app.include_router(product_router)
```

## 🎯 优势总结

1. **配置驱动**: API定义与代码分离，易于维护
2. **版本管理**: 支持API版本演进和兼容性
3. **自动化**: 自动生成路由、文档和测试
4. **一致性**: 统一的API设计和响应格式
5. **可扩展**: 新增API只需配置文件
6. **测试友好**: 配置即测试合约
