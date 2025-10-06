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
 
class BrandRepository:
    """品牌数据访问"""
    @staticmethod
    def create(db: Session, brand: Brand) -> Brand:
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand

    @staticmethod
    def get_by_id(db: Session, brand_id: int) -> Optional[Brand]:
        return db.query(Brand).filter(Brand.id == brand_id).first()

    @staticmethod
    def list(db: Session) -> List[Brand]:
        return db.query(Brand).all()

    @staticmethod
    def update(db: Session, brand: Brand, data: Dict[str, Any]) -> Brand:
        for k, v in data.items():
            setattr(brand, k, v)
        db.commit()
        db.refresh(brand)
        return brand

    @staticmethod
    def soft_delete(db: Session, brand: Brand) -> None:
        # Perform soft delete if is_active field exists
        if hasattr(brand, 'is_active'):
            brand.is_active = False
        db.commit()


class ProductRepository:
    """商品数据访问"""

    @staticmethod
    def create(db: Session, product: Product) -> Product:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id, Product.is_deleted == False).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Product]:
        query = db.query(Product).filter(Product.is_deleted == False)
        if filters.get('category_id') is not None:
            query = query.filter(Product.category_id == filters['category_id'])
        if filters.get('status') is not None:
            query = query.filter(Product.status == filters['status'])
        if filters.get('search'):
            term = f"%{filters['search']}%"
            query = query.filter((Product.name.like(term)) | (Product.description.like(term)))
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, product: Product, data: Dict[str, Any]) -> Product:
        for k, v in data.items():
            setattr(product, k, v)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def soft_delete(db: Session, product: Product) -> None:
        product.is_deleted = True
        db.commit()


class SKURepository:
    """SKU数据访问"""

    @staticmethod
    def create(db: Session, sku: SKU) -> SKU:
        db.add(sku)
        db.commit()
        db.refresh(sku)
        return sku

    @staticmethod
    def get_by_id(db: Session, sku_id: int) -> Optional[SKU]:
        return db.query(SKU).filter(SKU.id == sku_id).first()

    @staticmethod
    def list(db: Session, product_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[SKU]:
        query = db.query(SKU)
        if product_id is not None:
            query = query.filter(SKU.product_id == product_id)
        if is_active is not None:
            query = query.filter(SKU.is_active == is_active)
        return query.all()

    @staticmethod
    def update(db: Session, sku: SKU, data: Dict[str, Any]) -> SKU:
        for k, v in data.items():
            setattr(sku, k, v)
        db.commit()
        db.refresh(sku)
        return sku

    @staticmethod
    def soft_delete(db: Session, sku: SKU) -> None:
        sku.is_active = False
        db.commit()
