from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
import app.data_models as models
from app.api import schemas
# V1.0 Mini-MVP: 导入认证依赖
from app.auth import get_current_admin_user

router = APIRouter()


@router.post("/products", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)  # V1.0: 管理员权限检查
):
    """创建新商品（需要管理员权限）"""
    # 检查SKU是否已存在
    existing = db.query(models.Product).filter(models.Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"商品SKU '{payload.sku}' 已存在"
        )
    
    # 如果指定了分类，检查分类是否存在
    if payload.category_id:
        category = db.query(models.Category).get(payload.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"分类ID {payload.category_id} 不存在"
            )
    
    # 创建商品
    product_data = payload.dict()
    product = models.Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products", response_model=List[schemas.ProductRead])
def list_products(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    category_id: Optional[int] = Query(None, description="按分类筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    search: Optional[str] = Query(None, description="搜索商品名称或SKU"),
    db: Session = Depends(get_db)
):
    """获取商品列表，支持分页和筛选"""
    query = db.query(models.Product)
    
    # 筛选条件
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if status:
        query = query.filter(models.Product.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.Product.name.like(search_term)) | 
            (models.Product.sku.like(search_term))
        )
    
    # 分页
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取单个商品详情"""
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"商品ID {product_id} 不存在"
        )
    return product


@router.put("/products/{product_id}", response_model=schemas.ProductRead)
def update_product(
    product_id: int, 
    payload: schemas.ProductUpdate, 
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)  # V1.0: 管理员权限检查
):
    """更新商品信息（需要管理员权限）"""
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商品ID {product_id} 不存在"
        )
    
    # 检查SKU冲突（如果更新了SKU）
    update_data = payload.dict(exclude_unset=True)
    if 'sku' in update_data and update_data['sku'] != product.sku:
        existing = db.query(models.Product).filter(
            models.Product.sku == update_data['sku'],
            models.Product.id != product_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品SKU '{update_data['sku']}' 已存在"
            )
    
    # 检查分类存在性
    if 'category_id' in update_data and update_data['category_id']:
        category = db.query(models.Category).get(update_data['category_id'])
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"分类ID {update_data['category_id']} 不存在"
            )
    
    # 更新字段
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.patch("/products/{product_id}/stock", response_model=schemas.ProductRead)
def update_product_stock(
    product_id: int,
    stock_update: schemas.ProductStockUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)  # V1.0: 管理员权限检查
):
    """更新商品库存（需要管理员权限）"""
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商品ID {product_id} 不存在"
        )
    
    new_stock = product.stock_quantity + stock_update.quantity_change
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存不能为负数"
        )
    
    product.stock_quantity = new_stock
    
    # 根据库存自动更新状态
    if new_stock == 0 and product.status == 'active':
        product.status = 'out_of_stock'
    elif new_stock > 0 and product.status == 'out_of_stock':
        product.status = 'active'
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)  # V1.0: 管理员权限检查
):
    """删除商品（需要管理员权限，软删除）"""
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商品ID {product_id} 不存在"
        )
    
    # 检查是否有关联的订单项
    order_items = db.query(models.OrderItem).filter(
        models.OrderItem.product_id == product_id
    ).first()
    
    if order_items:
        # 软删除：设置状态为inactive而不是真正删除
        product.status = 'inactive'
        db.commit()
    else:
        # 硬删除：没有关联数据时可以直接删除
        db.delete(product)
        db.commit()
    
    return None
