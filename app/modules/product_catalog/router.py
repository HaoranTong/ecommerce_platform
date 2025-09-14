from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.modules.user_auth.models import User
from .models import Product, Category
from .schemas import ProductRead, ProductCreate, ProductUpdate, CategoryRead, CategoryCreate, CategoryUpdate
# V1.0 Mini-MVP: 导入认证依赖
from app.core.auth import get_current_admin_user

router = APIRouter()


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)  # V1.0: 管理员权限检查
):
    """创建新商品（需要管理员权限）"""
    # 检查SKU是否已存在
    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"商品SKU '{payload.sku}' 已存在"
        )
    
    # 如果指定了分类，检查分类是否存在
    if payload.category_id:
        category = db.query(Category).get(payload.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"分类ID {payload.category_id} 不存在"
            )
    
    # 创建商品
    product_data = payload.dict()
    product = Product(**product_data)
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


# ============ 分类管理API ============

@router.post("/categories", response_model=schemas.CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: schemas.CategoryCreate, 
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)
):
    """创建新分类（需要管理员权限）"""
    # 检查父分类是否存在
    if payload.parent_id:
        parent = db.query(models.Category).get(payload.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"父分类ID {payload.parent_id} 不存在"
            )
    
    # 检查同级分类名称是否重复
    existing = db.query(models.Category).filter(
        models.Category.name == payload.name,
        models.Category.parent_id == payload.parent_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"同级分类'{payload.name}'已存在"
        )
    
    category_data = payload.dict()
    category = models.Category(**category_data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories", response_model=List[schemas.CategoryRead])
def list_categories(
    parent_id: Optional[int] = Query(None, description="父分类ID，不传则返回顶级分类"),
    include_inactive: bool = Query(False, description="是否包含已停用的分类"),
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    query = db.query(models.Category)
    
    # 筛选父分类
    if parent_id is not None:
        query = query.filter(models.Category.parent_id == parent_id)
    else:
        # 默认只返回顶级分类
        query = query.filter(models.Category.parent_id.is_(None))
    
    # 是否包含已停用的分类
    if not include_inactive:
        query = query.filter(models.Category.is_active == True)
    
    # 按排序字段和创建时间排序
    categories = query.order_by(models.Category.sort_order, models.Category.created_at).all()
    return categories


@router.get("/categories/tree")
def get_category_tree(
    include_inactive: bool = Query(False, description="是否包含已停用的分类"),
    db: Session = Depends(get_db)
):
    """获取分类树结构"""
    # 获取所有分类
    query = db.query(models.Category)
    if not include_inactive:
        query = query.filter(models.Category.is_active == True)
    
    all_categories = query.order_by(models.Category.sort_order, models.Category.created_at).all()
    
    # 构建树结构
    def build_tree(parent_id=None):
        children = []
        for cat in all_categories:
            if cat.parent_id == parent_id:
                # 构建分类数据
                cat_data = {
                    "id": cat.id,
                    "name": cat.name,
                    "parent_id": cat.parent_id,
                    "sort_order": cat.sort_order,
                    "is_active": cat.is_active,
                    "created_at": cat.created_at,
                    "children": build_tree(cat.id)
                }
                children.append(cat_data)
        return children
    
    return build_tree()


@router.get("/categories/{category_id}", response_model=schemas.CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """获取指定分类信息"""
    category = db.query(models.Category).get(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    return category


@router.put("/categories/{category_id}", response_model=schemas.CategoryRead)
def update_category(
    category_id: int, 
    payload: schemas.CategoryUpdate, 
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)
):
    """更新分类信息（需要管理员权限）"""
    category = db.query(models.Category).get(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    
    # 检查父分类是否存在（如果有变更）
    if hasattr(payload, 'parent_id') and payload.parent_id:
        parent = db.query(models.Category).get(payload.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"父分类ID {payload.parent_id} 不存在"
            )
        
        # 防止将分类设为自己的子分类
        if payload.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能将分类设为自己的子分类"
            )
    
    # 检查同级分类名称是否重复（如果有名称变更）
    if hasattr(payload, 'name') and payload.name != category.name:
        existing = db.query(models.Category).filter(
            models.Category.name == payload.name,
            models.Category.parent_id == getattr(payload, 'parent_id', category.parent_id),
            models.Category.id != category_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"同级分类'{payload.name}'已存在"
            )
    
    # 更新分类
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)
):
    """删除分类（需要管理员权限）"""
    category = db.query(models.Category).get(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    
    # 检查是否有子分类
    children = db.query(models.Category).filter(
        models.Category.parent_id == category_id
    ).first()
    
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除含有子分类的分类，请先删除或移动子分类"
        )
    
    # 检查是否有关联的商品
    products = db.query(models.Product).filter(
        models.Product.category_id == category_id
    ).first()
    
    if products:
        # 软删除：设置状态为inactive而不是真正删除
        category.is_active = False
        db.commit()
    else:
        # 硬删除：没有关联数据时可以直接删除
        db.delete(category)
        db.commit()
    
    return None
