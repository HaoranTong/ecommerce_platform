#!/usr/bin/env python3
"""
修复 member_system Repository 测试中的硬编码问题

问题: 测试生成工具为 member_code 字段生成了 "TEST测试" 这样的值
      但模型验证要求格式为 "M+年月日+4位序号" (13位字符)
      
解决: 批量替换测试文件中的硬编码值为符合验证规则的值
"""

import re
from pathlib import Path
from datetime import datetime

def fix_member_code_in_file(file_path: Path):
    """修复文件中的 member_code 硬编码问题"""
    
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # 生成符合格式的 member_code
    today_str = datetime.now().strftime('%Y%m%d')
    
    # 替换模式1: member_code="TEST查询测试"
    content = re.sub(
        r'member_code="TEST查询测试"',
        f'member_code="M{today_str}0001"',
        content
    )
    
    # 替换模式2: member_code="TEST完整测试"
    content = re.sub(
        r'member_code="TEST完整测试"',
        f'member_code="M{today_str}0002"',
        content
    )
    
    # 替换模式3: member_code="TEST测试"
    content = re.sub(
        r'member_code="TEST测试"',
        f'member_code="M{today_str}0003"',
        content
    )
    
    # 修复其他字段的硬编码
    # total_spent 应该是 Decimal 类型
    content = re.sub(
        r'total_spent="(查询测试|完整测试|测试)"',
        'total_spent=Decimal("100.00")',
        content
    )
    
    # join_date 应该是 date 类型
    content = re.sub(
        r'join_date="(查询测试|完整测试|测试)"',
        'join_date=date.today()',
        content
    )
    
    # 确保导入必要的模块
    if 'from decimal import Decimal' not in content and 'Decimal' in content:
        # 在 imports 区域添加
        content = re.sub(
            r'(from datetime import datetime)',
            r'\1, date\nfrom decimal import Decimal',
            content,
            count=1
        )
    
    # 如果内容有变化，写回文件
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ 修复完成: {file_path}")
        return True
    else:
        print(f"⏭️  无需修复: {file_path}")
        return False

def main():
    """主函数"""
    test_file = Path("tests/unit/test_repositories/test_member_system_repositories.py")
    
    if not test_file.exists():
        print(f"❌ 文件不存在: {test_file}")
        return
    
    print(f"🔧 开始修复测试文件中的硬编码问题...")
    print(f"📁 文件: {test_file}")
    print()
    
    if fix_member_code_in_file(test_file):
        print()
        print("✅ 修复完成！")
        print()
        print("📋 修复内容:")
        print("  1. member_code 字段值改为符合 M+年月日+4位序号 格式")
        print("  2. total_spent 字段值改为 Decimal 类型")
        print("  3. join_date 字段值改为 date 类型")
        print("  4. 添加必要的 import 语句")
    else:
        print()
        print("ℹ️  文件无需修复或已经修复")

if __name__ == "__main__":
    main()
