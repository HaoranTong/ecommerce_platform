#!/usr/bin/env python3
"""
硬编码检查工具
严格检查API测试生成器中的硬编码问题
"""

import re
import sys
from pathlib import Path

def check_hardcoded_values(file_path):
    """检查文件中的硬编码值"""
    
    hardcode_patterns = [
        # 邮箱地址
        r'"[^"]*@[^"]*\.(com|cn|org)"',
        # 测试用户名
        r'"test_?user"',
        r'"user_?test"', 
        # 测试密码
        r'"test_?password\d*"',
        r'"password\d+"',
        # 手机号
        r'"1[3-9]\d{9}"',
        # 具体的硬编码值
        r'"test@example\.com"',
        r'"13800138000"',
        r'"test_password123"',
        r'"123456"',
        # 测试数据
        r'"test_?data"',
        r'"test_?value"',
        r'"test_?field"',
        # 硬编码的断言字段
        r'assert "username"',
        r'assert "email"', 
        r'assert "password"',
        # 其他明显的测试硬编码
        r'"[^"]*test[^"]*@[^"]*"',
    ]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    violations = []
    
    for i, line in enumerate(lines, 1):
        for pattern in hardcode_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            if matches:
                violations.append({
                    'line': i,
                    'content': line.strip(),
                    'matches': matches,
                    'pattern': pattern
                })
    
    return violations

def main():
    """主检查函数"""
    
    api_generator_path = Path("tools/test_generators/api_test_generator.py")
    
    if not api_generator_path.exists():
        print("❌ API测试生成器文件不存在")
        sys.exit(1)
    
    print("🔍 开始硬编码检查...")
    violations = check_hardcoded_values(api_generator_path)
    
    if violations:
        print(f"❌ 发现 {len(violations)} 个硬编码违规:")
        for v in violations:
            print(f"  行{v['line']}: {v['content']}")
            print(f"    匹配: {v['matches']}")
            print(f"    模式: {v['pattern']}")
            print()
        sys.exit(1)
    else:
        print("✅ 硬编码检查通过！没有发现违规项")
        sys.exit(0)

if __name__ == "__main__":
    main()