"""
自动合并Repository测试生成器框架和提取的方法

策略：
1. 保留框架文件的头部（导入、类定义、构造函数）
2. 替换占位方法为提取的实际实现
3. 添加必要的辅助方法
"""
from pathlib import Path

# 文件路径
FRAMEWORK_FILE = Path("e:/ecommerce_platform/tools/test_generators/unit/repository_test_generator.py")
EXTRACTED_FILE = Path("e:/ecommerce_platform/tools/test_generators/unit/_extracted_methods.py")
OUTPUT_FILE = Path("e:/ecommerce_platform/tools/test_generators/unit/repository_test_generator_new.py")

def merge_files():
    print("🔧 合并Repository测试生成器...")
    
    # 读取框架文件
    with open(FRAMEWORK_FILE, 'r', encoding='utf-8') as f:
        framework_content = f.read()
    
    # 读取提取的方法
    with open(EXTRACTED_FILE, 'r', encoding='utf-8') as f:
        extracted_content = f.read()
    
    # 提取框架的头部（到类定义和__init__方法结束）
    lines = framework_content.split('\n')
    
    # 找到__init__方法的结束位置
    header_lines = []
    in_init = False
    init_ended = False
    
    for i, line in enumerate(lines):
        if 'def __init__' in line:
            in_init = True
        
        if in_init and line.strip() and not line.startswith(' ') and i > 0:
            # 遇到下一个方法定义，__init__结束
            init_ended = True
        
        if not init_ended:
            header_lines.append(line)
        else:
            break
    
    # 构建新文件
    new_content = []
    
    # 添加头部
    new_content.extend(header_lines)
    new_content.append('')
    new_content.append('    # ==================== 主要生成方法 ====================')
    new_content.append('')
    
    # 添加提取的方法（移除标记注释，添加4空格缩进）
    extracted_lines = extracted_content.split('\n')
    for line in extracted_lines:
        if line.startswith('# =====') or line == '# 从主程序提取的方法':
            continue  # 跳过分隔符
        if line.startswith('def '):
            # 方法定义，添加缩进
            new_content.append('    ' + line)
        elif line.strip():
            # 非空行，添加缩进
            new_content.append('    ' + line)
        else:
            # 空行保持
            new_content.append(line)
    
    # 写入新文件
    final_content = '\n'.join(new_content)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"✅ 合并完成: {OUTPUT_FILE}")
    print(f"📊 新文件行数: {len(new_content)}")
    
    return OUTPUT_FILE

if __name__ == '__main__':
    output = merge_files()
    print(f"\n💡 请检查生成的文件，如果正确则替换原文件：")
    print(f"   Move-Item {output} {FRAMEWORK_FILE} -Force")
