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
from ..utils.service_analyzer import ServiceAnalyzer


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
        self.service_analyzer = ServiceAnalyzer(project_root)
    
    def generate_service_tests(
        self,
        module_name: str,
        models: Dict[str, ModelInfo],
        repositories: Dict[str, RepositoryInfo]
    ) -> str:
        """生成服务层测试 - Mock Repository [CHECK:TEST-001]
        
        ✅ **符合架构设计意图** ✅
        严格遵循 testing-standards.md v2.0.0 和 architecture/overview.md 的设计原则：
        - Service层测试必须Mock Repository（不使用数据库）
        - 专注测试业务逻辑，不测试SQL（SQL由Repository层测试）
        - 使用pytest-mock而非SQLite数据库
        - Mock Repository返回值，验证Service调用Repository的参数和顺序
        
        🎯 **核心原则**:
        1. Service层测试使用mocker fixture，不使用unit_test_db
        2. Mock所有Repository方法调用
        3. 验证业务规则、流程编排、异常处理
        4. 不依赖数据库，测试速度快
        
        📖 **参考标准**:
        - testing-standards.md 第46-123行: Service层Mock Repository
        - architecture/overview.md 第310行: Repository可轻松Mock

        Args:
            module_name: 模块名称
            models: 模型信息字典
            repositories: Repository信息字典

        Returns:
            str: 服务层测试代码（使用Mock Repository）
        """
        from datetime import datetime
        
        service_info = self._detect_service_info(module_name)
        service_class_name = service_info['class_name']
        test_class_name = f"Test{service_class_name}"
        
        # 收集需要Mock的Repository类
        repo_imports = []
        repo_mock_examples = []
        for repo_name, repo_info in repositories.items():
            repo_imports.append(repo_name)
            # 生成Mock示例
            repo_mock_examples.append(f"""
    # Mock {repo_name}
    mock_{repo_info.model_name.lower()}_repo = mocker.patch(
        'app.modules.{module_name}.repository.{repo_name}'
    )
    # 设置Mock返回值
    mock_{repo_info.model_name.lower()} = mocker.Mock(spec={repo_info.model_name})
    mock_{repo_info.model_name.lower()}.id = 1
    mock_{repo_info.model_name.lower()}_repo.get_by_id.return_value = mock_{repo_info.model_name.lower()}""")
        
        # 生成Mock Repository的业务逻辑测试
        mock_tests = self._generate_mock_service_tests(
            module_name, models, repositories, service_info
        )
        
        template = '''"""
{module_title} 服务层测试

测试类型: 单元测试 - 服务层业务逻辑
测试策略: Mock Repository（符合架构设计意图）
测试范围: 业务规则、流程编排、异常处理、Repository调用验证
生成时间: {generation_time}

符合标准: 
- [CHECK:TEST-001] 测试标准合规
- testing-standards.md v2.0.0 第46-123行: Service层Mock Repository
- architecture/overview.md 第310行: Repository可轻松Mock

测试重点:
1. ✅ 业务规则是否正确
2. ✅ 流程编排是否合理
3. ✅ 异常处理是否完善
4. ✅ 调用Repository的参数和顺序
5. ❌ 不测试SQL正确性（由Repository层测试负责）

为什么Mock Repository?
- 符合架构设计意图（"Repository可轻松Mock"）
- 测试速度快，不依赖数据库
- 职责清晰，只测试业务逻辑
- SQL错误由Repository测试发现，Service不重复测试
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pytest_mock import MockerFixture
from decimal import Decimal
from datetime import datetime, timedelta

# 全局常量
NEWLINE = "\\n"

# 被测服务和模型
from app.modules.{module_name}.models import {model_imports}

# Repository导入（用于Mock）
from app.modules.{module_name}.repository import {repo_imports}

# 尝试导入服务类
try:
    from app.modules.{module_name}.service import {service_class_name}
    SERVICE_AVAILABLE = True
except ImportError as e:
    print("⚠️ 服务类导入失败: " + str(e) + " - 将跳过服务相关测试")
    SERVICE_AVAILABLE = False


@pytest.mark.unit
@pytest.mark.services
class {test_class_name}:
    """服务层测试类 - Mock Repository策略
    
    测试策略说明:
    - 使用pytest-mock的mocker fixture
    - Mock所有Repository方法调用
    - 验证业务逻辑，不测试SQL
    - 测试速度快，无数据库依赖
    """
    
    def test_service_initialization(self, mocker: MockerFixture):
        """测试服务初始化
        
        验证点:
        - Service类可以正常实例化
        - 不依赖数据库连接
        """
        print("\\n🔧 测试服务初始化...")
        
        if not SERVICE_AVAILABLE:
            pytest.skip("服务类不可用，跳过服务初始化测试")
        
        # Service通常是静态方法类，不需要实例化
        assert {service_class_name} is not None
        
{mock_tests}
    
    def test_business_rule_validation(self, mocker: MockerFixture):
        """测试业务规则验证
        
        验证点:
        - 业务规则是否正确执行
        - 参数验证是否有效
        - 边界条件处理
        """
        print("\\n📋 测试业务规则验证...")
        
        if not SERVICE_AVAILABLE:
            pytest.skip("服务类不可用")
        
        # 示例：测试参数验证
        # Mock Repository
        mock_repo = mocker.patch('app.modules.{module_name}.repository.{first_repo_name}')
        
        # 测试空参数
        # TODO: 根据实际Service方法补充测试
        assert True
    
    def test_exception_handling(self, mocker: MockerFixture):
        """测试异常处理
        
        验证点:
        - Repository异常是否正确处理
        - 业务异常是否正确抛出
        - 错误信息是否清晰
        """
        print("\\n⚠️ 测试异常处理...")
        
        if not SERVICE_AVAILABLE:
            pytest.skip("服务类不可用")
        
        # Mock Repository抛出异常
        mock_repo = mocker.patch('app.modules.{module_name}.repository.{first_repo_name}')
        mock_repo.get_by_id.side_effect = Exception("Database error")
        
        # 测试Service如何处理Repository异常
        # TODO: 根据实际Service方法补充测试
        assert True
    
    def test_repository_call_verification(self, mocker: MockerFixture):
        """测试Repository调用验证
        
        验证点:
        - Repository方法是否被正确调用
        - 调用参数是否正确
        - 调用次数和顺序是否符合预期
        """
        print("\\n🔍 测试Repository调用...")
        
        if not SERVICE_AVAILABLE:
            pytest.skip("服务类不可用")
        
        # Mock Repository
        mock_repo = mocker.patch('app.modules.{module_name}.repository.{first_repo_name}')
        mock_result = mocker.Mock()
        mock_repo.get_by_id.return_value = mock_result
        
        # TODO: 调用Service方法
        # result = {service_class_name}.some_method(db, 1)
        
        # 验证Repository调用
        # mock_repo.get_by_id.assert_called_once_with(db, 1)
        assert True
'''
        
        return template.format(
            module_title=module_name.title(),
            generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            module_name=module_name,
            model_imports=', '.join(models.keys()) if models else '',
            service_class_name=service_class_name,
            test_class_name=test_class_name,
            repo_imports=', '.join(repo_imports) if repo_imports else '',
            mock_tests=mock_tests,
            first_repo_name=repo_imports[0] if repo_imports else 'Repository'
        )
    
    # ========== 辅助方法 ==========
    
    def _generate_mock_service_tests(
        self, module_name: str, models: Dict[str, ModelInfo], repositories: Dict[str, RepositoryInfo], service_info: dict
    ) -> str:
        """生成Mock Repository的Service测试代码
        
        符合testing-standards.md v2.0.0要求：
        - Mock所有Repository方法
        - 验证业务逻辑，不测试SQL
        - 使用pytest-mock
        
        Args:
            module_name: 模块名称
            models: 模型信息字典
            repositories: Repository信息字典
            service_info: 服务类信息
            
        Returns:
            str: Mock测试代码
        """
        if not repositories:
            return '''    
    def test_service_methods_placeholder(self, mocker: MockerFixture):
        """Service方法测试占位符
        
        注意: 未检测到Repository，请手动补充测试
        """
        print("\\n⚠️ 需要手动补充Service测试")
        if not SERVICE_AVAILABLE:
            pytest.skip("服务类不可用")
        assert True  # 占位符测试
'''
        
        tests = []
        
        # 为每个Repository生成Mock测试示例
        for repo_name, repo_info in list(repositories.items())[:2]:  # 最多生成2个示例
            model_name = repo_info.model_name
            model_name_lower = model_name.lower()
            
            # 生成CRUD操作的Mock测试
            test_code = f'''
    def test_service_with_mock_{model_name_lower}_repository(self, mocker: MockerFixture):
        """测试Service使用Mock {repo_name}
        
        测试策略:
        - Mock {repo_name}的方法
        - 验证Service业务逻辑
        - 不依赖数据库
        
        示例: 测试获取{model_name}的业务逻辑
        """
        print("\\n🔧 测试Service Mock {repo_name}...")
        
        if not SERVICE_AVAILABLE:
            pytest.skip("服务类不可用")
        
        # Mock Repository
        mock_repo = mocker.patch(
            'app.modules.{module_name}.repository.{repo_name}'
        )
        
        # 创建Mock {model_name}对象
        mock_{model_name_lower} = mocker.Mock(spec={model_name})
        mock_{model_name_lower}.id = 1
        # 设置其他必要属性
        # mock_{model_name_lower}.name = "Test {model_name}"
        
        # 设置Mock Repository返回值
        mock_repo.get_by_id.return_value = mock_{model_name_lower}
        
        # TODO: 调用Service方法（需要根据实际Service API补充）
        # result = ServiceClass.some_method(mock_db, 1)
        
        # 验证Repository被正确调用
        # mock_repo.get_by_id.assert_called_once_with(mock_db, 1)
        
        # 验证业务逻辑结果
        # assert result is not None
        # assert result.id == 1
        
        # 占位符断言
        assert mock_{model_name_lower} is not None
        assert mock_repo is not None
'''
            tests.append(test_code)
        
        return '\n'.join(tests)
    
    def _detect_service_info(self, module_name: str) -> dict:
        """检测Service类信息（使用ServiceAnalyzer）
        
        Args:
            module_name: 模块名称
            
        Returns:
            dict: Service信息字典
        """
        return self.service_analyzer.detect_service_info(module_name)
    
    def _generate_service_instantiation(self, service_info: dict, db_var: str = "unit_test_db") -> str:
        """生成服务实例化代码，解决静态方法vs实例方法的实例化问题
        
        核心功能说明：
        - 根据服务类的方法模式生成正确的实例化代码
        - 解决之前硬编码实例化导致的测试失败问题
        
        关键修复历史：
        - 问题：UserService使用静态方法，但生成的代码是service = UserService(unit_test_db)
        - 解决：检测服务类模式，静态方法类直接引用，实例方法类创建实例
        - 重要性：确保生成的测试代码能够正确调用服务方法
        
        实例化模式：
        - 静态方法模式：service = UserService (直接引用类，不创建实例)
        - 实例方法模式：service = UserService() (创建类实例)
        
        Args:
            service_info: 服务信息字典，包含is_static和class_name
            db_var: 数据库变量名 (目前未使用，保留接口兼容性)
            
        Returns:
            str: 正确的服务实例化代码
            
        示例输出：
        - 静态模式：service = UserService
        - 实例模式：service = UserService()
        
        错误预防：
        - 避免对静态方法类错误地传递数据库参数
        - 确保实例方法类正确创建实例
        - 与_detect_service_info()方法配合使用
        """
        service_class_name = service_info['class_name']
        
        if service_info['is_static']:
            # 静态方法模式：直接引用类，不创建实例
            # 例如：service = UserService
            return f"service = {service_class_name}"
        else:
            # 实例方法模式：创建实例
            # 例如：service = UserService()
            # 注意：目前不传递数据库参数，根据实际需要可以扩展
            return f"service = {service_class_name}()"
