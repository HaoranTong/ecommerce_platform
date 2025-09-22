# 库存管理模块API实现文档

<!--
文件名：api-implementation.md
文件路径：docs/modules/inventory-management/api-implementation.md
文档类型：API实现文档
模块名称：库存管理模块 (Inventory Management Module)
文档版本：v1.0.0
创建时间：2025-09-15
最后修改：2025-09-15
维护人员：API开发工程师
文档状态：正式版本

文档用途：
- 详细描述库存管理模块的API端点实现
- 提供完整的请求/响应示例和错误处理
- 指导前端开发和第三方集成

相关文档：
- API规范：api-spec.md
- 系统设计文档：design.md
- 实现指南：implementation.md
-->

## 1. API概述

### 1.1 API设计原则
- **RESTful设计**: 遵循REST API设计规范
- **资源导向**: 以库存资源为中心进行接口设计
- **无状态**: API调用之间相互独立，无状态依赖
- **幂等性**: 相同的请求产生相同的结果
- **版本控制**: 支持API版本向后兼容

### 1.2 基础信息
- **Base URL**: `{host}/api/v1/inventory`
- **认证方式**: Bearer Token (JWT)
- **响应格式**: JSON
- **字符编码**: UTF-8
- **时间格式**: ISO 8601 (UTC)

### 1.3 通用响应结构

```json
{
    "success": true,
    "data": {...},
    "message": "操作成功",
    "timestamp": "2025-09-15T10:30:00Z",
    "request_id": "req_123456789"
}
```

#### 错误响应结构
```json
{
    "success": false,
    "error": {
        "code": "INV_002",
        "message": "库存不足",
        "details": {
            "sku_id": "SKU-001",
            "requested": 100,
            "available": 50
        }
    },
    "timestamp": "2025-09-15T10:30:00Z",
    "request_id": "req_123456789"
}
```

## 2. 库存查询接口

### 2.1 获取单个SKU库存

**接口信息**
- **URL**: `GET /api/v1/inventory/sku/{sku_id}`
- **权限**: `inventory:read`
- **限流**: 1000次/分钟

**路径参数**
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| sku_id | string | 是 | SKU标识符，1-100字符 |

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| include_history | boolean | 否 | false | 是否包含库存历史 |

**响应示例**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "sku_id": "SKU-001",
        "total_quantity": 1000,
        "available_quantity": 750,
        "reserved_quantity": 250,
        "warning_threshold": 100,
        "critical_threshold": 50,
        "is_low_stock": false,
        "is_critical_stock": false,
        "is_out_of_stock": false,
        "is_active": true,
        "last_updated": "2025-09-15T08:30:00Z",
        "history": [
            {
                "id": "tx_001",
                "transaction_type": "deduct",
                "quantity_change": -50,
                "quantity_before": 800,
                "quantity_after": 750,
                "reason": "订单扣减",
                "created_at": "2025-09-15T08:25:00Z"
            }
        ]
    }
}
```

**实现代码**
```python
@router.get("/sku/{sku_id}", response_model=InventoryDetailResponse)
async def get_sku_inventory(
    sku_id: str = Path(..., min_length=1, max_length=100, description="SKU标识符"),
    include_history: bool = Query(False, description="是否包含库存历史"),
    service: InventoryService = Depends(get_inventory_service),
    current_user = Depends(get_current_user)
):
    """
    获取SKU库存详细信息
    
    - **sku_id**: SKU标识符
    - **include_history**: 是否返回库存变更历史记录
    """
    # 权限检查
    require_permission(current_user, Permission.INVENTORY_READ)
    
    try:
        inventory = await service.get_sku_inventory_detailed(
            sku_id=sku_id,
            include_history=include_history
        )
        
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "INV_001",
                    "message": f"SKU {sku_id} 的库存记录不存在"
                }
            )
        
        return create_success_response(inventory)
        
    except InventoryServiceError as e:
        logger.error(f"获取库存失败: {str(e)}", extra={
            "sku_id": sku_id,
            "user_id": current_user.id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INV_006",
                "message": "库存查询失败"
            }
        )
```

### 2.2 批量获取库存

**接口信息**
- **URL**: `POST /api/v1/inventory/batch`
- **权限**: `inventory:read`
- **限流**: 100次/分钟

**请求体**
```json
{
    "sku_ids": ["SKU-001", "SKU-002", "SKU-003"],
    "include_unavailable": false
}
```

**请求参数**
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| sku_ids | array[string] | 是 | SKU ID列表，最多100个 |
| include_unavailable | boolean | 否 | 是否包含无库存记录的SKU |

**响应示例**
```json
{
    "success": true,
    "data": {
        "inventories": [
            {
                "sku_id": "SKU-001",
                "available_quantity": 750,
                "reserved_quantity": 250,
                "total_quantity": 1000,
                "is_low_stock": false,
                "is_out_of_stock": false
            },
            {
                "sku_id": "SKU-002",
                "available_quantity": 0,
                "reserved_quantity": 0,
                "total_quantity": 0,
                "is_low_stock": false,
                "is_out_of_stock": true
            }
        ],
        "not_found": ["SKU-003"],
        "total_requested": 3,
        "total_found": 2
    }
}
```

## 3. 库存预占接口

### 3.1 创建库存预占

**接口信息**
- **URL**: `POST /api/v1/inventory/reserve`
- **权限**: `inventory:update`
- **限流**: 500次/分钟

**请求体**
```json
{
    "reservation_type": "cart",
    "reference_id": "cart_12345",
    "items": [
        {
            "sku_id": "SKU-001",
            "quantity": 2
        },
        {
            "sku_id": "SKU-002", 
            "quantity": 1
        }
    ],
    "expires_minutes": 120,
    "idempotency_key": "idem_key_12345"
}
```

**请求参数验证**
```python
class ReservationRequest(BaseModel):
    reservation_type: ReservationType = Field(..., description="预占类型")
    reference_id: str = Field(..., min_length=1, max_length=100, description="业务关联ID")
    items: List[ReservationItem] = Field(..., min_items=1, max_items=50, description="预占商品列表")
    expires_minutes: int = Field(default=120, ge=5, le=1440, description="预占有效期(分钟)")
    idempotency_key: Optional[str] = Field(None, description="幂等性键")
    
    @validator('items')
    def validate_unique_skus(cls, v):
        """验证SKU不重复"""
        sku_ids = [item.sku_id for item in v]
        if len(sku_ids) != len(set(sku_ids)):
            raise ValueError("同一次预占中SKU不能重复")
        return v

class ReservationItem(BaseModel):
    sku_id: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0, le=10000, description="预占数量")
```

**响应示例**
```json
{
    "success": true,
    "data": {
        "reservation_id": "rsv_550e8400e29b41d4a716446655440000",
        "reference_id": "cart_12345",
        "expires_at": "2025-09-15T12:30:00Z",
        "status": "active",
        "reserved_items": [
            {
                "sku_id": "SKU-001",
                "reserved_quantity": 2,
                "available_before": 752,
                "available_after": 750
            },
            {
                "sku_id": "SKU-002",
                "reserved_quantity": 1,
                "available_before": 101,
                "available_after": 100
            }
        ],
        "total_items": 2,
        "total_reserved": 3
    }
}
```

**实现代码**
```python
@router.post("/reserve", response_model=ReservationResponse)
async def reserve_inventory(
    request: ReservationRequest,
    service: InventoryService = Depends(get_inventory_service),
    current_user = Depends(get_current_user),
    idempotency_service: IdempotencyService = Depends(get_idempotency_service)
):
    """
    预占库存
    
    支持购物车和订单场景的库存预占，确保库存在指定时间内为用户保留。
    """
    # 权限检查
    require_permission(current_user, Permission.INVENTORY_UPDATE)
    
    # 幂等性检查
    if request.idempotency_key:
        existing_result = await idempotency_service.get_result(
            key=request.idempotency_key,
            user_id=current_user.id
        )
        if existing_result:
            return existing_result

    try:
        # 输入验证
        await validate_sku_existence(service, [item.sku_id for item in request.items])
        
        # 执行预占
        result = await service.reserve_inventory(
            reservation_type=request.reservation_type,
            reference_id=request.reference_id,
            items=[item.dict() for item in request.items],
            expires_minutes=request.expires_minutes,
            user_id=current_user.id
        )
        
        # 记录审计日志
        await InventoryAuditLogger.log_reservation_event(
            event_type="create_reservation",
            reservation_id=result["reservation_id"],
            items=request.items,
            user_id=current_user.id,
            expires_at=result["expires_at"]
        )
        
        response = create_success_response(result)
        
        # 保存幂等性结果
        if request.idempotency_key:
            await idempotency_service.save_result(
                key=request.idempotency_key,
                user_id=current_user.id,
                result=response
            )
        
        return response
        
    except InsufficientInventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INV_002",
                "message": "库存不足",
                "details": {
                    "insufficient_items": e.insufficient_items
                }
            }
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "INV_005",
                "message": "参数验证失败",
                "details": e.errors()
            }
        )
```

### 3.2 释放库存预占

**接口信息**
- **URL**: `DELETE /api/v1/inventory/reserve/{reservation_id}`
- **权限**: `inventory:update`
- **限流**: 500次/分钟

**路径参数**
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| reservation_id | string | 是 | 预占ID |

**响应示例**
```json
{
    "success": true,
    "data": {
        "reservation_id": "rsv_550e8400e29b41d4a716446655440000",
        "status": "released",
        "released_items": [
            {
                "sku_id": "SKU-001",
                "released_quantity": 2,
                "available_before": 750,
                "available_after": 752
            }
        ],
        "total_released": 2,
        "released_at": "2025-09-15T10:45:00Z"
    }
}
```

## 4. 库存扣减接口

### 4.1 执行库存扣减

**接口信息**
- **URL**: `POST /api/v1/inventory/deduct`
- **权限**: `inventory:update`
- **限流**: 200次/分钟

**请求体**
```json
{
    "order_id": "order_12345",
    "items": [
        {
            "sku_id": "SKU-001",
            "quantity": 2,
            "reservation_id": "rsv_550e8400e29b41d4a716446655440000"
        },
        {
            "sku_id": "SKU-002",
            "quantity": 1
        }
    ],
    "operator_type": "system",
    "reason": "订单确认扣减"
}
```

**实现代码**
```python
@router.post("/deduct", response_model=DeductionResponse)
async def deduct_inventory(
    request: DeductionRequest,
    service: InventoryService = Depends(get_inventory_service),
    current_user = Depends(get_current_user)
):
    """
    扣减库存（实际出库）
    
    用于订单确认后的实际库存扣减，支持从预占库存或可用库存中扣减。
    """
    require_permission(current_user, Permission.INVENTORY_UPDATE)
    
    try:
        # 参数验证
        await validate_deduction_request(service, request)
        
        # 执行扣减
        result = await service.deduct_inventory(
            order_id=request.order_id,
            items=[item.dict() for item in request.items],
            operator_id=current_user.id,
            reason=request.reason
        )
        
        # 记录审计日志
        await InventoryAuditLogger.log_inventory_operation(
            operation="deduct_inventory",
            order_id=request.order_id,
            items=request.items,
            user_id=current_user.id,
            reason=request.reason
        )
        
        return create_success_response(result)
        
    except InsufficientInventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INV_002",
                "message": f"库存扣减失败: {str(e)}"
            }
        )
    except ReservationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "INV_007",
                "message": f"预占记录不存在: {str(e)}"
            }
        )
```

## 5. 库存管理接口

### 5.1 创建SKU库存

**接口信息**
- **URL**: `POST /api/v1/inventory/create`
- **权限**: `inventory:create`
- **限流**: 50次/分钟

**请求体**
```json
{
    "sku_id": "SKU-NEW-001",
    "initial_quantity": 1000,
    "warning_threshold": 100,
    "critical_threshold": 50,
    "reason": "新商品上架"
}
```

**响应示例**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "sku_id": "SKU-NEW-001",
        "total_quantity": 1000,
        "available_quantity": 1000,
        "reserved_quantity": 0,
        "warning_threshold": 100,
        "critical_threshold": 50,
        "is_active": true,
        "created_at": "2025-09-15T10:30:00Z"
    }
}
```

### 5.2 调整库存数量

**接口信息**
- **URL**: `PATCH /api/v1/inventory/sku/{sku_id}/adjust`
- **权限**: `inventory:admin`
- **限流**: 50次/分钟

**请求体**
```json
{
    "adjustment_type": "increase",
    "quantity": 500,
    "reason": "采购入库",
    "reference_id": "purchase_order_123"
}
```

### 5.3 更新库存阈值

**接口信息**
- **URL**: `PATCH /api/v1/inventory/sku/{sku_id}/thresholds`
- **权限**: `inventory:update`
- **限流**: 100次/分钟

**请求体**
```json
{
    "warning_threshold": 200,
    "critical_threshold": 100,
    "reason": "调整预警策略"
}
```

## 6. 库存查询和报表接口

### 6.1 获取低库存商品

**接口信息**
- **URL**: `GET /api/v1/inventory/low-stock`
- **权限**: `inventory:read`
- **限流**: 100次/分钟

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| warning_only | boolean | 否 | false | 只返回预警级别的低库存 |
| critical_only | boolean | 否 | false | 只返回紧急级别的低库存 |
| category | string | 否 | | 商品类别筛选 |
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量，最大100 |

**响应示例**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "sku_id": "SKU-LOW-001",
                "available_quantity": 45,
                "warning_threshold": 100,
                "critical_threshold": 50,
                "is_critical_stock": true,
                "category": "electronics"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 15,
            "total_pages": 1
        },
        "summary": {
            "total_low_stock": 15,
            "critical_count": 8,
            "warning_count": 7
        }
    }
}
```

### 6.2 获取库存变更历史

**接口信息**
- **URL**: `GET /api/v1/inventory/sku/{sku_id}/transactions`
- **权限**: `inventory:read`
- **限流**: 100次/分钟

**查询参数**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| start_date | string | 否 | | 开始日期 (ISO 8601) |
| end_date | string | 否 | | 结束日期 (ISO 8601) |
| transaction_type | string | 否 | | 事务类型筛选 |
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 50 | 每页数量，最大100 |

## 7. 错误处理和状态码

### 7.1 HTTP状态码

| 状态码 | 描述 | 使用场景 |
|--------|------|----------|
| 200 | 成功 | 查询、更新操作成功 |
| 201 | 创建成功 | 创建新库存记录 |
| 400 | 请求错误 | 库存不足、参数错误 |
| 401 | 未授权 | 缺少或无效的认证信息 |
| 403 | 权限不足 | 用户权限不够 |
| 404 | 资源不存在 | SKU或预占记录不存在 |
| 409 | 冲突 | 并发操作冲突 |
| 422 | 参数验证失败 | 请求体格式错误 |
| 429 | 请求过多 | 触发限流 |
| 500 | 服务器错误 | 内部系统错误 |

### 7.2 业务错误码

| 错误码 | HTTP状态码 | 描述 | 解决方案 |
|--------|------------|------|----------|
| INV_001 | 404 | SKU库存记录不存在 | 检查SKU ID或创建库存记录 |
| INV_002 | 400 | 库存数量不足 | 减少请求数量或等待补货 |
| INV_003 | 400 | 预占已过期 | 重新发起预占请求 |
| INV_004 | 409 | 并发操作冲突 | 重试操作 |
| INV_005 | 422 | 参数验证失败 | 检查请求参数格式和值 |
| INV_006 | 500 | 数据库操作失败 | 联系系统管理员 |
| INV_007 | 404 | 预占记录不存在 | 检查预占ID有效性 |
| INV_008 | 400 | 重复操作 | 检查幂等性键或操作历史 |

### 7.3 全局异常处理

```python
@app.exception_handler(InsufficientInventoryError)
async def insufficient_inventory_handler(request: Request, exc: InsufficientInventoryError):
    return JSONResponse(
        status_code=400,
        content={
            "success": false,
            "error": {
                "code": "INV_002",
                "message": str(exc),
                "details": {
                    "sku_id": exc.sku_id,
                    "requested": exc.requested,
                    "available": exc.available
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": str(uuid.uuid4())
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": false,
            "error": {
                "code": "INV_005",
                "message": "参数验证失败",
                "details": exc.errors()
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": str(uuid.uuid4())
        }
    )
```

## 8. API安全和限流

### 8.1 认证和授权

```python
# JWT Token验证
async def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

# 权限检查装饰器
def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(verify_jwt_token), **kwargs):
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error_code": "AUTH_003",
                        "message": "权限不足"
                    }
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

### 8.2 API限流

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 应用限流
@router.get("/sku/{sku_id}")
@limiter.limit("1000/minute")
async def get_sku_inventory(request: Request, sku_id: str):
    # 接口逻辑
    pass

@router.post("/reserve")
@limiter.limit("500/minute")  
async def reserve_inventory(request: Request, ...):
    # 接口逻辑
    pass
```

### 8.3 幂等性处理

```python
class IdempotencyService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 86400  # 24小时
        
    async def get_result(self, key: str, user_id: int) -> Optional[dict]:
        """获取幂等性结果"""
        cache_key = f"idempotency:{user_id}:{key}"
        result = await self.redis.get(cache_key)
        if result:
            return json.loads(result)
        return None
    
    async def save_result(self, key: str, user_id: int, result: dict):
        """保存幂等性结果"""
        cache_key = f"idempotency:{user_id}:{key}"
        await self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps(result, default=str)
        )
```

## 9. 性能优化

### 9.1 响应时间优化

- **数据库连接池**: 合理配置连接池大小
- **查询优化**: 使用索引、避免N+1查询
- **缓存策略**: Redis缓存热点数据
- **并发控制**: 合理使用锁机制

### 9.2 批量操作优化

```python
@router.post("/batch/reserve")
@limiter.limit("50/minute")
async def batch_reserve_inventory(
    request: BatchReservationRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """批量预占库存 - 性能优化版本"""
    
    # 按SKU分组，减少数据库查询
    sku_groups = defaultdict(list)
    for item in request.items:
        sku_groups[item.sku_id].append(item)
    
    # 批量查询库存
    sku_ids = list(sku_groups.keys())
    inventories = await service.batch_get_inventory(sku_ids)
    
    # 并行处理预占
    tasks = []
    for sku_id, items in sku_groups.items():
        if sku_id in inventories:
            task = service.reserve_sku_inventory(
                sku_id, 
                sum(item.quantity for item in items),
                request.reference_id
            )
            tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return process_batch_results(results)
```

---

**文档版本**: v1.0  
**创建日期**: 2025-09-15  
**最后更新**: 2025-09-15  
**责任人**: API开发工程师  
**审核人**: 技术负责人