"""
修复Pydantic V2兼容性问题的脚本
"""
import os
import re

def fix_pydantic_config(file_path):
    """修复单个文件中的Pydantic配置"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 确保导入了ConfigDict
        if 'ConfigDict' not in content and 'class Config:' in content:
            # 找到pydantic导入并添加ConfigDict
            import_pattern = r'from pydantic import ([^(]*?)(\n)'
            match = re.search(import_pattern, content)
            if match:
                imports = match.group(1).strip()
                if 'ConfigDict' not in imports:
                    new_imports = imports.rstrip(', ') + ', ConfigDict'
                    content = re.sub(import_pattern, f'from pydantic import {new_imports}\\2', content)
        
        # 替换class Config:模式
        # 处理简单的from_attributes = True
        pattern1 = r'(\s+)class Config:\s*\n\s+from_attributes = True'
        replacement1 = r'\1model_config = ConfigDict(from_attributes=True)'
        content = re.sub(pattern1, replacement1, content)
        
        # 处理复杂的Config类
        pattern2 = r'(\s+)class Config:\s*\n((?:\s+\w+\s*=.*\n)*)'
        def config_replacer(match):
            indent = match.group(1)
            config_lines = match.group(2)
            
            # 解析配置选项
            options = []
            for line in config_lines.strip().split('\n'):
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 转换废弃的配置项
                    if key == 'orm_mode':
                        key = 'from_attributes'
                    elif key == 'schema_extra':
                        key = 'json_schema_extra'
                    
                    options.append(f'{key}={value}')
            
            if options:
                config_str = ', '.join(options)
                return f'{indent}model_config = ConfigDict({config_str})'
            else:
                return f'{indent}model_config = ConfigDict()'
        
        content = re.sub(pattern2, config_replacer, content)
        
        # 如果内容发生了变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 修复了文件: {file_path}")
            return True
        else:
            print(f"⏭️  跳过文件: {file_path} (无需修复)")
            return False
            
    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时出错: {e}")
        return False

def main():
    """主函数"""
    # 需要处理的目录
    target_dirs = [
        'app/shared',
        'app/modules'
    ]
    
    fixed_files = 0
    total_files = 0
    
    for target_dir in target_dirs:
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    total_files += 1
                    if fix_pydantic_config(file_path):
                        fixed_files += 1
    
    print(f"\n🎉 修复完成! 处理了 {total_files} 个文件，修复了 {fixed_files} 个文件")

if __name__ == '__main__':
    main()