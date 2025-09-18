"""
安全事件日志记录模块
用于记录登录失败、账户锁定等安全相关事件
"""

import logging
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

class SecurityEventFilter(logging.Filter):
    """安全事件过滤器，确保只记录安全相关事件"""
    
    def filter(self, record):
        return hasattr(record, 'event_type')

class SecurityJSONFormatter(logging.Formatter):
    """安全事件JSON格式化器"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        
        # 添加安全事件相关字段
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'username'):
            log_entry['username'] = record.username
        if hasattr(record, 'event_type'):
            log_entry['event_type'] = record.event_type
        if hasattr(record, 'failed_attempts'):
            log_entry['failed_attempts'] = record.failed_attempts
        if hasattr(record, 'locked_until'):
            log_entry['locked_until'] = record.locked_until
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_security_logger():
    """配置安全事件日志记录器"""
    
    # 创建安全日志记录器
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    
    # 防止重复添加处理器
    if security_logger.handlers:
        return security_logger
    
    # 创建文件处理器（每天轮转）
    security_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / "security_events.log",
        when='midnight',
        interval=1,
        backupCount=30,  # 保留30天的日志
        encoding='utf-8'
    )
    
    # 创建控制台处理器（开发环境）
    console_handler = logging.StreamHandler()
    
    # 设置格式化器
    json_formatter = SecurityJSONFormatter()
    security_handler.setFormatter(json_formatter)
    console_handler.setFormatter(json_formatter)
    
    # 添加过滤器
    security_filter = SecurityEventFilter()
    security_handler.addFilter(security_filter)
    console_handler.addFilter(security_filter)
    
    # 添加处理器
    security_logger.addHandler(security_handler)
    security_logger.addHandler(console_handler)
    
    # 防止向父日志记录器传播
    security_logger.propagate = False
    
    return security_logger

def log_security_event(event_type: str, message: str, user_data: Dict[str, Any] = None, **kwargs):
    """记录安全事件的便捷函数"""
    logger = setup_security_logger()
    
    # 准备额外信息
    extra = {"event_type": event_type}
    if user_data:
        extra.update(user_data)
    extra.update(kwargs)
    
    # 根据事件类型选择日志级别
    if event_type in ['account_locked', 'login_failed', 'suspicious_activity']:
        logger.warning(message, extra=extra)
    elif event_type in ['login_success', 'password_changed']:
        logger.info(message, extra=extra)
    else:
        logger.info(message, extra=extra)

# 初始化安全日志记录器
setup_security_logger()


class SecurityLogger:
    """
    安全审计日志记录器类
    
    功能描述：
        提供会员系统相关的安全事件记录功能，包括会员操作、
        积分变更、权益使用等关键业务操作的审计日志。
        
    主要方法：
        - log_member_access(): 记录会员信息访问
        - log_member_creation(): 记录会员创建
        - log_member_update(): 记录会员信息更新
        - log_level_upgrade(): 记录等级升级
        - log_point_transaction(): 记录积分交易
        - log_benefit_usage(): 记录权益使用
        - log_activity_creation(): 记录活动创建
        - log_activity_participation(): 记录活动参与
        
    使用方式：
        ```python
        security_logger = SecurityLogger()
        security_logger.log_member_access(user_id, "profile_view", {...})
        ```
    """

    def __init__(self):
        """初始化安全日志记录器"""
        self.logger = setup_security_logger()

    def log_member_access(self, user_id: int, action: str, data: Dict[str, Any]):
        """
        记录会员信息访问
        
        Args:
            user_id (int): 用户ID
            action (str): 操作类型
            data (Dict[str, Any]): 额外数据
        """
        message = f"会员信息访问: user_id={user_id}, action={action}"
        log_security_event(
            event_type="member_access",
            message=message,
            user_data={"user_id": user_id},
            action=action,
            **data
        )

    def log_member_creation(self, user_id: int, data: Dict[str, Any]):
        """
        记录会员创建
        
        Args:
            user_id (int): 用户ID
            data (Dict[str, Any]): 会员创建数据
        """
        message = f"会员创建: user_id={user_id}, member_id={data.get('member_id')}"
        log_security_event(
            event_type="member_creation",
            message=message,
            user_data={"user_id": user_id},
            **data
        )

    def log_member_update(self, user_id: int, data: Dict[str, Any]):
        """
        记录会员信息更新
        
        Args:
            user_id (int): 用户ID
            data (Dict[str, Any]): 更新数据
        """
        message = f"会员信息更新: user_id={user_id}, fields={data.get('updated_fields')}"
        log_security_event(
            event_type="member_update",
            message=message,
            user_data={"user_id": user_id},
            **data
        )

    def log_level_upgrade(self, user_id: int, data: Dict[str, Any]):
        """
        记录会员等级升级
        
        Args:
            user_id (int): 用户ID
            data (Dict[str, Any]): 升级数据
        """
        old_level = data.get('old_level', {}).get('level_name', 'Unknown')
        new_level = data.get('new_level', {}).get('level_name', 'Unknown')
        message = f"会员等级升级: user_id={user_id}, {old_level} -> {new_level}"
        log_security_event(
            event_type="level_upgrade",
            message=message,
            user_data={"user_id": user_id},
            **data
        )

    def log_point_transaction(self, user_id: int, data: Dict[str, Any]):
        """
        记录积分交易
        
        Args:
            user_id (int): 用户ID
            data (Dict[str, Any]): 交易数据
        """
        transaction_type = data.get('type', 'Unknown')
        points = data.get('points', 0)
        message = f"积分交易: user_id={user_id}, type={transaction_type}, points={points}"
        log_security_event(
            event_type="point_transaction",
            message=message,
            user_data={"user_id": user_id},
            **data
        )

    def log_benefit_usage(self, user_id: int, data: Dict[str, Any]):
        """
        记录权益使用
        
        Args:
            user_id (int): 用户ID
            data (Dict[str, Any]): 权益使用数据
        """
        benefit_type = data.get('benefit_type', 'Unknown')
        benefit_name = data.get('benefit_name', 'Unknown')
        message = f"权益使用: user_id={user_id}, benefit={benefit_name} ({benefit_type})"
        log_security_event(
            event_type="benefit_usage",
            message=message,
            user_data={"user_id": user_id},
            **data
        )

    def log_activity_creation(self, data: Dict[str, Any]):
        """
        记录活动创建
        
        Args:
            data (Dict[str, Any]): 活动创建数据
        """
        activity_id = data.get('activity_id', 'Unknown')
        title = data.get('title', 'Unknown')
        message = f"活动创建: activity_id={activity_id}, title={title}"
        log_security_event(
            event_type="activity_creation",
            message=message,
            **data
        )

    def log_activity_participation(self, user_id: int, data: Dict[str, Any]):
        """
        记录活动参与
        
        Args:
            user_id (int): 用户ID
            data (Dict[str, Any]): 参与数据
        """
        activity_id = data.get('activity_id', 'Unknown')
        activity_title = data.get('activity_title', 'Unknown')
        message = f"活动参与: user_id={user_id}, activity={activity_title} (ID:{activity_id})"
        log_security_event(
            event_type="activity_participation",
            message=message,
            user_data={"user_id": user_id},
            **data
        )