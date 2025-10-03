#!/usr/bin/env python3
"""
硬编码检查工具 v2.0
严格检查API测试生成器中的硬编码问题
"""

import re
import sys
from pathlib import Path

def check_hardcoded_values(file_path):
    """检查文件中的硬编码值"""
    
    violations = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        line_strip = line.strip()
        
        # 跳过注释行
        if line_strip.startswith('#') or line_strip.startswith('"""') or line_strip.startswith("'''"):
            continue
            
        # 跳过变量定义行（左侧赋值）
        if re.match(r'^\s*\w+\s*=', line_strip):
            continue
            
        # 检查真正的硬编码数据值（在字符串中的固定值）
        hardcoded_patterns = [
            r'"test@example\.com"',          # 固定邮箱
            r"'test@example\.com'",          # 固定邮箱
            r'"test_password123"',           # 固定密码
            r"'test_password123'",           # 固定密码  
            r'"13800138000"',                # 固定手机号
            r"'13800138000'",                # 固定手机号
            r'"123456"',                     # 固定密码
            r"'123456'",                     # 固定密码
            r'"测试用户"',                    # 固定中文名
            r"'测试用户'",                    # 固定中文名
            r'"admin"',                      # 固定用户名（在字符串中）
            r"'admin'",                      # 固定用户名（在字符串中）
            r'"testuser"',                   # 固定用户名
            r"'testuser'",                   # 固定用户名
        ]
        
        for pattern in hardcoded_patterns:
            if re.search(pattern, line):
                match = re.search(pattern, line)
                violations.append({
                    'line': i,
                    'content': line.strip(),
                    'value': match.group(0)
                })
    
    return violations

def main():
    if len(sys.argv) != 2:
        print("用法: python check_hardcode.py <文件路径>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    print("🔍 开始硬编码检查...")
    violations = check_hardcoded_values(file_path)
    
    if violations:
        print(f"❌ 发现 {len(violations)} 个硬编码违规项:")
        for v in violations:
            print(f"  第{v['line']}行: {v['content']}")
            print(f"    违规值: {v['value']}")
        sys.exit(1)
    else:
        print("✅ 硬编码检查通过！没有发现违规项")

if __name__ == "__main__":
    main()