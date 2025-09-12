"""
文件名：category_service.py
文件路径：app/services/category_service.py
功能描述：商品分类管理相关的业务逻辑服务
主要功能：
- 分类的创建、查询、更新、删除
- 分类层级结构管理
- 分类商品统计和排序
使用说明：
- 导入：from app.services.category_service import CategoryService
- 在路由中调用：CategoryService.create_category(category_data)
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.data_models import Category, Product


class CategoryService:
    """商品分类管理业务逻辑服务"""
    
    @staticmethod
    def create_category(db: Session, name: str, description: Optional[str] = None,
                       parent_id: Optional[int] = None, sort_order: int = 0,
                       is_active: bool = True, meta_data: Optional[Dict[str, Any]] = None) -> Category:
        """
        创建新分类
        
        Args:
            db: 数据库会话
            name: 分类名称
            description: 分类描述
            parent_id: 父分类ID
            sort_order: 排序顺序
            is_active: 是否激活
            meta_data: 元数据（JSON格式）
            
        Returns:
            Category: 创建的分类对象
            
        Raises:
            HTTPException: 分类名称重复或父分类不存在时抛出错误
        """
        # 验证分类名称唯一性（同级别下）
        existing_category = db.query(Category).filter(
            Category.name == name,
            Category.parent_id == parent_id
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="同级别下已存在相同名称的分类"
            )
        
        # 验证父分类存在性
        if parent_id:
            parent_category = db.query(Category).filter(Category.id == parent_id).first()
            if not parent_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父分类不存在"
                )
        
        category = Category(
            name=name,
            description=description,
            parent_id=parent_id,
            sort_order=sort_order,
            is_active=is_active,
            meta_data=meta_data or {}
        )
        
        try:
            db.add(category)
            db.commit()
            db.refresh(category)
            return category
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类创建失败，数据冲突"
            )
    
    @staticmethod
    def get_category_by_id(db: Session, category_id: int, include_children: bool = False) -> Optional[Category]:
        """
        根据ID获取分类
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            include_children: 是否包含子分类
            
        Returns:
            Category: 分类对象或None
        """
        query = db.query(Category)
        
        if include_children:
            query = query.options(joinedload(Category.children))
        
        return query.filter(Category.id == category_id).first()
    
    @staticmethod
    def get_categories(db: Session, parent_id: Optional[int] = None, 
                      is_active: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[Category]:
        """
        获取分类列表
        
        Args:
            db: 数据库会话
            parent_id: 父分类ID筛选（None表示获取顶级分类）
            is_active: 激活状态筛选
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            List[Category]: 分类列表
        """
        query = db.query(Category)
        
        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        else:
            query = query.filter(Category.parent_id.is_(None))
        
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        
        return query.order_by(Category.sort_order, Category.name).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_category_tree(db: Session, parent_id: Optional[int] = None, 
                         is_active: Optional[bool] = True) -> List[Dict[str, Any]]:
        """
        获取分类树结构
        
        Args:
            db: 数据库会话
            parent_id: 根分类ID（None表示从顶级开始）
            is_active: 是否只获取激活的分类
            
        Returns:
            List[Dict[str, Any]]: 分类树结构
        """
        def build_tree(parent_id: Optional[int]) -> List[Dict[str, Any]]:
            categories = CategoryService.get_categories(db, parent_id, is_active, limit=1000)
            tree = []
            
            for category in categories:
                category_dict = {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'sort_order': category.sort_order,
                    'is_active': category.is_active,
                    'product_count': CategoryService.get_product_count(db, category.id),
                    'children': build_tree(category.id)
                }
                tree.append(category_dict)
            
            return tree
        
        return build_tree(parent_id)
    
    @staticmethod
    def update_category(db: Session, category_id: int, name: Optional[str] = None,
                       description: Optional[str] = None, parent_id: Optional[int] = None,
                       sort_order: Optional[int] = None, is_active: Optional[bool] = None,
                       meta_data: Optional[Dict[str, Any]] = None) -> Optional[Category]:
        """
        更新分类信息
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            name: 新名称
            description: 新描述
            parent_id: 新父分类ID
            sort_order: 新排序顺序
            is_active: 新激活状态
            meta_data: 新元数据
            
        Returns:
            Category: 更新后的分类对象或None
            
        Raises:
            HTTPException: 分类名称重复或父分类不存在时抛出错误
        """
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        
        # 验证分类名称唯一性（如果更改了名称）
        if name and name != category.name:
            existing_category = db.query(Category).filter(
                Category.name == name,
                Category.parent_id == (parent_id if parent_id is not None else category.parent_id),
                Category.id != category_id
            ).first()
            
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="同级别下已存在相同名称的分类"
                )
        
        # 验证父分类存在性（如果更改了父分类）
        if parent_id is not None and parent_id != category.parent_id:
            if parent_id:
                parent_category = db.query(Category).filter(Category.id == parent_id).first()
                if not parent_category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="父分类不存在"
                    )
            
            # 检查是否会形成循环引用
            if CategoryService._would_create_cycle(db, category_id, parent_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能将分类移动到其子分类下，这会形成循环引用"
                )
        
        # 更新字段
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        if parent_id is not None:
            category.parent_id = parent_id
        if sort_order is not None:
            category.sort_order = sort_order
        if is_active is not None:
            category.is_active = is_active
        if meta_data is not None:
            category.meta_data.update(meta_data)
        
        db.commit()
        db.refresh(category)
        return category
    
    @staticmethod
    def delete_category(db: Session, category_id: int, cascade: bool = False) -> bool:
        """
        删除分类
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            cascade: 是否级联删除子分类
            
        Returns:
            bool: 删除成功返回True
            
        Raises:
            HTTPException: 分类下有商品或子分类时抛出错误（非级联删除）
        """
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False
        
        # 检查是否有商品关联
        product_count = CategoryService.get_product_count(db, category_id)
        if product_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"分类下还有 {product_count} 个商品，无法删除"
            )
        
        # 检查是否有子分类
        children_count = db.query(Category).filter(Category.parent_id == category_id).count()
        if children_count > 0 and not cascade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"分类下还有 {children_count} 个子分类，请先删除子分类或使用级联删除"
            )
        
        # 级联删除子分类
        if cascade:
            CategoryService._delete_category_recursive(db, category_id)
        else:
            db.delete(category)
        
        db.commit()
        return True
    
    @staticmethod
    def get_product_count(db: Session, category_id: int, include_children: bool = False) -> int:
        """
        获取分类下的商品数量
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            include_children: 是否包含子分类的商品
            
        Returns:
            int: 商品数量
        """
        if include_children:
            # 获取所有子分类ID
            child_ids = CategoryService._get_all_child_ids(db, category_id)
            child_ids.append(category_id)
            return db.query(Product).filter(Product.category_id.in_(child_ids)).count()
        else:
            return db.query(Product).filter(Product.category_id == category_id).count()
    
    @staticmethod
    def get_category_path(db: Session, category_id: int) -> List[Category]:
        """
        获取分类的完整路径（从根到当前分类）
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            
        Returns:
            List[Category]: 分类路径列表
        """
        path = []
        current_id = category_id
        
        while current_id:
            category = db.query(Category).filter(Category.id == current_id).first()
            if not category:
                break
            path.insert(0, category)
            current_id = category.parent_id
        
        return path
    
    @staticmethod
    def move_category(db: Session, category_id: int, new_parent_id: Optional[int],
                     new_sort_order: Optional[int] = None) -> Optional[Category]:
        """
        移动分类到新的父分类下
        
        Args:
            db: 数据库会话
            category_id: 要移动的分类ID
            new_parent_id: 新父分类ID
            new_sort_order: 新排序顺序
            
        Returns:
            Category: 移动后的分类对象或None
        """
        return CategoryService.update_category(
            db, category_id, parent_id=new_parent_id, sort_order=new_sort_order
        )
    
    @staticmethod
    def _would_create_cycle(db: Session, category_id: int, new_parent_id: Optional[int]) -> bool:
        """
        检查移动分类是否会形成循环引用
        
        Args:
            db: 数据库会话
            category_id: 要移动的分类ID
            new_parent_id: 新父分类ID
            
        Returns:
            bool: 会形成循环返回True
        """
        if not new_parent_id:
            return False
        
        # 获取新父分类的所有祖先
        current_id = new_parent_id
        while current_id:
            if current_id == category_id:
                return True
            
            parent = db.query(Category).filter(Category.id == current_id).first()
            if not parent:
                break
            current_id = parent.parent_id
        
        return False
    
    @staticmethod
    def _get_all_child_ids(db: Session, category_id: int) -> List[int]:
        """
        递归获取所有子分类ID
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            
        Returns:
            List[int]: 子分类ID列表
        """
        child_ids = []
        children = db.query(Category).filter(Category.parent_id == category_id).all()
        
        for child in children:
            child_ids.append(child.id)
            child_ids.extend(CategoryService._get_all_child_ids(db, child.id))
        
        return child_ids
    
    @staticmethod
    def _delete_category_recursive(db: Session, category_id: int):
        """
        递归删除分类及其所有子分类
        
        Args:
            db: 数据库会话
            category_id: 分类ID
        """
        # 先删除所有子分类
        children = db.query(Category).filter(Category.parent_id == category_id).all()
        for child in children:
            CategoryService._delete_category_recursive(db, child.id)
        
        # 删除当前分类
        category = db.query(Category).filter(Category.id == category_id).first()
        if category:
            db.delete(category)