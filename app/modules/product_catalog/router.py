"""
商品目录模块路由定义
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Any

from app.core.database import get_db
from app.modules.user_auth.models import User

from .dependencies import require_admin
from .models import SKU, Brand, Category, Product
from .repository import SKURepository, BrandRepository
from .category_service import CategoryService
from .service import ProductService
from .schemas import (BrandCreate, BrandRead, BrandUpdate, CategoryCreate,
                      CategoryRead, CategoryUpdate, ProductCreate, ProductRead,
                      ProductUpdate, SKUCreate, SKURead, SKUUpdate)

router = APIRouter()


# ============ 分类管理API ============


@router.post(
    "/product-catalog/categories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="创建新分类",
    description="创建新的商品分类，需要管理员权限"
)
async def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    admin: Any = Depends(require_admin),
):
    """创建新分类（需要管理员权限）"""
    return CategoryService.create_category(
        db,
        name=payload.name,
        description=payload.description,
        parent_id=payload.parent_id,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
        meta_data=getattr(payload, 'meta_data', None)
    )


@router.get(
    "/product-catalog/categories",
    response_model=List[CategoryRead],
    summary="获取分类列表",
    description="按条件查询分类列表，支持父分类过滤和激活状态过滤"
)
async def list_categories(
    parent_id: Optional[int] = Query(None, description="按父分类筛选"),
    is_active: Optional[bool] = Query(None, description="按状态筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
):
    """获取分类列表，调用 CategoryRepository"""
    return CategoryService.get_categories(db, parent_id, is_active, skip, limit)


# ============ 品牌管理API ============


@router.post(
    "/product-catalog/brands",
    response_model=BrandRead,
    status_code=status.HTTP_201_CREATED,
    summary="创建新品牌",
    description="创建新的品牌，需要管理员权限"
)
async def create_brand(
    payload: BrandCreate,
    db: Session = Depends(get_db),
    admin: Any = Depends(require_admin),
):
    """创建新品牌（需要管理员权限）"""
    brand = Brand(**payload.model_dump())
    try:
        return BrandRepository.create(db, brand)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"品牌创建失败: {e}")


@router.get(
    "/product-catalog/brands",
    response_model=List[BrandRead],
    summary="获取品牌列表",
    description="查询所有品牌，无需管理员权限"
)
async def list_brands(
    db: Session = Depends(get_db)
):
    """获取品牌列表"""
    return BrandRepository.list(db)


@router.get(
    "/product-catalog/brands/{brand_id}",
    response_model=BrandRead,
    summary="获取品牌详情",
    description="根据品牌ID获取品牌信息"
)
async def get_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """获取单个品牌详情"""
    brand = BrandRepository.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"品牌ID {brand_id} 不存在")
    return brand


@router.put(
    "/product-catalog/brands/{brand_id}",
    response_model=BrandRead,
    summary="更新品牌信息",
    description="根据品牌ID更新品牌信息，需要管理员权限"
)
async def update_brand(
    brand_id: int,
    payload: BrandUpdate,
    db: Session = Depends(get_db),
    admin: Any = Depends(require_admin)
):
    """更新品牌信息（需要管理员权限）"""
    brand = BrandRepository.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"品牌ID {brand_id} 不存在")
    data = payload.model_dump(exclude_unset=True)
    try:
        return BrandRepository.update(db, brand, data)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"品牌更新失败: {e}")


@router.delete(
    "/product-catalog/brands/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除品牌",
    description="软删除品牌，需要管理员权限"
)
async def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    admin: Any = Depends(require_admin)
):
    """软删除品牌（需要管理员权限）"""
    brand = BrandRepository.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"品牌ID {brand_id} 不存在")
    BrandRepository.soft_delete(db, brand)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============ 商品管理API ============


@router.post(
    "/product-catalog/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="创建新商品",
    description="创建新的商品，需要管理员权限"
)
async def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    admin: Any = Depends(require_admin),
):
    """创建新商品（需要管理员权限）"""
    return ProductService.create_product(
        db,
        name=payload.name,
        sku=payload.sku if hasattr(payload, 'sku') else None,
        price=payload.price if hasattr(payload, 'price') else None,
        category_id=payload.category_id,
        description=payload.description,
        stock_quantity=getattr(payload, 'stock_quantity', 0),
        image_url=getattr(payload, 'image_url', None)
    )


@router.get(
    "/product-catalog/products",
    response_model=List[ProductRead],
    summary="获取商品列表",
    description="按条件查询商品列表，支持搜索、分类、品牌和状态过滤"
)
async def list_products(
    search: Optional[str] = Query(None, description="搜索商品名称或描述"),
    category_id: Optional[int] = Query(None, description="按分类筛选"),
    brand_id: Optional[int] = Query(None, description="按品牌筛选"),
    status: Optional[str] = Query(
        None, description="按状态筛选（draft, published, archived）"
    ),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
):
    """获取商品列表，调用 ProductRepository"""
    return ProductService.get_products(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        status=status,
        search=search
    )


@router.get(
    "/product-catalog/products/{product_id}",
    response_model=ProductRead,
    summary="获取商品详情",
    description="根据商品ID获取商品详情，返回404当商品不存在"
)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取单个商品详情"""
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"商品ID {product_id} 不存在")
    return product


@router.put(
    "/product-catalog/products/{product_id}",
    response_model=ProductRead,
    summary="更新商品信息",
    description="根据商品ID更新商品信息，需要管理员权限"
)
async def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db),
        admin: Any = Depends(require_admin)):
    """更新商品信息（需要管理员权限）"""
    return ProductService.update_product(
        db,
        product_id,
        **payload.model_dump(exclude_unset=True)
    )


@router.delete(
    "/product-catalog/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除商品",
    description="软删除商品，需要管理员权限"
)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: Any = Depends(require_admin),
):
    """软删除指定商品（需管理员权限）"""
    ProductService.delete_product(db, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============ SKU管理API ============


@router.post(
    "/product-catalog/skus",
    response_model=SKURead,
    status_code=status.HTTP_201_CREATED,
    summary="创建SKU",
    description="创建SKU，需要管理员权限"
)
async def create_sku(
    payload: SKUCreate,
    db: Session = Depends(get_db),
    admin: Any = Depends(require_admin),
):
    """创建SKU（需要管理员权限）"""
    sku = SKU(**payload.model_dump())
    try:
        return SKURepository.create(db, sku)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"SKU创建失败: {e}")


@router.get(
    "/product-catalog/skus",
    response_model=List[SKURead]
)
async def list_skus(
    product_id: Optional[int] = Query(None, description="按商品ID过滤"),
    is_active: Optional[bool] = Query(None, description="按是否激活过滤"),
    db: Session = Depends(get_db),
):
    """获取SKU列表"""
    return SKURepository.list(db, product_id, is_active)


@router.get("/product-catalog/skus/{sku_id}", response_model=SKURead)
async def get_sku(sku_id: int, db: Session = Depends(get_db)):
    """获取单个SKU详情"""
    sku = SKURepository.get_by_id(db, sku_id)
    if not sku:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"SKU ID {sku_id} 不存在")
    return sku


@router.put("/product-catalog/skus/{sku_id}", response_model=SKURead)
async def update_sku(sku_id: int, payload: SKUUpdate, db: Session = Depends(get_db), admin: Any = Depends(require_admin)):
    """更新SKU信息"""
    sku = SKURepository.get_by_id(db, sku_id)
    if not sku:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"SKU ID {sku_id} 不存在")
    data = payload.model_dump(exclude_unset=True)
    try:
        return SKURepository.update(db, sku, data)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"SKU更新失败: {e}")


@router.delete("/product-catalog/skus/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sku(sku_id: int, db: Session = Depends(get_db), admin: Any = Depends(require_admin)):
    """软删除SKU"""
    sku = SKURepository.get_by_id(db, sku_id)
    if not sku:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"SKU ID {sku_id} 不存在")
    SKURepository.soft_delete(db, sku)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
