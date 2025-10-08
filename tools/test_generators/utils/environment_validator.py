"""
环境验证器 - 测试环境配置验证

职责：
1. 验证模块路径存在性
2. 检查conftest.py配置
3. 解析可用的pytest fixtures
4. 验证数据库配置

版本: v1.0
创建时间: 2025-10-08
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
