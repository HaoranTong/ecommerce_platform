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
from .repository import CategoryRepository, ProductRepository, SKURepository  # add imports
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
    try:
        category_data = payload.model_dump()
        category = Category(**category_data)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分类创建失败: {str(e)}",
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
    categories = CategoryRepository.list(db, parent_id, is_active, skip, limit)
    return categories


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
        _: Any = Depends(require_admin),
):
    """创建新品牌（需要管理员权限）"""
    try:
        brand_data = payload.model_dump()
        brand = Brand(**brand_data)
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"品牌创建失败: {str(e)}",
        )


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
    product = Product(**payload.model_dump())
    try:
        return ProductRepository.create(db, product)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"商品创建失败: {str(e)}",
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
    filters = {"search": search, "category_id": category_id, "status": status}
    return ProductRepository.list(db, skip=skip, limit=limit, **filters)


@router.get(
    "/product-catalog/products/{product_id}",
    response_model=ProductRead,
    summary="获取商品详情",
    description="根据商品ID获取商品详情，返回404当商品不存在"
)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取单个商品详情"""
    product = ProductRepository.get_by_id(db, product_id)
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
    product = ProductRepository.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"商品ID {product_id} 不存在")
    data = payload.model_dump(exclude_unset=True)
    try:
        return ProductRepository.update(db, product, data)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"商品更新失败: {e}")


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
    product = ProductRepository.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"商品ID {product_id} 不存在")
    ProductRepository.soft_delete(db, product)
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
    data = payload.model
