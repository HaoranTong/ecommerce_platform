"""
文件名：product.py
文件路径：app/api/routes/product.py
功能描述：商品和分类管理相关的API路由定义
主要功能：
- 商品CRUD操作（创建、查询、更新、删除）
- 商品分类管理
- 商品搜索、筛选和排序
- 商品库存管理
- 商品统计和批量操作
使用说明：
- 路由前缀：/api/v1/products
- 认证要求：商品管理需要管理员权限
- 权限控制：商品浏览对游客开放，管理需要权限
依赖模块：
- app.services.ProductService: 商品业务逻辑服务
- app.schemas.product: 商品相关输入输出模式
- app.auth: 管理员权限验证
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductRead, ProductSearch,
    CategoryCreate, CategoryUpdate, CategoryRead,
    ProductStats, ProductPublic
)
from app.services import ProductService
from app.auth import get_current_admin_user

router = APIRouter(prefix="/products", tags=["商品管理"])


# === 商品相关路由 ===

@router.get("", response_model=List[ProductRead])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    is_active: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("created_at", regex="^(name|price|created_at|updated_at)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    获取商品列表
    
    - 支持分页、搜索、筛选和排序
    - 对所有用户开放（包括游客）
    - 可按分类、价格范围、状态筛选
    """
    products = ProductService.get_products(
        db=db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return products


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取商品详情
    
    - 对所有用户开放
    - 返回完整商品信息
    """
    product = ProductService.get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    创建商品
    
    - 需要管理员权限
    - 验证分类存在性
    - 自动设置创建时间
    """
    try:
        product = ProductService.create_product(
            db=db,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category_id=product_data.category_id,
            stock_quantity=product_data.stock_quantity,
            sku=product_data.sku,
            is_active=product_data.is_active
        )
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="商品创建失败")


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    更新商品信息
    
    - 需要管理员权限
    - 支持部分字段更新
    """
    product = ProductService.update_product(
        db=db,
        product_id=product_id,
        name=product_update.name,
        description=product_update.description,
        price=product_update.price,
        category_id=product_update.category_id,
        stock_quantity=product_update.stock_quantity,
        is_active=product_update.is_active
    )
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    删除商品
    
    - 需要管理员权限
    - 软删除商品
    """
    success = ProductService.delete_product(db=db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="商品不存在")
    return None


@router.post("/search", response_model=List[ProductRead])
def search_products(
    search_data: ProductSearch,
    db: Session = Depends(get_db)
):
    """
    商品高级搜索
    
    - 支持复杂搜索条件
    - 全文搜索商品名称和描述
    """
    products = ProductService.search_products(
        db=db,
        query=search_data.query,
        category_ids=search_data.category_ids,
        price_range=search_data.price_range,
        tags=search_data.tags,
        skip=search_data.skip,
        limit=search_data.limit
    )
    return products


@router.put("/{product_id}/stock", response_model=ProductRead)
def update_stock(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    更新商品库存
    
    - 需要管理员权限
    - 可增加或减少库存
    """
    product = ProductService.update_stock(
        db=db,
        product_id=product_id,
        quantity=quantity
    )
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


# === 分类相关路由 ===

@router.get("/categories", response_model=List[CategoryRead])
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    parent_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取商品分类列表
    
    - 对所有用户开放
    - 支持层级分类查询
    """
    categories = ProductService.get_categories(
        db=db,
        skip=skip,
        limit=limit,
        parent_id=parent_id,
        is_active=is_active
    )
    return categories


@router.get("/categories/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取分类详情
    
    - 对所有用户开放
    """
    category = ProductService.get_category_by_id(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    创建商品分类
    
    - 需要管理员权限
    - 支持多级分类
    """
    try:
        category = ProductService.create_category(
            db=db,
            name=category_data.name,
            description=category_data.description,
            parent_id=category_data.parent_id,
            is_active=category_data.is_active
        )
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="分类创建失败")


@router.put("/categories/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    更新商品分类
    
    - 需要管理员权限
    """
    category = ProductService.update_category(
        db=db,
        category_id=category_id,
        name=category_update.name,
        description=category_update.description,
        parent_id=category_update.parent_id,
        is_active=category_update.is_active
    )
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    删除商品分类
    
    - 需要管理员权限
    - 检查是否有子分类或商品
    """
    success = ProductService.delete_category(db=db, category_id=category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在或包含商品")
    return None


@router.get("/stats/overview", response_model=ProductStats)
def get_product_stats(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    获取商品统计信息
    
    - 需要管理员权限
    - 返回商品数量、分类、库存等统计
    """
    stats = ProductService.get_product_statistics(db=db)
    return stats