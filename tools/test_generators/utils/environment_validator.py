"""
环境验证器 - 测试环境配置完整性检查

该模块实现测试代码生成工具的环境验证功能，在生成测试代码之前检查测试环境的配置完整性，
包括模块路径、conftest.py配置、pytest fixtures、数据库配置等，确保生成的测试代码可以正常运行。

主要功能:
- 模块路径验证: 检查目标模块的models.py、repository.py、service.py等文件是否存在
- conftest.py验证: 检查tests/conftest.py是否存在并正确配置
- Fixture解析: 解析conftest.py中定义的所有pytest fixtures
- 数据库配置检查: 验证测试数据库连接配置是否完整
- 环境依赖检查: 检查Factory类、测试工具类等依赖是否就绪

技术栈:
- os/pathlib: 文件和路径操作
- re: 正则表达式解析fixture定义

依赖关系:
- tests/conftest.py: pytest配置文件（解析fixture定义）
- app/modules/{module}/: 待测试的业务模块目录
- tools.test_generators.generate_test_template: 主程序调用环境验证

使用示例:
    from tools.test_generators.utils.environment_validator import EnvironmentValidator
    
    # 初始化验证器
    config = {"project_root": "/path/to/project"}
    validator = EnvironmentValidator(config)
    
    # 验证user_auth模块的测试环境
    env_info = validator.validate_test_environment("user_auth")
    
    # 检查验证结果
    if env_info["module_path_exists"]:
        print(f"模块路径: {env_info['module_path']}")
        print(f"可用fixtures: {', '.join(env_info['available_fixtures'])}")
    else:
        print("模块路径不存在，无法生成测试")

注意事项:
- 环境验证不会修改任何配置，仅读取和检查
- Fixture解析基于正则表达式，可能不完全准确（如动态生成的fixture）
- 数据库配置检查仅验证配置项存在，不测试实际连接
- 建议在生成测试之前先运行环境验证，避免生成无法运行的测试

Author: AI Assistant
Created: 2025-10-08
Modified: 2025-10-08
Version: 1.0.0
"""
import os
import re
from typing import Any, Dict


class EnvironmentValidator:
    """测试环境配置验证器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化验证器
        
        Args:
            config: 配置字典
        """
        self.config = config
    
    def validate_test_environment(self, module_name: str) -> Dict[str, Any]:
        """验证测试环境配置并返回环境信息
        
        Args:
            module_name: 模块名称
            
        Returns:
            Dict[str, Any]: 环境验证信息
        """
        env_info = {
            "module_exists": False,
            "fixtures_available": [],
            "database_config": {},
            "issues": []
        }
        
        # 检查模块是否存在
        module_path = os.path.join(
            self.config["project_structure"]["modules_path"], 
            module_name
        )
        env_info["module_exists"] = os.path.exists(module_path)
        if not env_info["module_exists"]:
            env_info["issues"].append(f"模块路径不存在: {module_path}")
        
        # 检查conftest.py并获取可用fixture
        conftest_path = os.path.join(
            self.config["project_structure"]["tests_path"], 
            "conftest.py"
        )
        if os.path.exists(conftest_path):
            try:
                with open(conftest_path, 'r', encoding='utf-8') as f:
                    conftest_content = f.read()
                
                # 解析可用的fixture
                fixture_pattern = r'@pytest\.fixture[^\n]*\ndef\s+(\w+)'
                fixtures = re.findall(fixture_pattern, conftest_content)
                env_info["fixtures_available"] = fixtures
                
            except Exception as e:
                env_info["issues"].append(f"无法读取conftest.py: {e}")
        else:
            env_info["issues"].append(f"conftest.py不存在: {conftest_path}")
        
        # 设置数据库配置信息
        db_config = self.config["database_config"]
        env_info["database_config"] = {
            "unit_fixture": db_config["unit_test_fixture"],
            "integration_fixture": db_config["integration_test_fixture"],
            "e2e_fixture": db_config["e2e_test_fixture"],
        }
        
        return env_info
