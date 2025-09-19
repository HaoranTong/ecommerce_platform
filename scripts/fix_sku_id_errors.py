"""
批量修复sku_id类型错误的脚本

这个脚本会：
1. 扫描所有测试文件中的sku_id字符串使用
2. 自动替换为正确的整数ID用法
3. 更新测试文件使用标准测试数据工厂
"""

import os
import re
import sys
from pathlib import Path


def fix_sku_id_in_file(file_path: Path) -> bool:
    """修复单个文件中的sku_id问题
    
    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {file_path} - {e}")
        return False
    
    original_content = content
    modified = False
    
    # 1. 修复直接的字符串sku_id赋值
    patterns_to_fix = [
        # sku_id="SKU_xxx" → 需要使用sku.id
        (r'sku_id\s*=\s*["\']SKU_[^"\']*["\']', 'sku_id=sku.id  # 🔧 修复：使用整数ID而不是字符串'),
        
        # 在Mock对象中的sku_id赋值
        (r'(\w+)\.sku_id\s*=\s*["\']SKU_[^"\']*["\']', r'\1.sku_id = 1  # 🔧 修复：使用整数ID'),
        
        # 函数调用中的sku_id参数
        (r'sku_id\s*=\s*["\'][\w-]+["\']', 'sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID'),
        
        # InventoryStock等模型中的字符串sku_id
        (r'InventoryStock\([^)]*sku_id\s*=\s*["\'][^"\']*["\']', 'InventoryStock(sku_id=sku.id'),
    ]
    
    for pattern, replacement in patterns_to_fix:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    # 2. 添加标准测试数据工厂导入（如果没有的话）
    if 'from tests.factories.test_data_factory import' not in content:
        # 找到其他导入语句的位置
        import_match = re.search(r'(from app\..*import.*\n)', content)
        if import_match:
            import_pos = import_match.end()
            factory_import = "from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator\n"
            content = content[:import_pos] + factory_import + content[import_pos:]
            modified = True
    
    # 3. 如果文件被修改了，写回文件
    if modified:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 修复完成: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 写入文件失败: {file_path} - {e}")
            return False
    
    return False


def scan_and_fix_all_tests():
    """扫描并修复所有测试文件"""
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print(f"❌ 测试目录不存在: {tests_dir}")
        return
    
    # 扫描所有Python测试文件
    test_files = list(tests_dir.rglob("*.py"))
    
    print(f"🔍 扫描到 {len(test_files)} 个测试文件")
    
    fixed_files = []
    
    for test_file in test_files:
        # 跳过__pycache__和其他非测试文件
        if "__pycache__" in str(test_file) or test_file.name == "__init__.py":
            continue
            
        if fix_sku_id_in_file(test_file):
            fixed_files.append(test_file)
    
    print(f"\n📊 修复结果:")
    print(f"✅ 修复了 {len(fixed_files)} 个文件")
    
    if fixed_files:
        print("\n修复的文件列表:")
        for file_path in fixed_files:
            print(f"  - {file_path.relative_to(project_root)}")
    
    return len(fixed_files)


def create_example_test_file():
    """创建示例测试文件展示正确用法"""
    example_content = '''"""
示例：正确使用sku_id的测试文件

❌ 错误用法：
    sku_id="SKU_001"  # 字符串类型，会导致外键错误
    
✅ 正确用法：
    sku_id=sku.id     # 整数类型，正确的外键引用
"""

import pytest
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator


class TestCorrectSkuIdUsage:
    """演示正确的sku_id使用方法"""
    
    def test_create_inventory_with_correct_sku_id(self, unit_test_db):
        """✅ 正确：使用整数sku_id"""
        # 创建完整的测试数据链
        user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(unit_test_db)
        
        # ✅ 正确：使用sku.id（整数）
        inventory = StandardTestDataFactory.create_inventory_stock(
            unit_test_db,
            sku_id=sku.id,  # 🔥 关键：使用sku.id而不是sku.sku_code
            available_quantity=100
        )
        
        assert inventory.sku_id == sku.id  # 整数比较
        assert isinstance(inventory.sku_id, int)
    
    def test_create_cart_item_with_correct_sku_id(self, unit_test_db):
        """✅ 正确：购物车项目使用整数sku_id"""
        user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(unit_test_db)
        
        # ✅ 正确：使用sku.id（整数）
        cart_item = StandardTestDataFactory.create_cart_item(
            unit_test_db,
            user_id=user.id,
            sku_id=sku.id,  # 🔥 关键：整数ID
            quantity=2
        )
        
        assert cart_item.sku_id == sku.id
        assert isinstance(cart_item.sku_id, int)
    
    def test_validation_prevents_string_sku_id(self, unit_test_db):
        """✅ 验证器防止字符串sku_id错误"""
        with pytest.raises(TypeError, match="sku_id必须是整数类型"):
            TestDataValidator.validate_sku_id("SKU_001")  # 字符串会抛出错误
        
        # 整数通过验证
        TestDataValidator.validate_sku_id(123)  # 不会抛出错误
'''
    
    example_path = Path(__file__).parent / "example_correct_sku_usage.py"
    with open(example_path, 'w', encoding='utf-8') as f:
        f.write(example_content)
    
    print(f"✅ 创建示例文件: {example_path}")


if __name__ == "__main__":
    print("🚀 开始批量修复sku_id类型错误...")
    print("=" * 50)
    
    fixed_count = scan_and_fix_all_tests()
    
    print("=" * 50)
    print("📝 创建示例文件...")
    create_example_test_file()
    
    print("=" * 50)
    print("🎉 批量修复完成！")
    print(f"📊 总共修复了 {fixed_count} 个文件")
    print("\n💡 下一步：")
    print("1. 检查修复结果")
    print("2. 运行测试验证修复效果")
    print("3. 如有需要，手动调整特殊情况")