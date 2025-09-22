"""
商品管理模块

对应文档：docs/design/modules/product-catalog/
功能：商品CRUD、分类管理、规格管理
"""

from .router import router
from .service import *
from .models import *
from .schemas import *