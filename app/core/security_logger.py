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