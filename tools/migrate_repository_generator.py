"""
Repository测试生成器实现迁移脚本

自动从主程序提取Repository测试生成相关方法并迁移到新文件

使用方法:
python tools/migrate_repository_generator.py
"""
import re
from pathlib import Path

# 需要迁移的方法列表（按依赖顺序）
METHODS_TO_MIGRATE = [
    # 辅助方法（无依赖，先迁移）
    '_table_name_to_model_name',
    '_has_composite_primary_key',
    '_get_primary_key_fields',
    '_get_minimal_test_value',
    '_get_test_value_for_field',
    
    # 实体创建方法（依赖上面的辅助方法）
    '_generate_minimal_entity_creation',
    '_generate_test_entity_creation',
    
    # 参数推断方法
    '_infer_query_parameter',
    '_infer_entity_from_param',
    
    # CRUD测试生成方法（依赖所有辅助方法）
    '_generate_repository_create_test',
    '_generate_repository_read_test',
    '_generate_repository_update_test',
    '_generate_repository_delete_test',
    '_generate_repository_count_test',
    '_generate_repository_query_test',
    
    # 主调度方法（依赖所有CRUD方法）
    '_generate_single_repository_test',
    '_generate_repository_tests',
]

def extract_method(content: str, method_name: str) -> str:
    """从文件内容中提取完整的方法定义"""
    # 找到方法定义的起始位置
    pattern = rf'^    def {method_name}\('
    lines = content.split('\n')
    
    start_idx = None
    for i, line in enumerate(lines):
        if re.match(pattern, line):
            start_idx = i
            break
    
    if start_idx is None:
        print(f"  ⚠️  未找到方法: {method_name}")
        return None
    
    # 找到方法的结束位置（下一个同级方法或类结束）
    method_lines = [lines[start_idx]]
    indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        
        # 空行总是包含
        if not line.strip():
            method_lines.append(line)
            continue
        
        # 检查缩进级别
        current_indent = len(line) - len(line.lstrip())
        
        # 如果遇到同级或更低级别的def，说明方法结束
        if current_indent <= indent_level and line.strip().startswith('def '):
            break
        
        # 如果遇到同级别的非空行（不是方法内容），可能是类的其他部分
        if current_indent < indent_level and line.strip():
            break
        
        method_lines.append(line)
    
    return '\n'.join(method_lines)

def transform_method(method_code: str, method_name: str) -> str:
    """转换方法代码：
    1. 移除一层缩进（从类方法变为独立方法）
    2. 添加类型提示导入
    3. 更新方法调用（self.method -> self.method保持不变，因为仍在类中）
    """
    lines = method_code.split('\n')
    
    # 移除一层缩进（4个空格）
    transformed_lines = []
    for line in lines:
        if line.strip():  # 非空行
            if line.startswith('    '):
                transformed_lines.append(line[4:])  # 移除4个空格
            else:
                transformed_lines.append(line)
        else:  # 空行
            transformed_lines.append(line)
    
    return '\n'.join(transformed_lines)

def main():
    print("🚀 开始迁移 Repository 测试生成器实现...\n")
    
    # 读取主程序
    main_file = Path('e:/ecommerce_platform/tools/generate_test_template.py')
    print(f"📖 读取主程序: {main_file}")
    
    with open(main_file, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # 读取目标文件（Repository生成器框架）
    target_file = Path('e:/ecommerce_platform/tools/test_generators/unit/repository_test_generator.py')
    print(f"📖 读取目标文件: {target_file}\n")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        target_content = f.read()
    
    # 提取所有方法
    print("📦 提取方法...")
    extracted_methods = []
    
    for method_name in METHODS_TO_MIGRATE:
        print(f"  🔍 提取: {method_name}")
        method_code = extract_method(main_content, method_name)
        
        if method_code:
            # 转换方法代码
            transformed_code = transform_method(method_code, method_name)
            extracted_methods.append((method_name, transformed_code))
            print(f"     ✅ 成功 ({len(method_code.split(chr(10)))} 行)")
        else:
            print(f"     ❌ 失败")
    
    print(f"\n✅ 成功提取 {len(extracted_methods)}/{len(METHODS_TO_MIGRATE)} 个方法")
    
    # 统计代码行数
    total_lines = sum(len(code.split('\n')) for _, code in extracted_methods)
    print(f"📊 总计约 {total_lines} 行代码\n")
    
    # 生成新的目标文件内容
    print("🔧 生成新文件内容...")
    
    # 找到类定义的结束位置（所有pass的位置）
    # 在最后一个方法的pass之前插入提取的方法
    
    # 简单策略：在文件末尾添加所有方法
    new_content = target_content.rstrip()
    
    # 移除类的最后一个pass和方法占位符
    # 这需要更复杂的解析，暂时手动处理
    
    print("⚠️  警告: 自动迁移脚本需要进一步完善")
    print("💡 建议: 手动将提取的方法复制到目标文件")
    print(f"\n提取的方法总数: {len(extracted_methods)}")
    print(f"预计总行数: {total_lines}")
    
    # 输出提取的方法到临时文件，供手动复制
    temp_file = Path('e:/ecommerce_platform/tools/test_generators/unit/_extracted_methods.py')
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write("# 从主程序提取的方法\n\n")
        for method_name, method_code in extracted_methods:
            f.write(f"# ===== {method_name} =====\n")
            f.write(method_code)
            f.write("\n\n")
    
    print(f"\n✅ 提取的方法已保存到: {temp_file}")
    print("💡 请手动将这些方法复制到 repository_test_generator.py")

if __name__ == '__main__':
    main()
