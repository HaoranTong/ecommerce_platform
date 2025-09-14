"""
文件名：product_service.py
文件路径：app/services/product_service.py
功能描述：商品管理相关的业务逻辑服务
主要功能：
- 商品的创建、查询、更新、删除
- 商品状态管理和库存更新
- 商品搜索和分类筛选
使用说明：
- 导入：from app.services.product_service import ProductService
- 在路由中调用：ProductService.create_product(product_data)
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from .models import Product, Category


class ProductService:
    """商品管理业务逻辑服务"""
    
    @staticmethod
    def create_product(db: Session, name: str, sku: str, price: float,
                      category_id: Optional[int] = None, description: Optional[str] = None,
                      stock_quantity: int = 0, image_url: Optional[str] = None) -> Product:
        """
        创建新商品
        
        Args:
            db: 数据库会话
            name: 商品名称
            sku: 商品SKU
            price: 商品价格
            category_id: 分类ID（可选）
            description: 商品描述（可选）
            stock_quantity: 库存数量
            image_url: 商品图片URL（可选）
            
        Returns:
            Product: 创建的商品对象
            
        Raises:
            HTTPException: SKU重复或分类不存在时抛出错误
        """
        # 检查SKU唯一性
        existing_product = db.query(Product).filter(Product.sku == sku).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="商品SKU已存在"
            )
        
        # 验证分类存在性
        if category_id:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="指定的分类不存在"
                )
        
        # 创建商品
        product = Product(
            name=name,
            sku=sku,
            price=price,
            category_id=category_id,
            description=description,
            stock_quantity=stock_quantity,
            image_url=image_url,
            status='active'
        )
        
        try:
            db.add(product)
            db.commit()
            db.refresh(product)
            return product
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="商品创建失败，数据冲突"
            )
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """
        根据ID获取商品
        
        Args:
            db: 数据库会话
            product_id: 商品ID
            
        Returns:
            Product: 商品对象或None
        """
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.id == product_id
        ).first()
    
    @staticmethod
    def get_products(db: Session, skip: int = 0, limit: int = 100,
                    category_id: Optional[int] = None, status: Optional[str] = None,
                    search: Optional[str] = None) -> List[Product]:
        """
        获取商品列表（支持筛选和搜索）
        
        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            category_id: 分类筛选
            status: 状态筛选
            search: 搜索关键词
            
        Returns:
            List[Product]: 商品列表
        """
        query = db.query(Product).options(joinedload(Product.category))
        
        # 应用筛选条件
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if status:
            query = query.filter(Product.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.like(search_term),
                    Product.sku.like(search_term),
                    Product.description.like(search_term)
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_product(db: Session, product_id: int, **kwargs) -> Optional[Product]:
        """
        更新商品信息
        
        Args:
            db: 数据库会话
            product_id: 商品ID
            **kwargs: 要更新的字段
            
        Returns:
            Product: 更新后的商品对象或None
            
        Raises:
            HTTPException: SKU冲突或分类不存在时抛出错误
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        # 检查SKU唯一性（如果要更新SKU）
        if 'sku' in kwargs and kwargs['sku'] != product.sku:
            existing = db.query(Product).filter(
                and_(Product.sku == kwargs['sku'], Product.id != product_id)
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SKU已被其他商品使用"
                )
        
        # 验证分类存在性（如果要更新分类）
        if 'category_id' in kwargs and kwargs['category_id']:
            category = db.query(Category).filter(Category.id == kwargs['category_id']).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="指定的分类不存在"
                )
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)
        
        try:
            db.commit()
            db.refresh(product)
            return product
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="商品更新失败，数据冲突"
            )
    
    @staticmethod
    def update_stock(db: Session, product_id: int, quantity_change: int) -> Optional[Product]:
        """
        更新商品库存
        
        Args:
            db: 数据库会话
            product_id: 商品ID
            quantity_change: 库存变化量（正数增加，负数减少）
            
        Returns:
            Product: 更新后的商品对象或None
            
        Raises:
            HTTPException: 库存不足时抛出错误
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="库存不足，无法完成操作"
            )
        
        product.stock_quantity = new_quantity
        
        # 根据库存状态自动更新商品状态
        if new_quantity == 0 and product.status == 'active':
            product.status = 'out_of_stock'
        elif new_quantity > 0 and product.status == 'out_of_stock':
            product.status = 'active'
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """
        删除商品（软删除：设置为inactive状态）
        
        Args:
            db: 数据库会话
            product_id: 商品ID
            
        Returns:
            bool: 删除成功返回True，商品不存在返回False
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        
        product.status = 'inactive'
        db.commit()
        return True
    
    @staticmethod
    def get_low_stock_products(db: Session, threshold: int = 10) -> List[Product]:
        """
        获取低库存商品列表
        
        Args:
            db: 数据库会话
            threshold: 库存阈值
            
        Returns:
            List[Product]: 低库存商品列表
        """
        return db.query(Product).filter(
            and_(
                Product.stock_quantity <= threshold,
                Product.status == 'active'
            )
        ).all()