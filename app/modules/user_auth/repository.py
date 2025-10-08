"""
用户认证模块数据访问层（Repository）

按照四层架构设计，Repository层负责：
1. 数据库CRUD操作
2. 数据查询和过滤
3. 数据访问逻辑封装

⚠️ 重要：Repository层不负责事务管理
- Repository方法只执行数据访问操作（add/flush/refresh）
- 事务的提交/回滚由Service层控制
- 所有方法保持无状态，可在不同事务上下文中复用

参考: docs/architecture/overview.md - 事务管理原则
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import User, Role, Permission, UserRole, RolePermission, Session as UserSession


class UserRepository:
    """用户数据访问"""

    @staticmethod
    def create(db: Session, user: User) -> User:
        """创建用户（不提交事务）"""
        db.add(user)
        db.flush()  # 刷新获取ID，但不提交事务
        db.refresh(user)
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(
            User.username == username,
            User.is_deleted == False
        ).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()

    @staticmethod
    def get_by_username_or_email(db: Session, identifier: str) -> Optional[User]:
        """根据用户名或邮箱获取用户（用于登录）"""
        return db.query(User).filter(
            or_(User.username == identifier, User.email == identifier),
            User.is_deleted == False
        ).first()

    @staticmethod
    def get_by_phone(db: Session, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return db.query(User).filter(
            User.phone == phone,
            User.is_deleted == False
        ).first()

    @staticmethod
    def get_by_wx_openid(db: Session, openid: str) -> Optional[User]:
        """根据微信openid获取用户"""
        return db.query(User).filter(
            User.wx_openid == openid,
            User.is_deleted == False
        ).first()

    @staticmethod
    def check_exists(db: Session, username: Optional[str] = None, email: Optional[str] = None) -> bool:
        """检查用户名或邮箱是否已存在"""
        query = db.query(User).filter(User.is_deleted == False)
        conditions = []
        if username:
            conditions.append(User.username == username)
        if email:
            conditions.append(User.email == email)
        
        if not conditions:
            return False
            
        return query.filter(or_(*conditions)).first() is not None

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        status: Optional[str] = None,
        role: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """获取用户列表"""
        query = db.query(User).filter(User.is_deleted == False)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if status is not None:
            query = query.filter(User.status == status)
        if role is not None:
            query = query.filter(User.role == role)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.like(search_term),
                    User.email.like(search_term),
                    User.real_name.like(search_term)
                )
            )
        
        return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count(db: Session, **filters) -> int:
        """统计用户数量"""
        query = db.query(User).filter(User.is_deleted == False)
        
        if filters.get('is_active') is not None:
            query = query.filter(User.is_active == filters['is_active'])
        if filters.get('status'):
            query = query.filter(User.status == filters['status'])
        
        return query.count()

    @staticmethod
    def update(db: Session, user: User, data: Dict[str, Any]) -> User:
        """更新用户信息"""
        for key, value in data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        db.flush()
        db.refresh(user)
        return user

    @staticmethod
    def update_login_info(db: Session, user: User, ip_address: Optional[str] = None) -> User:
        """更新登录信息"""
        user.last_login_at = datetime.now()
        user.failed_login_attempts = 0
        user.locked_until = None
        db.flush()
        db.refresh(user)
        return user

    @staticmethod
    def increment_failed_login(db: Session, user: User) -> User:
        """增加登录失败次数"""
        user.failed_login_attempts += 1
        # 如果失败次数达到5次，锁定30分钟
        if user.failed_login_attempts >= 5:
            from datetime import timedelta
            user.locked_until = datetime.now() + timedelta(minutes=30)
        db.flush()
        db.refresh(user)
        return user

    @staticmethod
    def soft_delete(db: Session, user: User) -> None:
        """软删除用户"""
        user.is_deleted = True
        user.deleted_at = datetime.now()
        user.is_active = False
        db.flush()

    @staticmethod
    def hard_delete(db: Session, user: User) -> None:
        """硬删除用户（谨慎使用）"""
        db.delete(user)
        db.flush()


class RoleRepository:
    """角色数据访问"""

    @staticmethod
    def create(db: Session, role: Role) -> Role:
        """创建角色"""
        db.add(role)
        db.flush()
        db.refresh(role)
        return role

    @staticmethod
    def get_by_id(db: Session, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """获取角色列表"""
        return db.query(Role).order_by(Role.level.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, role: Role, data: Dict[str, Any]) -> Role:
        """更新角色"""
        for key, value in data.items():
            if hasattr(role, key) and value is not None:
                setattr(role, key, value)
        db.flush()
        db.refresh(role)
        return role

    @staticmethod
    def delete(db: Session, role: Role) -> None:
        """删除角色"""
        db.delete(role)
        db.flush()

    @staticmethod
    def get_user_count(db: Session, role_id: int) -> int:
        """获取拥有该角色的用户数量"""
        return db.query(UserRole).filter(UserRole.role_id == role_id).count()


class PermissionRepository:
    """权限数据访问"""

    @staticmethod
    def create(db: Session, permission: Permission) -> Permission:
        """创建权限"""
        db.add(permission)
        db.flush()
        db.refresh(permission)
        return permission

    @staticmethod
    def get_by_id(db: Session, permission_id: int) -> Optional[Permission]:
        """根据ID获取权限"""
        return db.query(Permission).filter(Permission.id == permission_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Permission]:
        """根据名称获取权限"""
        return db.query(Permission).filter(Permission.name == name).first()

    @staticmethod
    def list(
        db: Session,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Permission]:
        """获取权限列表"""
        query = db.query(Permission)
        if resource:
            query = query.filter(Permission.resource == resource)
        if action:
            query = query.filter(Permission.action == action)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, permission: Permission, data: Dict[str, Any]) -> Permission:
        """更新权限"""
        for key, value in data.items():
            if hasattr(permission, key) and value is not None:
                setattr(permission, key, value)
        db.flush()
        db.refresh(permission)
        return permission

    @staticmethod
    def delete(db: Session, permission: Permission) -> None:
        """删除权限"""
        db.delete(permission)
        db.flush()


class UserRoleRepository:
    """用户角色关联数据访问"""

    @staticmethod
    def create(db: Session, user_role: UserRole) -> UserRole:
        """创建用户角色关联"""
        db.add(user_role)
        db.flush()
        db.refresh(user_role)
        return user_role

    @staticmethod
    def get(db: Session, user_id: int, role_id: int) -> Optional[UserRole]:
        """获取用户角色关联"""
        return db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()

    @staticmethod
    def get_user_roles(db: Session, user_id: int) -> List[Role]:
        """获取用户的所有角色"""
        return db.query(Role).join(UserRole).filter(UserRole.user_id == user_id).all()

    @staticmethod
    def get_role_users(db: Session, role_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        """获取拥有指定角色的用户列表"""
        return db.query(User).join(UserRole).filter(
            UserRole.role_id == role_id,
            User.is_deleted == False
        ).offset(skip).limit(limit).all()

    @staticmethod
    def delete(db: Session, user_id: int, role_id: int) -> None:
        """删除用户角色关联"""
        user_role = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        if user_role:
            db.delete(user_role)
            db.flush()

    @staticmethod
    def delete_all_user_roles(db: Session, user_id: int) -> None:
        """删除用户的所有角色"""
        db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        db.flush()


class RolePermissionRepository:
    """角色权限关联数据访问"""

    @staticmethod
    def create(db: Session, role_permission: RolePermission) -> RolePermission:
        """创建角色权限关联"""
        db.add(role_permission)
        db.flush()
        db.refresh(role_permission)
        return role_permission

    @staticmethod
    def get(db: Session, role_id: int, permission_id: int) -> Optional[RolePermission]:
        """获取角色权限关联"""
        return db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        ).first()

    @staticmethod
    def get_role_permissions(db: Session, role_id: int) -> List[Permission]:
        """获取角色的所有权限"""
        return db.query(Permission).join(RolePermission).filter(
            RolePermission.role_id == role_id
        ).all()

    @staticmethod
    def get_user_permissions(db: Session, user_id: int) -> List[Permission]:
        """获取用户的所有权限（通过角色）"""
        return db.query(Permission).join(RolePermission).join(Role).join(UserRole).filter(
            UserRole.user_id == user_id
        ).distinct().all()

    @staticmethod
    def delete(db: Session, role_id: int, permission_id: int) -> None:
        """删除角色权限关联"""
        role_permission = db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        ).first()
        if role_permission:
            db.delete(role_permission)
            db.flush()

    @staticmethod
    def delete_all_role_permissions(db: Session, role_id: int) -> None:
        """删除角色的所有权限"""
        db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
        db.flush()


class SessionRepository:
    """会话数据访问"""

    @staticmethod
    def create(db: Session, session: UserSession) -> UserSession:
        """创建会话"""
        db.add(session)
        db.flush()
        db.refresh(session)
        return session

    @staticmethod
    def get_by_id(db: Session, session_id: int) -> Optional[UserSession]:
        """根据ID获取会话"""
        return db.query(UserSession).filter(UserSession.id == session_id).first()

    @staticmethod
    def get_by_token_hash(db: Session, token_hash: str) -> Optional[UserSession]:
        """根据token哈希获取会话"""
        return db.query(UserSession).filter(
            UserSession.token_hash == token_hash,
            UserSession.is_active == True
        ).first()

    @staticmethod
    def get_user_active_sessions(db: Session, user_id: int) -> List[UserSession]:
        """获取用户的所有活跃会话"""
        return db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.now()
        ).all()

    @staticmethod
    def update_last_accessed(db: Session, session: UserSession) -> UserSession:
        """更新最后访问时间"""
        session.last_accessed_at = datetime.now()
        db.flush()
        db.refresh(session)
        return session

    @staticmethod
    def deactivate(db: Session, session: UserSession) -> UserSession:
        """停用会话"""
        session.is_active = False
        db.flush()
        db.refresh(session)
        return session

    @staticmethod
    def deactivate_user_sessions(db: Session, user_id: int) -> None:
        """停用用户的所有会话"""
        db.query(UserSession).filter(UserSession.user_id == user_id).update(
            {"is_active": False}
        )
        db.flush()

    @staticmethod
    def delete_expired_sessions(db: Session) -> int:
        """删除过期会话"""
        count = db.query(UserSession).filter(
            UserSession.expires_at < datetime.now()
        ).delete()
        db.flush()
        return count

    @staticmethod
    def delete(db: Session, session: UserSession) -> None:
        """删除会话"""
        db.delete(session)
        db.flush()
