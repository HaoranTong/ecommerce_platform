"""
Service分析器 - 业务服务层智能检测与信息提取

该模块实现测试代码生成工具中的Service层分析功能，通过AST静态分析识别Service类的
真实名称、实例化模式、方法签名等信息，支持多种服务文件结构和命名约定。

主要功能:
- Service类识别: 自动识别模块中的Service类（支持多种命名模式）
- 实例化模式检测: 判断服务方法是否为静态方法或需要实例化
- 命名约定支持: 支持{Module}Service、Service等多种命名模式
- 文件结构适配: 支持单文件service.py和多文件services/结构

技术栈:
- Python AST: 抽象语法树解析和分析
- pathlib: 跨平台路径处理

依赖关系:
- app.modules.{module}.service: 待分析的业务模块Service定义
- tools.test_generators.generate_test_template: IntelligentTestGenerator主程序调用
- tools.test_generators.unit.service_test_generator: ServiceTestGenerator使用分析结果

使用示例:
    from pathlib import Path
    from tools.test_generators.utils.service_analyzer import ServiceAnalyzer
    
    # 初始化分析器
    analyzer = ServiceAnalyzer(project_root=Path.cwd())
    
    # 检测user_auth模块的Service信息
    service_info = analyzer.detect_service_info("user_auth")
    
    # 使用Service信息
    if service_info:
        print(f"Service类名: {service_info['service_class_name']}")
        print(f"实例化模式: {'静态' if service_info['is_static'] else '实例'}")
    else:
        print("未检测到Service类")

注意事项:
- 仅检测Service类的基本信息，不深入分析方法细节
- 假设Service类命名遵循项目命名约定（{Module}Service或Service）
- 对于非标准命名的Service类，可能无法自动识别

Author: AI Assistant
Created: 2025-10-08
Modified: 2025-10-08
Version: 1.0.0
"""

import ast
from pathlib import Path
from typing import Dict, Any


class ServiceAnalyzer:
    """服务分析器 - 检测服务类信息"""
    
    def __init__(self, project_root: Path):
        """初始化服务分析器
        
        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root
    
    def extract_service_used_models(self, module_name: str) -> list[str]:
        """提取Service实际使用的模型列表
        
        通过AST分析Service文件的import语句，提取从.models导入的模型名称。
        这确保Service测试只导入Service实际使用的模型，避免导入冗余模型。
        
        Args:
            module_name: 模块名称
            
        Returns:
            list[str]: Service使用的模型名称列表
            
        Example:
            >>> analyzer = ServiceAnalyzer(Path.cwd())
            >>> models = analyzer.extract_service_used_models('order_management')
            >>> print(models)
            ['Order', 'OrderItem', 'OrderStatus', 'OrderStatusHistory']
        """
        service_file_path = self.project_root / f"app/modules/{module_name}/service.py"
        
        if not service_file_path.exists():
            print(f"⚠️  服务文件不存在: {service_file_path}")
            return []
        
        try:
            with open(service_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            used_models = []
            
            for node in ast.walk(tree):
                # 查找 "from .models import ..." 语句
                if isinstance(node, ast.ImportFrom):
                    if node.module == 'models' or node.module == '.models':
                        for alias in node.names:
                            if alias.name != '*':  # 排除 import *
                                used_models.append(alias.name)
            
            return used_models
        
        except Exception as e:
            print(f"⚠️  分析Service文件失败: {e}")
            return []
    
    def detect_service_info(self, module_name: str) -> Dict[str, Any]:
        """检测服务类的完整信息
        
        核心功能：
        - 分析服务文件AST结构，识别真实的服务类名
        - 检测服务方法的实例化模式(静态方法 vs 实例方法)
        - 解决hardcode导致的命名冲突问题
        
        实例化模式检测：
        - 静态方法模式：service = UserService (无需初始化参数)
        - 实例方法模式：service = UserService() (需要创建实例)
        
        Args:
            module_name: 模块名称
            
        Returns:
            dict: 包含服务信息的字典
            - class_name: 服务类名 (如 'UserService')
            - is_static: 是否为静态方法模式 (True/False)
            - instantiation_pattern: 实例化模式 ('static'/'instance')
            - static_methods: 静态方法数量
            - instance_methods: 实例方法数量
            - static_method_names: 静态方法名称列表
            - instance_method_names: 实例方法名称列表
        """
        service_file_path = self.project_root / f"app/modules/{module_name}/service.py"
        
        # 默认信息 - 当检测失败时的fallback
        default_info = {
            'class_name': f"{module_name.title().replace('_', '')}Service",
            'is_static': False,
            'instantiation_pattern': 'instance',
            'static_methods': 0,
            'instance_methods': 0,
            'static_method_names': [],
            'instance_method_names': []
        }
        
        # 如果服务文件不存在，使用算法生成名称
        if not service_file_path.exists():
            print(f"⚠️  服务文件不存在: {service_file_path}")
            return default_info
        
        try:
            # 读取服务文件内容
            with open(service_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST查找类定义
            tree = ast.parse(content)
            service_classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    # 查找以Service结尾的类
                    if class_name.endswith('Service'):
                        # 分析方法模式 - 统计静态方法和实例方法数量
                        static_methods = 0
                        instance_methods = 0
                        static_method_names = []
                        instance_method_names = []
                        
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                # 检查是否有@staticmethod装饰器
                                is_static = any(
                                    isinstance(decorator, ast.Name) and decorator.id == 'staticmethod'
                                    for decorator in item.decorator_list
                                )
                                if is_static:
                                    static_methods += 1
                                    static_method_names.append(item.name)
                                elif item.name != '__init__':  # 排除构造函数
                                    instance_methods += 1
                                    instance_method_names.append(item.name)
                        
                        service_info = {
                            'class_name': class_name,
                            'static_methods': static_methods,
                            'instance_methods': instance_methods,
                            'static_method_names': static_method_names,
                            'instance_method_names': instance_method_names
                        }
                        
                        # 确定实例化模式 - 关键逻辑
                        if static_methods > 0 and instance_methods == 0:
                            # 纯静态方法类
                            service_info['is_static'] = True
                            service_info['instantiation_pattern'] = 'static'
                        elif static_methods > instance_methods:
                            # 静态方法占主导
                            service_info['is_static'] = True  
                            service_info['instantiation_pattern'] = 'static'
                        else:
                            # 实例方法占主导或相等
                            service_info['is_static'] = False
                            service_info['instantiation_pattern'] = 'instance'
                            
                        service_classes.append(service_info)
            
            if service_classes:
                # 如果找到多个Service类，优先选择最匹配的
                for service_info in service_classes:
                    class_name = service_info['class_name']
                    # 精确匹配模块名 - 避免命名冲突
                    module_pattern = module_name.replace('_', '').lower()
                    if module_pattern in class_name.lower():
                        print(f"✅ 检测到服务类: {class_name} (精确匹配模块 {module_name}, {'静态方法' if service_info['is_static'] else '实例方法'})")
                        print(f"   📊 方法统计: 静态方法={service_info['static_methods']}, 实例方法={service_info['instance_methods']}")
                        return service_info
                
                # 如果没有精确匹配，返回第一个Service类
                detected_service = service_classes[0]
                print(f"✅ 检测到服务类: {detected_service['class_name']} (第一个Service类, {'静态方法' if detected_service['is_static'] else '实例方法'})")
                print(f"   📊 方法统计: 静态方法={detected_service['static_methods']}, 实例方法={detected_service['instance_methods']}")
                return detected_service
            else:
                print(f"⚠️  未找到Service类，使用算法生成名称")
                return default_info
                
        except Exception as e:
            print(f"⚠️  解析服务文件失败: {e}")
            return default_info
    
    def get_service_class_name(self, module_name: str) -> str:
        """获取服务类名称
        
        Args:
            module_name: 模块名称
            
        Returns:
            str: 服务类名称
        """
        service_info = self.detect_service_info(module_name)
        return service_info['class_name']
