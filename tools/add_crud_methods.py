"""
完成Repository生成器剩余方法的迁移

自动从主程序提取剩余6个CRUD方法的完整实现并添加到Repository生成器
"""
from pathlib import Path
import re

def extract_method_with_proper_boundary(content: str, method_name: str) -> str:
    """提取完整方法,正确处理字符串边界"""
    lines = content.split('\n')
    
    # 找到方法定义
    start_idx = None
    for i, line in enumerate(lines):
        if f'def {method_name}(' in line:
            start_idx = i
            break
    
    if start_idx is None:
        return None
    
    # 从方法开始,找到下一个同级def或类结束
    method_lines = []
    indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    
    i = start_idx
    while i < len(lines):
        line = lines[i]
        
        # 添加当前行
        method_lines.append(line)
        
        # 检查是否到达下一个方法
        if i > start_idx and line.strip():
            current_indent = len(line) - len(line.lstrip())
            if current_indent == indent_level and line.strip().startswith('def '):
                # 找到下一个方法,移除最后一行
                method_lines.pop()
                break
        
        i += 1
    
    return '\n'.join(method_lines)

def add_methods_to_generator():
    """将剩余方法添加到Repository生成器"""
    
    # 读取主程序
    main_file = Path('e:/ecommerce_platform/tools/generate_test_template.py')
    with open(main_file, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # 读取Repository生成器
    gen_file = Path('e:/ecommerce_platform/tools/test_generators/unit/repository_test_generator.py')
    with open(gen_file, 'r', encoding='utf-8') as f:
        gen_content = f.read()
    
    # 提取需要的方法
    methods_to_add = [
        '_generate_repository_create_test',
        '_generate_repository_read_test',
        '_generate_repository_update_test',
        '_generate_repository_delete_test',
        '_generate_repository_count_test',
        '_generate_repository_query_test',
    ]
    
    extracted = {}
    for method_name in methods_to_add:
        print(f"📦 提取方法: {method_name}")
        method_code = extract_method_with_proper_boundary(main_content, method_name)
        if method_code:
            # 移除一层缩进(从类方法到模块方法再到类方法)
            lines = method_code.split('\n')
            adjusted_lines = []
            for line in lines:
                if line.strip():  # 非空行
                    if line.startswith('    '):
                        adjusted_lines.append(line[4:])  # 移除4个空格
                    else:
                        adjusted_lines.append(line)
                else:  # 空行保持
                    adjusted_lines.append(line)
            
            extracted[method_name] = '\n'.join(adjusted_lines)
            print(f"   ✅ 成功 ({len(lines)} 行)")
        else:
            print(f"   ❌ 失败")
    
    print(f"\n📊 总计提取 {len(extracted)}/{len(methods_to_add)} 个方法")
    
    # 生成新内容:替换占位方法
    new_content = gen_content
    
    for method_name, method_code in extracted.items():
        # 找到占位方法的public版本(没有下划线前缀)
        public_name = method_name if not method_name.startswith('_generate_repository_') else method_name.replace('_generate_repository_', 'generate_repository_')
        
        # 构建搜索模式
        pattern = rf'(    def {public_name}\([^)]+\)[^:]*:\s*"""[^"]*"""[^"]*# TODO:[^\n]*\n[^\n]*return[^\n]*)'
        
        # 替换为实际实现
        replacement = f'    {method_code}'
        new_content = re.sub(pattern, replacement, new_content, flags=re.DOTALL)
    
    # 写回文件
    with open(gen_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ 方法已添加到: {gen_file}")
    print("💡 请手动检查并验证导入")

if __name__ == '__main__':
    add_methods_to_generator()
