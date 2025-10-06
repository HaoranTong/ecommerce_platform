"""
商品目录模块数据访问层（Repository）
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from .models import Category, Product, Brand, SKU, ProductAttribute, SKUAttribute, ProductImage, ProductTag


class CategoryRepository:
    """分类数据访问"""

    @staticmethod
    def create(db: Session, category: Category) -> Category:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def list(
        db: Session,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        query = db.query(Category)
        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        else:
            query = query.filter(Category.parent_id.is_(None))
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        return query.order_by(Category.sort_order, Category.name).offset(skip).limit(limit).all()

    @staticmethod
    def count_products(db: Session, category_id: int) -> int:
        return db.query(Product).filter(Product.category_id == category_id).count()
