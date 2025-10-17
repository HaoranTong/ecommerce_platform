"""
订单管理模块错误码定义

统一管理订单模块的错误类型常量，避免硬编码字符串
符合错误处理标准和代码质量规范

错误码命名规则：OM_<场景>_<错误类型>
- OM: Order Management 模块前缀
- 场景：USER, ORDER, PRODUCT, SKU, INVENTORY等
- 错误类型：NOT_FOUND, UNAVAILABLE, INVALID等
"""

# ============ 用户相关错误 ============
OM_USER_NOT_FOUND = "OM_USER_NOT_FOUND"  # 用户不存在

# ============ 订单相关错误 ============
OM_ORDER_NOT_FOUND = "OM_ORDER_NOT_FOUND"  # 订单不存在
OM_ORDER_ACCESS_DENIED = "OM_ORDER_ACCESS_DENIED"  # 订单访问权限不足
OM_ORDER_STATUS_INVALID = "OM_ORDER_STATUS_INVALID"  # 订单状态不合法
OM_ORDER_CANNOT_CANCEL = "OM_ORDER_CANNOT_CANCEL"  # 订单无法取消
OM_ORDER_CANNOT_PAY = "OM_ORDER_CANNOT_PAY"  # 订单无法支付
OM_ORDER_ALREADY_PAID = "OM_ORDER_ALREADY_PAID"  # 订单已支付

# ============ 商品相关错误 ============
OM_PRODUCT_NOT_FOUND = "OM_PRODUCT_NOT_FOUND"  # 商品不存在
OM_PRODUCT_UNAVAILABLE = "OM_PRODUCT_UNAVAILABLE"  # 商品不可购买

# ============ SKU相关错误 ============
OM_SKU_NOT_FOUND = "OM_SKU_NOT_FOUND"  # SKU不存在
OM_SKU_UNAVAILABLE = "OM_SKU_UNAVAILABLE"  # SKU不可购买

# ============ 库存相关错误 ============
OM_STOCK_INSUFFICIENT = "OM_STOCK_INSUFFICIENT"  # 库存不足
OM_STOCK_RESERVE_FAILED = "OM_STOCK_RESERVE_FAILED"  # 库存预占失败
OM_STOCK_RELEASE_FAILED = "OM_STOCK_RELEASE_FAILED"  # 库存释放失败
OM_STOCK_DEDUCT_FAILED = "OM_STOCK_DEDUCT_FAILED"  # 库存扣减失败

# ============ 系统错误 ============
OM_INTERNAL_ERROR = "OM_INTERNAL_ERROR"  # 内部错误
OM_DATABASE_ERROR = "OM_DATABASE_ERROR"  # 数据库错误
OM_VALIDATION_ERROR = "OM_VALIDATION_ERROR"  # 数据验证错误

# ============ 参数错误 ============
OM_INVALID_PARAMETER = "OM_INVALID_PARAMETER"  # 无效参数
OM_MISSING_PARAMETER = "OM_MISSING_PARAMETER"  # 缺少必需参数
