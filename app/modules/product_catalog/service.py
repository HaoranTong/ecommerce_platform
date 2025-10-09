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

from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .models import Category, Product, Brand, SKU
from .repository import BrandRepository, SKURepository, ProductRepository, CategoryRepository


class ProductService:
    """
    商品管理业务逻辑服务
    
    职责：
    - 商品业务逻辑处理和流程编排
    - 事务边界控制（commit/rollback）
    - 业务规则验证
    - 跨Repository协调
    
    架构原则：
    - Service层通过Repository访问数据，禁止直接使用db.query()
    - Service层负责事务管理（commit/rollback）
    - Repository层只负责数据访问（add/flush/refresh）
    """

    @staticmethod
    def create_product(
        db: Session,
        name: str,
        description: Optional[str] = None,
        brand_id: Optional[int] = None,
        category_id: Optional[int] = None,
        status: str = "published",
        seo_title: Optional[str] = None,
        seo_description: Optional[str] = None,
        seo_keywords: Optional[str] = None,
        sort_order: int = 1,
    ) -> Product:
        """
        创建新商品（SPU）
        
        业务流程：
        1. 验证品牌和分类存在性
        2. 创建商品实体
        3. 通过Repository持久化
        4. Service层管理事务提交

        Args:
            db: 数据库会话
            name: 商品名称
            description: 商品描述（可选）
            brand_id: 品牌ID（可选）
            category_id: 分类ID（可选）
            status: 商品状态（draft, published, archived）
            seo_title: SEO标题（可选）
            seo_description: SEO描述（可选）
            seo_keywords: SEO关键词（可选）
            sort_order: 排序序号

        Returns:
            Product: 创建的商品对象

        Raises:
            HTTPException: 分类或品牌不存在时抛出错误
        """
        try:
            # 验证品牌存在性（通过Repository）
            if brand_id:
                brand = BrandRepository.get_by_id(db, brand_id)
                if not brand:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="指定的品牌不存在"
                    )

            # 验证分类存在性（通过Repository）
            if category_id:
                category = CategoryRepository.get_by_id(db, category_id)
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="指定的分类不存在"
                    )

            # 创建商品实体
            product = Product(
                name=name,
                description=description,
                brand_id=brand_id,
                category_id=category_id,
                status=status,
                seo_title=seo_title,
                seo_description=seo_description,
                seo_keywords=seo_keywords,
                sort_order=sort_order,
            )

            # 通过Repository创建（Repository只flush，不commit）
            product = ProductRepository.create(db, product)
            
            # Service层管理事务提交
            db.commit()
            db.refresh(product)
            return product
            
        except HTTPException:
            db.rollback()
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="商品创建失败，数据冲突"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"商品创建失败: {str(e)}"
            )

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """
        根据ID获取商品
        
        通过Repository层获取商品数据，符合分层架构原则

        Args:
            db: 数据库会话
            product_id: 商品ID

        Returns:
            Product: 商品对象或None
            
        Raises:
            无异常抛出，商品不存在返回None
        """
        return ProductRepository.get_by_id(db, product_id)

    @staticmethod
    def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Product]:
        """
        获取商品列表（支持筛选和搜索）
        
        通过Repository层查询商品列表，支持多条件筛选

        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            category_id: 分类筛选（可选）
            status: 状态筛选（可选）
            search: 搜索关键词（可选）

        Returns:
            List[Product]: 商品列表
            
        Example:
            # 获取已发布的商品
            products = ProductService.get_products(
                db, status="published", skip=0, limit=20
            )
        """
        # 构建筛选条件字典
        filters = {}
        if category_id is not None:
            filters['category_id'] = category_id
        if status is not None:
            filters['status'] = status
        if search is not None:
            filters['search'] = search
            
        # 通过Repository查询
        return ProductRepository.list(db, skip, limit, **filters)

    @staticmethod
    def update_product(db: Session, product_id: int, **kwargs) -> Optional[Product]:
        """
        更新商品信息
        
        业务流程：
        1. 通过Repository获取商品
        2. 验证业务规则（如分类存在性）
        3. 通过Repository更新商品
        4. Service层管理事务提交

        Args:
            db: 数据库会话
            product_id: 商品ID
            **kwargs: 要更新的字段（name, description, category_id, status等）

        Returns:
            Product: 更新后的商品对象
            None: 商品不存在时返回None

        Raises:
            HTTPException: 
                - 400: 分类不存在或数据冲突
                - 500: 服务器内部错误
                
        Example:
            product = ProductService.update_product(
                db, 
                product_id=123,
                name="新商品名称",
                status="published"
            )
        """
        try:
            # 通过Repository获取商品
            product = ProductRepository.get_by_id(db, product_id)
            if not product:
                return None

            # 验证分类存在性（如果要更新分类）
            if "category_id" in kwargs and kwargs["category_id"]:
                category = CategoryRepository.get_by_id(db, kwargs["category_id"])
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="指定的分类不存在"
                    )

            # 通过Repository更新商品（Repository只flush）
            product = ProductRepository.update(db, product, kwargs)
            
            # Service层管理事务提交
            db.commit()
            db.refresh(product)
            return product
            
        except HTTPException:
            db.rollback()
            raise
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="商品更新失败，数据冲突"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"商品更新失败: {str(e)}"
            )

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """
        删除商品（软删除）
        
        使用SoftDeleteMixin提供的软删除功能，设置is_deleted=True和deleted_at时间戳
        
        业务规则：
        - 使用软删除保护历史数据
        - 已删除商品不会出现在正常查询中
        - 可以通过管理后台恢复

        Args:
            db: 数据库会话
            product_id: 商品ID

        Returns:
            bool: 删除成功返回True，商品不存在返回False
            
        Example:
            success = ProductService.delete_product(db, 123)
            if success:
                print("商品已删除")
        """
        try:
            # 通过Repository获取商品
            product = ProductRepository.get_by_id(db, product_id)
            if not product:
                return False

            # 通过Repository软删除
            ProductRepository.soft_delete(db, product)
            
            # Service层管理事务提交
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"商品删除失败: {str(e)}"
            )


class BrandService:
    """品牌管理业务逻辑服务"""

    @staticmethod
    def create_brand(db: Session, data: Dict[str, Any]) -> Brand:
        brand = Brand(**data)
        return BrandRepository.create(db, brand)

    @staticmethod
    def get_brand(db: Session, brand_id: int) -> Optional[Brand]:
        return BrandRepository.get_by_id(db, brand_id)

    @staticmethod
    def list_brands(db: Session) -> List[Brand]:
        return BrandRepository.list(db)

    @staticmethod
    def update_brand(db: Session, brand_id: int, data: Dict[str, Any]) -> Brand:
        brand = BrandRepository.get_by_id(db, brand_id)
        if not brand:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"品牌ID {brand_id} 不存在")
        return BrandRepository.update(db, brand, data)

    @staticmethod
    def delete_brand(db: Session, brand_id: int) -> bool:
        brand = BrandRepository.get_by_id(db, brand_id)
        if not brand:
            return False
        BrandRepository.soft_delete(db, brand)
        return True


class SKUService:
    """SKU管理业务逻辑服务"""

    @staticmethod
    def create_sku(db: Session, data: Dict[str, Any]) -> SKU:
        """
        创建SKU
        
        注意：遵循四层架构原则，通过Repository层进行数据访问
        """
        # 提取attributes字段（如果存在），不传递给模型构造函数
        attributes_data = data.pop('attributes', None)
        
        try:
            # 通过Repository创建SKU，遵循四层架构原则
            sku = SKU(**data)
            sku = SKURepository.create(db, sku)
            
            # 如果有attributes数据，创建关联的SKUAttribute
            # TODO: 后续可以考虑将此逻辑移到SKURepository中处理
            if attributes_data:
                from .models import SKUAttribute
                for attr_data in attributes_data:
                    attr_data['sku_id'] = sku.id
                    sku_attr = SKUAttribute(**attr_data)
                    db.add(sku_attr)  # 临时直接操作，待SKUAttributeRepository实现后改为Repository模式
                    db.flush()
            
            db.commit()
            return sku
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU创建失败，数据冲突"
            )
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SKU创建失败，系统错误"
            )

    @staticmethod
    def get_sku(db: Session, sku_id: int) -> Optional[SKU]:
        return SKURepository.get_by_id(db, sku_id)

    @staticmethod
    def list_skus(
        db: Session, product_id: Optional[int] = None, is_active: Optional[bool] = None
    ) -> List[SKU]:
        return SKURepository.list(db, product_id, is_active)

    @staticmethod
    def update_sku(db: Session, sku_id: int, data: Dict[str, Any]) -> SKU:
        sku = SKURepository.get_by_id(db, sku_id)
        if not sku:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"SKU ID {sku_id} 不存在")
        return SKURepository.update(db, sku, data)

    @staticmethod
    def delete_sku(db: Session, sku_id: int) -> bool:
        sku = SKURepository.get_by_id(db, sku_id)
        if not sku:
            return False
        SKURepository.soft_delete(db, sku)
        return True

# Add alias for test import compatibility
ProductCatalogService = ProductService
