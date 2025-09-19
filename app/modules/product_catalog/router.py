"""
商品目录模块路由定义
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.modules.user_auth.models import User
from .models import Product, Category, Brand, SKU
from .schemas import (
    ProductRead, ProductCreate, ProductUpdate,
    CategoryRead, CategoryCreate, CategoryUpdate,
    BrandRead, BrandCreate, BrandUpdate,
    SKURead, SKUCreate, SKUUpdate,
)
from app.core.auth import get_current_admin_user

router = APIRouter()


# ============ 分类管理API ============

@router.post("/product-catalog/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
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
            detail=f"分类创建失败: {str(e)}"
        )


@router.get("/product-catalog/categories", response_model=List[CategoryRead])
async def list_categories(
    parent_id: Optional[int] = Query(None, description="按父分类筛选"),
    is_active: Optional[bool] = Query(None, description="按状态筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """获取分类列表，支持分页和筛选"""
    query = db.query(Category)
    
    # 筛选条件
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    
    # 分页
    categories = query.offset(skip).limit(limit).all()
    return categories


# ============ 品牌管理API ============

@router.post("/product-catalog/brands", response_model=BrandRead, status_code=status.HTTP_201_CREATED)
async def create_brand(
    payload: BrandCreate, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
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
            detail=f"品牌创建失败: {str(e)}"
        )


# ============ 商品管理API ============

@router.post("/product-catalog/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """创建新商品（需要管理员权限）"""
    try:
        product_data = payload.model_dump()
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"商品创建失败: {str(e)}"
        )


@router.get("/product-catalog/products", response_model=List[ProductRead])
async def list_products(
    search: Optional[str] = Query(None, description="搜索商品名称或描述"),
    category_id: Optional[int] = Query(None, description="按分类筛选"),
    brand_id: Optional[int] = Query(None, description="按品牌筛选"),
    status: Optional[str] = Query(None, description="按状态筛选（draft, published, archived）"),
    db: Session = Depends(get_db)
):
    """获取商品列表，支持分页和筛选"""
    query = db.query(Product).filter(Product.is_deleted == False)
    
    if search:
        query = query.filter(
            (Product.name.contains(search)) | 
            (Product.description.contains(search))
        )
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if brand_id is not None:
        query = query.filter(Product.brand_id == brand_id)
    if status is not None:
        query = query.filter(Product.status == status)
    
    products = query.all()
    return products


@router.get("/product-catalog/products/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取单个商品详情"""
    product = db.query(Product).filter(
        Product.id == product_id, 
        Product.is_deleted == False
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商品ID {product_id} 不存在"
        )
    return product


@router.put("/product-catalog/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """更新商品信息（需要管理员权限）"""
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商品ID {product_id} 不存在"
        )
    
    try:
        update_data = payload.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"商品更新失败: {str(e)}"
        )


@router.delete("/product-catalog/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """删除商品（需要管理员权限，软删除）"""
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商品ID {product_id} 不存在"
        )
    
    try:
        product.soft_delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"商品删除失败: {str(e)}"
        )


# ============ SKU管理API ============

@router.post("/product-catalog/skus", response_model=SKURead, status_code=status.HTTP_201_CREATED)
async def create_sku(
    payload: SKUCreate, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """创建新SKU（需要管理员权限）"""
    # 验证产品是否存在
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"产品ID {payload.product_id} 不存在"
        )
    
    # 检查SKU码是否重复
    existing_sku = db.query(SKU).filter(SKU.sku_code == payload.sku_code).first()
    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SKU码 {payload.sku_code} 已存在"
        )
    
    try:
        sku_data = payload.dict(exclude={'attributes'})
        sku = SKU(**sku_data)
        db.add(sku)
        db.commit()
        db.refresh(sku)
        return sku
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SKU创建失败: {str(e)}"
        )


@router.get("/product-catalog/skus", response_model=List[SKURead])
async def list_skus(
    search: Optional[str] = Query(None, description="搜索SKU名称或编码"),
    product_id: Optional[int] = Query(None, description="按产品ID筛选"),
    is_active: Optional[bool] = Query(None, description="按状态筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="限制记录数"),
    db: Session = Depends(get_db)
):
    """获取SKU列表"""
    query = db.query(SKU)
    
    if search:
        query = query.filter(
            (SKU.name.contains(search)) | 
            (SKU.sku_code.contains(search))
        )
    if product_id:
        query = query.filter(SKU.product_id == product_id)
    if is_active is not None:
        query = query.filter(SKU.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/product-catalog/skus/{sku_id}", response_model=SKURead)
async def get_sku(
    sku_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取SKU详情"""
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU ID {sku_id} 不存在"
        )
    return sku


@router.put("/product-catalog/skus/{sku_id}", response_model=SKURead)
async def update_sku(
    sku_id: int,
    payload: SKUUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """更新SKU（需要管理员权限）"""
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU ID {sku_id} 不存在"
        )
    
    try:
        update_data = payload.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sku, field, value)
        db.commit()
        db.refresh(sku)
        return sku
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SKU更新失败: {str(e)}"
        )


@router.delete("/product-catalog/skus/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sku(
    sku_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """删除SKU（需要管理员权限）"""
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU ID {sku_id} 不存在"
        )
    
    try:
        db.delete(sku)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SKU删除失败: {str(e)}"
        )


# ============ 产品关联的SKU API（兼容旧接口）============

@router.post("/product-catalog/products/{product_id}/skus", response_model=SKURead, status_code=status.HTTP_201_CREATED)
async def create_product_sku(
    product_id: int,
    payload: dict,  # 使用dict来兼容测试中的数据格式
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """为特定产品创建SKU（兼容接口）"""
    # 验证产品是否存在
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"产品ID {product_id} 不存在"
        )
    
    # 检查SKU码是否重复（如果提供了）
    if 'sku_code' in payload:
        existing_sku = db.query(SKU).filter(SKU.sku_code == payload['sku_code']).first()
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SKU码 {payload['sku_code']} 已存在"
            )
    
    try:
        # 转换payload到SKU字段格式
        sku_data = {
            'product_id': product_id,
            'sku_code': payload.get('sku_code', f"SKU-{product_id}-{int(__import__('time').time())}"),
            'name': payload.get('name'),
            'price': float(payload.get('price', 0)),
            'cost_price': payload.get('cost_price'),
            'market_price': payload.get('market_price'), 
            'weight': payload.get('weight'),
            'volume': payload.get('volume'),
            'is_active': payload.get('is_active', True)
        }
        
        sku = SKU(**sku_data)
        db.add(sku)
        db.commit()
        db.refresh(sku)
        return sku
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SKU创建失败: {str(e)}"
        )
