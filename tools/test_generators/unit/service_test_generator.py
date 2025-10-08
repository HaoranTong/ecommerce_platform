"""
Service测试生成器 - Service层Mock测试

职责：
生成Service层的Mock测试代码，包括：
1. Service初始化测试
2. Mock Repository测试 - 使用pytest-mock
3. 业务逻辑验证测试
4. 异常处理测试
5. Repository调用验证测试

测试策略：
- 必须Mock Repository（不使用数据库）
- 使用pytest-mock的mocker fixture
- 专注测试业务逻辑
- 符合testing-standards.md v2.0.0第46-123行

版本: v1.0
创建时间: 2025-10-08
"""
from pathlib import Path
from typing import Dict
from ..core import ModelInfo, RepositoryInfo


class ServiceTestGenerator:
    """Service测试生成器"""
    
    def __init__(self, project_root: Path, config: Dict, main_generator=None):
        """初始化生成器
        
        Args:
            project_root: 项目根目录
            config: 配置字典
            main_generator: 主生成器实例（临时使用）
        """
        self.project_root = project_root
        self.config = config
        self.main_generator = main_generator
    
    def generate_service_tests(
        self,
        module_name: str,
        models: Dict[str, ModelInfo],
        repositories: Dict[str, RepositoryInfo]
    ) -> str:
        """生成Service测试代码（主入口）
        
        Args:
            module_name: 模块名称
            models: 模型信息字典
            repositories: Repository信息字典
            
        Returns:
            生成的测试代码字符串
        """
        # 🔄 重构标记：待从主程序迁移实现
        # 主程序方法：_generate_service_tests() 第4622行
        # 预计代码量：~900行
        # 关键：必须使用Mock Repository，不能使用unit_test_db
        if self.main_generator:
            return self.main_generator._generate_service_tests(module_name, models, repositories)
        return f"# Service测试占位符 - {module_name}"
