# 【占位文件】批次溯源模块路由
# 对应文档：docs/modules/batch-traceability/api-spec.md

from fastapi import APIRouter

router = APIRouter(prefix="/api/batch-traceability", tags=["批次溯源"])

# 待实现API端点