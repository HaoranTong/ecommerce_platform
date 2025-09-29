"""
用户认证模块

对应文档：docs/design/modules/user-auth/
功能：用户注册、登录、权限管理、JWT认证
"""

from .models import *
from .router import router
from .schemas import *
from .service import *
