"""
库存管理模块代码验证

验证新实现的代码是否符合Python语法和架构要求
"""

import sys
import ast
from pathlib import Path

def verify_python_syntax(file_path: str) -> bool:
    """验证Python文件语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 解析AST
        ast.parse(source)
        return True
    except SyntaxError as e:
        print(f"❌ 语法错误 {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误 {file_path}: {e}")
        return False

def check_architecture_compliance(file_path: str) -> bool:
    """检查架构合规性"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        violations = []
        
        # 检查是否还在使用product_id
        if 'product_id' in content and file_path.endswith('.py'):
            # 排除注释中的说明
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'product_id' in line and not line.strip().startswith('#') and not line.strip().startswith('"""'):
                    if 'product_id' in line:
                        violations.append(f"第{i}行仍在使用product_id: {line.strip()}")
        
        # 检查是否正确使用sku_id
        if 'inventory' in file_path.lower() and 'sku_id' not in content:
            violations.append("库存管理文件中未找到sku_id引用")
        
        if violations:
            print(f"❌ 架构违规 {file_path}:")
            for violation in violations:
                print(f"   {violation}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 检查失败 {file_path}: {e}")
        return False

def verify_inventory_module():
    """验证库存管理模块"""
    print("🔍 库存管理模块代码验证")
    print("=" * 50)
    
    # 要验证的文件列表
    inventory_files = [
        "E:/ecommerce_platform/app/modules/inventory_management/models.py",
        "E:/ecommerce_platform/app/modules/inventory_management/schemas.py", 
        "E:/ecommerce_platform/app/modules/inventory_management/router.py",
        "E:/ecommerce_platform/app/modules/inventory_management/service.py",
        "E:/ecommerce_platform/docs/modules/inventory-management/api-spec.md"
    ]
    
    all_passed = True
    
    for file_path in inventory_files:
        if Path(file_path).exists():
            print(f"📁 检查文件: {Path(file_path).name}")
            
            # Python文件检查语法
            if file_path.endswith('.py'):
                if verify_python_syntax(file_path):
                    print(f"  ✅ 语法正确")
                else:
                    all_passed = False
                    continue
            
            # 检查架构合规性
            if check_architecture_compliance(file_path):
                print(f"  ✅ 架构合规")
            else:
                all_passed = False
        else:
            print(f"❌ 文件不存在: {file_path}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 所有验证通过！")
        print("📋 库存管理模块代码符合架构要求")
        return True
    else:
        print("❌ 发现问题，需要修复")
        return False

def check_api_endpoints():
    """检查API端点定义"""
    print("\n🔗 API端点架构验证")
    print("-" * 30)
    
    try:
        with open("E:/ecommerce_platform/app/modules/inventory_management/router.py", 'r', encoding='utf-8') as f:
            router_content = f.read()
        
        # 检查关键端点是否存在且使用正确的参数
        expected_endpoints = [
            ("/stock/{sku_id}", "sku_id"),
            ("/stock/batch", "sku_ids"),
            ("/reserve", "sku_id"),
            ("/deduct", "sku_id"),
            ("/adjust/{sku_id}", "sku_id")
        ]
        
        for endpoint, param in expected_endpoints:
            if endpoint in router_content:
                print(f"  ✅ 端点存在: {endpoint}")
            else:
                print(f"  ❌ 端点缺失: {endpoint}")
                return False
        
        # 确认没有使用product_id
        if 'product_id' in router_content:
            print("  ❌ 仍在使用product_id参数")
            return False
        
        print("  ✅ 所有API端点使用sku_id架构")
        return True
        
    except Exception as e:
        print(f"  ❌ 检查API端点失败: {e}")
        return False

def main():
    """主验证函数"""
    print("🚀 库存管理模块完整性验证")
    print("🎯 验证目标: 100%符合架构设计要求")
    print("=" * 60)
    
    # 验证代码
    code_ok = verify_inventory_module()
    
    # 验证API
    api_ok = check_api_endpoints()
    
    # 总结
    print("\n" + "=" * 60)
    if code_ok and api_ok:
        print("🎉 库存管理模块验证完成!")
        print("✅ 代码语法正确")
        print("✅ 架构设计合规") 
        print("✅ API端点规范")
        print("✅ Product-SKU分离原则遵循")
        print("\n📋 模块已100%符合系统架构设计要求")
        return 0
    else:
        print("❌ 验证失败，需要修复以下问题:")
        if not code_ok:
            print("   - 代码语法或架构合规性问题")
        if not api_ok:
            print("   - API端点定义问题")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)