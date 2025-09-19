"""
修复产品目录测试数据重复键问题

将固定的测试数据改为使用随机后缀，避免MySQL重复键错误
"""
import uuid
import random


def generate_unique_brand_name(base_name):
    """生成唯一品牌名称"""
    suffix = str(uuid.uuid4())[:8]
    return f"{base_name}_{suffix}"


def generate_unique_sku_code(base_code):
    """生成唯一SKU编码"""
    suffix = random.randint(1000, 9999)
    return f"{base_code}_{suffix}"


# 将要替换的测试数据模式
brand_replacements = [
    ('name="苹果"', 'name=generate_unique_brand_name("苹果")'),
    ('name="华为"', 'name=generate_unique_brand_name("华为")'),
    ('name="小米"', 'name=generate_unique_brand_name("小米")'),
    ('name="联想"', 'name=generate_unique_brand_name("联想")'),
]

sku_replacements = [
    ('sku_code="TEST-001"', 'sku_code=generate_unique_sku_code("TEST")'),
    ('sku_code="UNIQUE-001"', 'sku_code=generate_unique_sku_code("UNIQUE")'),
]

# 添加导入语句模板
import_addition = '''
import uuid
import random

def generate_unique_brand_name(base_name):
    """生成唯一品牌名称"""
    suffix = str(uuid.uuid4())[:8]
    return f"{base_name}_{suffix}"

def generate_unique_sku_code(base_code):
    """生成唯一SKU编码"""
    suffix = random.randint(1000, 9999)
    return f"{base_code}_{suffix}"

'''

print("修复脚本准备完成，将更新测试文件...")