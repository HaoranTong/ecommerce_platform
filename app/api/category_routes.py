from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_session
import app.models as models
from app.api import schemas

router = APIRouter()


@router.post("/categories", response_model=schemas.CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_session)):
    """创建新分类"""
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
    db: Session = Depends(get_session)
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
    db: Session = Depends(get_session)
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
def get_category(category_id: int, db: Session = Depends(get_session)):
    """获取单个分类详情"""
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
    db: Session = Depends(get_session)
):
    """更新分类信息"""
    category = db.query(models.Category).get(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    
    update_data = payload.dict(exclude_unset=True)
    
    # 检查父分类
    if 'parent_id' in update_data:
        if update_data['parent_id'] == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类不能设置自己为父分类"
            )
        
        if update_data['parent_id']:
            parent = db.query(models.Category).get(update_data['parent_id'])
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"父分类ID {update_data['parent_id']} 不存在"
                )
            
            # 检查是否会形成循环引用
            def check_circular_reference(parent_id, target_id):
                if parent_id == target_id:
                    return True
                parent_cat = db.query(models.Category).get(parent_id)
                if parent_cat and parent_cat.parent_id:
                    return check_circular_reference(parent_cat.parent_id, target_id)
                return False
            
            if check_circular_reference(update_data['parent_id'], category_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能设置该父分类，会形成循环引用"
                )
    
    # 检查同级分类名称冲突
    if 'name' in update_data:
        parent_id = update_data.get('parent_id', category.parent_id)
        existing = db.query(models.Category).filter(
            models.Category.name == update_data['name'],
            models.Category.parent_id == parent_id,
            models.Category.id != category_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"同级分类'{update_data['name']}'已存在"
            )
    
    # 更新字段
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_session)):
    """删除分类"""
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
            detail="该分类下还有子分类，无法删除"
        )
    
    # 检查是否有关联的商品
    products = db.query(models.Product).filter(
        models.Product.category_id == category_id
    ).first()
    
    if products:
        # 软删除：设置为不可用
        category.is_active = False
        db.commit()
    else:
        # 硬删除：没有关联数据时直接删除
        db.delete(category)
        db.commit()
    
    return None
