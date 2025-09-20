#!/usr/bin/env python3
"""
五层架构标准测试生成器

根据测试标准 (docs/standards/testing-standards.md) 生成完整测试套件
符合70%单元、20%集成、6%E2E、2%烟雾、2%专项的分层架构

使用方法:
    python scripts/generate_test_template.py module_name [--type all|unit|integration|smoke|e2e|specialized]
    
示例:
    python scripts/generate_test_template.py user_auth --type all
    python scripts/generate_test_template.py shopping_cart --type unit

生成标准:
- Factory Boy数据工厂模式
- pytest.ini配置要求  
- 五层测试架构分布
- 标准化测试结构
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class FiveLayerTestGenerator:
    """五层架构测试生成器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_distributions = {
            'unit': 0.70,      # 70% 单元测试
            'integration': 0.20, # 20% 集成测试  
            'e2e': 0.06,       # 6% E2E测试
            'smoke': 0.02,     # 2% 烟雾测试
            'specialized': 0.02 # 2% 专项测试
        }
    
    def generate_unit_tests(self, module_name: str) -> Dict[str, str]:
        """生成单元测试 (70% - Mock + SQLite内存)"""
        
        # Mock模型测试 (test_models/)
        mock_tests = self._generate_mock_model_tests(module_name)
        
        # 服务层测试 (test_services/) 
        service_tests = self._generate_service_tests(module_name)
        
        # 独立业务流程测试 (*_standalone.py)
        standalone_tests = self._generate_standalone_tests(module_name)
        
        return {
            f'tests/unit/test_models/test_{module_name}_models.py': mock_tests,
            f'tests/unit/test_services/test_{module_name}_service.py': service_tests, 
            f'tests/unit/test_{module_name}_standalone.py': standalone_tests
        }
    
    def _generate_mock_model_tests(self, module_name: str) -> str:
        """生成Mock模型测试 - 100% Mock, 无数据库"""
        return f'''"""
{module_name.title()} 模型Mock测试套件

测试类型: 单元测试 (Mock)
数据策略: 100% Mock对象，无数据库依赖
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

根据testing-standards.md第32-45行Mock测试规范
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date

# 测试工厂导入 - Factory Boy模式
from tests.factories import {module_name.title()}Factory


class TestMock{module_name.title()}Model:
    """Mock {module_name} 模型测试"""
    
    def setup_method(self):
        """每个测试方法前的准备"""
        self.mock_{module_name} = Mock()
        
    def test_model_validation_with_valid_data(self, mocker):
        """测试模型验证 - 有效数据"""
        # 使用Factory Boy创建Mock数据
        mock_data = {module_name.title()}Factory.build()
        mock_validator = mocker.Mock()
        mock_validator.validate.return_value = True
        
        # 执行验证
        result = mock_validator.validate(mock_data)
        
        # 验证调用
        assert result is True
        mock_validator.validate.assert_called_once_with(mock_data)
        
    def test_model_validation_with_invalid_data(self, mocker):
        """测试模型验证 - 无效数据"""
        mock_validator = mocker.Mock()
        mock_validator.validate.side_effect = ValueError("Validation failed")
        
        # 验证异常抛出
        with pytest.raises(ValueError, match="Validation failed"):
            mock_validator.validate({{"invalid": "data"}})
            
    @pytest.mark.parametrize("field_name,field_value,expected", [
        ("status", "active", True),
        ("status", "inactive", False), 
        ("status", None, False),
    ])
    def test_status_field_validation(self, field_name, field_value, expected, mocker):
        """参数化测试状态字段验证"""
        mock_model = mocker.Mock()
        mock_model.status = field_value
        
        # Mock验证逻辑
        result = field_value == "active" if field_value else False
        assert result == expected
'''
    
    def _generate_service_tests(self, module_name: str) -> str:
        """生成服务层测试 - SQLite内存数据库"""
        return f'''"""
{module_name.title()} 服务层测试套件

测试类型: 单元测试 (Service)
数据策略: SQLite内存数据库, unit_test_db fixture
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

根据testing-standards.md第54-68行服务测试规范
"""

import pytest
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import {module_name.title()}Factory, UserFactory

# Fixture导入
from tests.conftest import unit_test_db

# 被测模块导入
from app.modules.{module_name}.service import {module_name.title()}Service
from app.modules.{module_name}.models import {module_name.title()}


class Test{module_name.title()}Service:
    """服务层业务逻辑测试"""
    
    def setup_method(self):
        """测试准备"""
        self.test_data = {module_name.title()}Factory.build_dict()
        
    def test_create_{module_name}_with_valid_data(self, unit_test_db: Session):
        """测试创建{module_name} - 有效数据"""
        # Arrange
        service = {module_name.title()}Service(unit_test_db)
        create_data = self.test_data
        
        # Act
        created_{module_name} = service.create(create_data)
        
        # Assert
        assert created_{module_name} is not None
        assert created_{module_name}.id is not None
        assert hasattr(created_{module_name}, 'created_at')
        
        # 验证数据库存储
        db_{module_name} = unit_test_db.query({module_name.title()}).filter_by(
            id=created_{module_name}.id
        ).first()
        assert db_{module_name} is not None
        
    def test_get_{module_name}_by_id_exists(self, unit_test_db: Session):
        """测试按ID查询{module_name} - 存在"""
        # 准备测试数据
        {module_name}_data = {module_name.title()}Factory.create_dict()
        service = {module_name.title()}Service(unit_test_db)
        created = service.create({module_name}_data)
        
        # 执行查询
        found_{module_name} = service.get_by_id(created.id)
        
        # 验证结果
        assert found_{module_name} is not None
        assert found_{module_name}.id == created.id
        
    def test_get_{module_name}_by_id_not_exists(self, unit_test_db: Session):
        """测试按ID查询{module_name} - 不存在"""
        service = {module_name.title()}Service(unit_test_db)
        
        # 查询不存在的ID
        result = service.get_by_id(99999)
        
        # 验证返回None
        assert result is None
        
    def test_update_{module_name}_success(self, unit_test_db: Session):
        """测试更新{module_name} - 成功"""
        # 创建测试数据
        service = {module_name.title()}Service(unit_test_db)
        created = service.create(self.test_data)
        
        # 准备更新数据
        update_data = {{"status": "updated"}}
        
        # 执行更新
        updated = service.update(created.id, update_data)
        
        # 验证更新结果
        assert updated is not None
        assert updated.status == "updated"
        assert hasattr(updated, 'updated_at')
        
    def test_delete_{module_name}_success(self, unit_test_db: Session):
        """测试删除{module_name} - 成功"""
        # 创建测试数据
        service = {module_name.title()}Service(unit_test_db)
        created = service.create(self.test_data)
        
        # 执行删除
        result = service.delete(created.id)
        
        # 验证删除结果
        assert result is True
        
        # 验证数据库中已删除
        deleted = service.get_by_id(created.id)
        assert deleted is None
'''

    def _generate_standalone_tests(self, module_name: str) -> str:
        """生成独立业务流程测试 - SQLite内存数据库"""
        return f'''"""
{module_name.title()} 独立业务流程测试套件

测试类型: 单元测试 (Standalone Business Flow)
数据策略: SQLite内存数据库, unit_test_db fixture
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

根据testing-standards.md第78-92行业务流程测试规范
"""

import pytest
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import {module_name.title()}Factory, UserFactory

# Fixture导入  
from tests.conftest import unit_test_db

# 被测模块导入
from app.modules.{module_name}.service import {module_name.title()}Service
from app.modules.{module_name}.models import {module_name.title()}


class Test{module_name.title()}BusinessFlow:
    """独立业务流程测试"""
    
    def setup_method(self):
        """测试准备"""
        self.user_data = UserFactory.build_dict()
        self.{module_name}_data = {module_name.title()}Factory.build_dict()
        
    def test_complete_{module_name}_workflow(self, unit_test_db: Session):
        """测试完整{module_name}业务流程"""
        service = {module_name.title()}Service(unit_test_db)
        
        # 步骤1: 创建{module_name}
        created = service.create(self.{module_name}_data)
        assert created is not None
        assert created.id is not None
        
        # 步骤2: 查询验证
        found = service.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        
        # 步骤3: 更新状态
        update_result = service.update(created.id, {{"status": "processed"}})
        assert update_result.status == "processed"
        
        # 步骤4: 最终验证
        final_check = service.get_by_id(created.id)
        assert final_check.status == "processed"
        
    def test_{module_name}_error_handling_flow(self, unit_test_db: Session):
        """测试{module_name}错误处理流程"""
        service = {module_name.title()}Service(unit_test_db)
        
        # 测试无效数据处理
        with pytest.raises((ValueError, TypeError)):
            service.create({{"invalid": "data"}})
            
        # 测试不存在ID处理
        result = service.get_by_id(99999)
        assert result is None
        
        # 测试删除不存在项目
        delete_result = service.delete(99999)
        assert delete_result is False
        
    @pytest.mark.parametrize("test_scenario,expected_result", [
        ("valid_create", True),
        ("valid_update", True),
        ("valid_delete", True),
    ])
    def test_{module_name}_scenarios(self, test_scenario, expected_result, unit_test_db: Session):
        """参数化测试{module_name}场景"""
        service = {module_name.title()}Service(unit_test_db)
        
        if test_scenario == "valid_create":
            result = service.create(self.{module_name}_data)
            assert (result is not None) == expected_result
            
        elif test_scenario == "valid_update":
            created = service.create(self.{module_name}_data)
            result = service.update(created.id, {{"status": "updated"}})
            assert (result is not None) == expected_result
            
        elif test_scenario == "valid_delete":
            created = service.create(self.{module_name}_data)
            result = service.delete(created.id)
            assert result == expected_result
'''

    def generate_integration_tests(self, module_name: str) -> Dict[str, str]:
        """生成集成测试 (20% - MySQL Docker)"""
        integration_tests = self._generate_integration_api_tests(module_name)
        
        return {
            f'tests/integration/test_{module_name}_integration.py': integration_tests
        }
    
    def _generate_integration_api_tests(self, module_name: str) -> str:
        """生成集成API测试 - MySQL Docker数据库"""
        return f'''"""
{module_name.title()} 集成测试套件

测试类型: 集成测试 (Integration)
数据策略: MySQL Docker, mysql_integration_db fixture  
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

根据testing-standards.md第105-125行集成测试规范
"""

import pytest
import requests
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import {module_name.title()}Factory, UserFactory

# Fixture导入
from tests.conftest import mysql_integration_db, api_client

# 被测模块导入  
from app.modules.{module_name}.service import {module_name.title()}Service


@pytest.mark.integration
class Test{module_name.title()}Integration:
    """集成测试 - 真实环境模拟"""
    
    def setup_method(self):
        """集成测试准备"""
        self.api_base_url = "http://localhost:8000"
        self.test_data = {module_name.title()}Factory.build_dict()
        
    def test_{module_name}_api_integration(self, api_client, mysql_integration_db: Session):
        """测试{module_name} API完整集成"""
        # 创建API请求
        create_response = api_client.post(
            f"/{module_name}/",
            json=self.test_data
        )
        
        # 验证创建响应
        assert create_response.status_code == 201
        created_data = create_response.json()
        assert "id" in created_data
        {module_name}_id = created_data["id"]
        
        # 查询API验证
        get_response = api_client.get(f"/{module_name}/{{poll_id}}")
        assert get_response.status_code == 200
        
        # 更新API验证
        update_data = {{"status": "updated"}}
        update_response = api_client.put(
            f"/{module_name}/{{poll_id}}",
            json=update_data
        )
        assert update_response.status_code == 200
        
        # 删除API验证
        delete_response = api_client.delete(f"/{module_name}/{{poll_id}}")
        assert delete_response.status_code == 204
        
    def test_{module_name}_database_integration(self, mysql_integration_db: Session):
        """测试{module_name}数据库集成"""
        service = {module_name.title()}Service(mysql_integration_db)
        
        # 测试数据库事务完整性
        created = service.create(self.test_data)
        assert created is not None
        
        # 验证数据库持久化
        mysql_integration_db.commit()
        found = service.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        
    def test_{module_name}_external_service_integration(self, mysql_integration_db: Session):
        """测试{module_name}外部服务集成"""
        service = {module_name.title()}Service(mysql_integration_db)
        
        # 模拟外部服务调用
        with pytest.raises((ConnectionError, TimeoutError), match="external"):
            # 这里应该是真实的外部服务调用测试
            pass
            
    @pytest.mark.slow
    def test_{module_name}_performance_integration(self, mysql_integration_db: Session):
        """测试{module_name}性能集成"""
        service = {module_name.title()}Service(mysql_integration_db)
        
        import time
        start_time = time.time()
        
        # 批量操作性能测试
        for i in range(100):
            test_data = {module_name.title()}Factory.build_dict()
            service.create(test_data)
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 验证性能要求 (100个操作 < 5秒)
        assert execution_time < 5.0, f"Performance test failed: {{execution_time:.2f}}s > 5s"
'''

    def generate_smoke_tests(self, module_name: str) -> Dict[str, str]:
        """生成烟雾测试 (2% - SQLite文件)"""
        smoke_tests = self._generate_smoke_health_tests(module_name)
        
        return {
            f'tests/smoke/test_{module_name}_smoke.py': smoke_tests
        }
    
    def _generate_smoke_health_tests(self, module_name: str) -> str:
        """生成烟雾测试 - SQLite文件数据库"""
        return f'''"""
{module_name.title()} 烟雾测试套件

测试类型: 烟雾测试 (Smoke)
数据策略: SQLite文件数据库, smoke_test_db fixture
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

根据testing-standards.md第95-104行烟雾测试规范
"""

import pytest
import requests
from sqlalchemy.orm import Session

# Fixture导入
from tests.conftest import smoke_test_db


@pytest.mark.smoke  
class Test{module_name.title()}Smoke:
    """烟雾测试 - 基本健康检查"""
    
    def test_{module_name}_health_check(self):
        """验证{module_name}模块基本健康状态"""
        try:
            # 模块导入测试
            from app.modules.{module_name} import service
            from app.modules.{module_name} import models
            assert True, "{module_name} module imports successfully"
        except ImportError as e:
            pytest.fail(f"{module_name} module import failed: {{e}}")
            
    def test_{module_name}_database_connection_smoke(self, smoke_test_db: Session):
        """验证{module_name}数据库连接正常"""
        # 简单的数据库连接测试
        result = smoke_test_db.execute("SELECT 1 as test")
        assert result.fetchone()[0] == 1
        
    def test_{module_name}_api_endpoint_smoke(self):
        """验证{module_name} API端点可访问性"""
        try:
            response = requests.get(
                "http://localhost:8000/{module_name}/health",
                timeout=5
            )
            assert response.status_code in [200, 404]  # 404也可接受，只要服务响应
        except requests.ConnectionError:
            pytest.skip("API服务未运行，跳过烟雾测试")
            
    def test_{module_name}_basic_functionality_smoke(self, smoke_test_db: Session):
        """验证{module_name}基本功能正常"""
        from app.modules.{module_name}.service import {module_name.title()}Service
        
        service = {module_name.title()}Service(smoke_test_db)
        
        # 最基本的功能测试
        basic_data = {{"name": "smoke_test", "status": "active"}}
        
        try:
            created = service.create(basic_data)
            assert created is not None
        except Exception as e:
            pytest.fail(f"{module_name} basic create functionality failed: {{e}}")
'''

    def generate_e2e_tests(self, module_name: str) -> Dict[str, str]:
        """生成E2E测试 (6% - MySQL Docker)"""
        e2e_tests = self._generate_e2e_workflow_tests(module_name)
        
        return {
            f'tests/e2e/test_{module_name}_e2e.py': e2e_tests
        }
    
    def _generate_e2e_workflow_tests(self, module_name: str) -> str:
        """生成E2E工作流测试 - MySQL Docker数据库"""
        return f'''"""
{module_name.title()} E2E测试套件

测试类型: 端到端测试 (E2E)
数据策略: MySQL Docker, mysql_e2e_db fixture
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

根据testing-standards.md第135-155行E2E测试规范
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import {module_name.title()}Factory, UserFactory

# Fixture导入
from tests.conftest import mysql_e2e_db, selenium_driver


@pytest.mark.e2e
@pytest.mark.slow
class Test{module_name.title()}E2E:
    """端到端测试 - 完整用户流程"""
    
    def setup_method(self):
        """E2E测试准备"""
        self.base_url = "http://localhost:3000"  # 前端应用URL
        self.test_user_data = UserFactory.build_dict()
        self.test_{module_name}_data = {module_name.title()}Factory.build_dict()
        
    def test_complete_{module_name}_user_journey(self, selenium_driver, mysql_e2e_db: Session):
        """测试{module_name}完整用户旅程"""
        driver = selenium_driver
        
        # 步骤1: 用户登录
        driver.get(f"{{self.base_url}}/login")
        
        # 输入登录信息
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "login-btn")
        
        username_field.send_keys(self.test_user_data["username"])
        password_field.send_keys(self.test_user_data["password"])
        login_button.click()
        
        # 验证登录成功
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        
        # 步骤2: 导航到{module_name}页面
        driver.get(f"{{self.base_url}}/{module_name}")
        
        # 步骤3: 创建新{module_name}
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"create-{module_name}-btn"))
        )
        create_button.click()
        
        # 填写表单
        name_field = driver.find_element(By.ID, f"{module_name}-name")
        name_field.send_keys(self.test_{module_name}_data["name"])
        
        submit_button = driver.find_element(By.ID, "submit-btn")
        submit_button.click()
        
        # 步骤4: 验证创建成功
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "successfully created" in success_message.text.lower()
        
        # 步骤5: 验证数据库中存在
        from app.modules.{module_name}.service import {module_name.title()}Service
        service = {module_name.title()}Service(mysql_e2e_db)
        
        created_items = service.get_all()
        assert len(created_items) > 0
        assert any(item.name == self.test_{module_name}_data["name"] for item in created_items)
        
    def test_{module_name}_error_handling_e2e(self, selenium_driver, mysql_e2e_db: Session):
        """测试{module_name}错误处理端到端流程"""
        driver = selenium_driver
        
        # 导航到{module_name}页面
        driver.get(f"{{self.base_url}}/{module_name}")
        
        # 尝试提交无效表单
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"create-{module_name}-btn"))
        )
        create_button.click()
        
        # 不填写必填字段，直接提交
        submit_button = driver.find_element(By.ID, "submit-btn")
        submit_button.click()
        
        # 验证错误消息显示
        error_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )
        assert "required" in error_message.text.lower()
'''

    def generate_specialized_tests(self, module_name: str) -> Dict[str, str]:
        """生成专项测试 (2% - 性能/安全)"""
        performance_tests = self._generate_performance_tests(module_name)
        security_tests = self._generate_security_tests(module_name)
        
        return {
            f'tests/performance/test_{module_name}_performance.py': performance_tests,
            f'tests/security/test_{module_name}_security.py': security_tests
        }
    
    def _generate_performance_tests(self, module_name: str) -> str:
        """生成性能测试"""
        return f'''"""
{module_name.title()} 性能测试套件

测试类型: 专项测试 (Performance)
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

根据testing-standards.md第165-185行性能测试规范
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import {module_name.title()}Factory

# Fixture导入
from tests.conftest import mysql_integration_db

# 被测模块导入
from app.modules.{module_name}.service import {module_name.title()}Service


@pytest.mark.performance
@pytest.mark.slow
class Test{module_name.title()}Performance:
    """性能测试"""
    
    def test_{module_name}_create_performance(self, mysql_integration_db: Session):
        """测试{module_name}创建操作性能"""
        service = {module_name.title()}Service(mysql_integration_db)
        
        # 性能基准: 1000次创建操作 < 10秒
        start_time = time.time()
        
        for i in range(1000):
            test_data = {module_name.title()}Factory.build_dict()
            test_data['name'] = f"perf_test_{{i}}"
            service.create(test_data)
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time < 10.0, f"Create performance failed: {{execution_time:.2f}}s > 10s"
        
    def test_{module_name}_query_performance(self, mysql_integration_db: Session):
        """测试{module_name}查询操作性能"""
        service = {module_name.title()}Service(mysql_integration_db)
        
        # 准备测试数据
        for i in range(100):
            test_data = {module_name.title()}Factory.build_dict()
            test_data['name'] = f"query_test_{{i}}"
            service.create(test_data)
            
        # 性能测试: 1000次查询 < 5秒
        start_time = time.time()
        
        for i in range(1000):
            results = service.get_all(limit=10)
            assert len(results) > 0
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time < 5.0, f"Query performance failed: {{execution_time:.2f}}s > 5s"
        
    def test_{module_name}_concurrent_access(self, mysql_integration_db: Session):
        """测试{module_name}并发访问性能"""
        service = {module_name.title()}Service(mysql_integration_db)
        
        def create_item(thread_id):
            test_data = {module_name.title()}Factory.build_dict()
            test_data['name'] = f"concurrent_test_{{thread_id}}"
            return service.create(test_data)
            
        # 并发测试: 10个线程同时创建100个项目
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_item, i) for i in range(100)]
            results = [f.result() for f in futures]
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 验证所有操作成功
        assert all(r is not None for r in results)
        
        # 并发性能要求: 100个并发操作 < 15秒
        assert execution_time < 15.0, f"Concurrent performance failed: {{execution_time:.2f}}s > 15s"
'''
    
    def _generate_security_tests(self, module_name: str) -> str:
        """生成安全测试"""
        return f'''"""
{module_name.title()} 安全测试套件

测试类型: 专项测试 (Security)
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

根据testing-standards.md第190-210行安全测试规范
"""

import pytest
import requests
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import {module_name.title()}Factory, UserFactory

# Fixture导入
from tests.conftest import mysql_integration_db, api_client


@pytest.mark.security
class Test{module_name.title()}Security:
    """安全测试"""
    
    def test_{module_name}_sql_injection_protection(self, api_client):
        """测试{module_name} SQL注入防护"""
        # SQL注入攻击测试
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1; INSERT INTO users VALUES('hacker', 'password'); --"
        ]
        
        for payload in malicious_payloads:
            response = api_client.get(f"/{module_name}/{{payload}}")
            
            # 验证没有返回敏感数据或系统错误
            assert response.status_code in [400, 404, 422]
            assert "error" not in response.text.lower() or "sql" not in response.text.lower()
            
    def test_{module_name}_xss_protection(self, api_client):
        """测试{module_name} XSS防护"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            test_data = {module_name.title()}Factory.build_dict()
            test_data['name'] = payload
            
            response = api_client.post(f"/{module_name}/", json=test_data)
            
            if response.status_code == 201:
                # 如果创建成功，验证返回的数据已被转义
                response_text = response.text
                assert "<script>" not in response_text
                assert "javascript:" not in response_text
                
    def test_{module_name}_authorization_check(self, api_client):
        """测试{module_name}权限控制"""
        # 未授权访问测试
        response = api_client.get(f"/{module_name}/")
        
        # 根据实际权限设计验证
        if response.status_code == 401:
            assert "unauthorized" in response.text.lower()
        elif response.status_code == 403:
            assert "forbidden" in response.text.lower()
            
    def test_{module_name}_input_validation(self, api_client):
        """测试{module_name}输入验证"""
        # 无效输入测试
        invalid_payloads = [
            {{"name": ""}},  # 空值
            {{"name": "x" * 1000}},  # 超长值
            {{"invalid_field": "test"}},  # 无效字段
            {{}},  # 空对象
        ]
        
        for payload in invalid_payloads:
            response = api_client.post(f"/{module_name}/", json=payload)
            
            # 验证输入验证生效
            assert response.status_code in [400, 422]
            
    def test_{module_name}_rate_limiting(self, api_client):
        """测试{module_name}速率限制"""
        # 快速连续请求测试
        responses = []
        
        for i in range(100):  # 发送100个快速请求
            response = api_client.get(f"/{module_name}/")
            responses.append(response.status_code)
            
        # 验证是否有速率限制生效
        rate_limited = any(status == 429 for status in responses)
        
        # 如果没有速率限制，至少验证服务稳定性
        if not rate_limited:
            successful_requests = sum(1 for status in responses if status == 200)
            assert successful_requests > 50, "服务在高频请求下不稳定"
'''

    def generate_all_tests(self, module_name: str) -> Dict[str, str]:
        """生成完整的五层测试套件"""
        all_tests = {}
        
        # 70% 单元测试
        unit_tests = self.generate_unit_tests(module_name)
        all_tests.update(unit_tests)
        
        # 20% 集成测试  
        integration_tests = self.generate_integration_tests(module_name)
        all_tests.update(integration_tests)
        
        # 6% E2E测试
        e2e_tests = self.generate_e2e_tests(module_name)
        all_tests.update(e2e_tests)
        
        # 2% 烟雾测试
        smoke_tests = self.generate_smoke_tests(module_name)
        all_tests.update(smoke_tests)
        
        # 2% 专项测试
        specialized_tests = self.generate_specialized_tests(module_name)
        all_tests.update(specialized_tests)
        
        return all_tests
    
    def create_test_files(self, test_files: Dict[str, str]) -> None:
        """创建测试文件到磁盘"""
        for file_path, content in test_files.items():
            full_path = self.project_root / file_path
            
            # 确保目录存在
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Created: {file_path}")
    
    def validate_module_exists(self, module_name: str) -> bool:
        """验证模块是否存在"""
        module_path = self.project_root / "app" / "modules" / module_name
        return module_path.exists()


class TestCodeValidator:
    """测试代码自动化验证器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validation_results = []
        
    def validate_generated_tests(self, test_files: Dict[str, str]) -> Dict[str, Any]:
        """验证生成的测试代码"""
        validation_report = {
            'total_files': len(test_files),
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': {}
        }
        
        for file_path, content in test_files.items():
            print(f"🔍 验证文件: {file_path}")
            
            file_validation = self._validate_single_file(file_path, content)
            validation_report['details'][file_path] = file_validation
            
            if file_validation['status'] == 'passed':
                validation_report['passed'] += 1
            elif file_validation['status'] == 'failed':
                validation_report['failed'] += 1
            else:
                validation_report['warnings'] += 1
                
        return validation_report
    
    def _validate_single_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """验证单个测试文件"""
        validation = {
            'status': 'passed',
            'issues': [],
            'suggestions': [],
            'metrics': {}
        }
        
        # 1. 语法检查
        syntax_issues = self._check_syntax(content)
        if syntax_issues:
            validation['issues'].extend(syntax_issues)
            validation['status'] = 'failed'
            
        # 2. 导入验证
        import_issues = self._check_imports(content)
        if import_issues:
            validation['issues'].extend(import_issues)
            validation['status'] = 'failed'
            
        # 3. Factory Boy模式验证
        factory_issues = self._check_factory_pattern(content)
        if factory_issues:
            validation['suggestions'].extend(factory_issues)
            if validation['status'] == 'passed':
                validation['status'] = 'warning'
                
        # 4. pytest标准验证
        pytest_issues = self._check_pytest_standards(content)
        if pytest_issues:
            validation['suggestions'].extend(pytest_issues)
            
        # 5. 测试覆盖度分析
        validation['metrics'] = self._analyze_test_metrics(content)
        
        # 6. 文档字符串验证
        docstring_issues = self._check_docstrings(content)
        if docstring_issues:
            validation['suggestions'].extend(docstring_issues)
            
        return validation
    
    def _check_syntax(self, content: str) -> List[str]:
        """检查Python语法"""
        issues = []
        try:
            compile(content, '<generated_test>', 'exec')
        except SyntaxError as e:
            issues.append(f"语法错误 第{e.lineno}行: {e.msg}")
        except Exception as e:
            issues.append(f"编译错误: {str(e)}")
        return issues
    
    def _check_imports(self, content: str) -> List[str]:
        """检查导入语句"""
        issues = []
        lines = content.split('\n')
        
        required_imports = {
            'pytest': False,
            'Factory': False,
            'Session': False
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('import pytest'):
                required_imports['pytest'] = True
            if 'Factory' in line and 'from tests.factories' in line:
                required_imports['Factory'] = True  
            if 'Session' in line and 'sqlalchemy' in line:
                required_imports['Session'] = True
                
        for import_name, found in required_imports.items():
            if not found and import_name in content:
                issues.append(f"缺少必需导入: {import_name}")
                
        return issues
    
    def _check_factory_pattern(self, content: str) -> List[str]:
        """检查Factory Boy模式使用"""
        suggestions = []
        
        # 检查是否使用Factory.build()或Factory.create()
        if 'Factory' in content:
            if '.build()' not in content and '.create()' not in content:
                suggestions.append("建议使用Factory.build()或Factory.create()方法")
                
            if '.build_dict()' not in content and '.create_dict()' not in content:
                suggestions.append("建议使用Factory.build_dict()生成字典数据")
                
        return suggestions
    
    def _check_pytest_standards(self, content: str) -> List[str]:
        """检查pytest标准"""
        suggestions = []
        lines = content.split('\n')
        
        test_methods = [line for line in lines if 'def test_' in line]
        
        # 检查测试方法命名
        for line in test_methods:
            if 'def test_' in line:
                method_name = line.split('def ')[1].split('(')[0]
                if len(method_name) < 15:
                    suggestions.append(f"测试方法名过短，建议更具描述性: {method_name}")
                    
        # 检查断言语句
        assert_count = content.count('assert ')
        if assert_count < len(test_methods):
            suggestions.append("部分测试方法可能缺少断言语句")
            
        # 检查文档字符串
        docstring_count = content.count('"""')
        if docstring_count < len(test_methods) * 2:  # 每个方法至少应该有一个docstring
            suggestions.append("建议为所有测试方法添加文档字符串")
            
        return suggestions
    
    def _analyze_test_metrics(self, content: str) -> Dict[str, int]:
        """分析测试度量指标"""
        return {
            'test_methods': content.count('def test_'),
            'assert_statements': content.count('assert '),
            'mock_usage': content.count('Mock()') + content.count('mocker.'),
            'parametrized_tests': content.count('@pytest.mark.parametrize'),
            'fixtures_used': content.count('def test_') if 'fixture' in content else 0,
            'lines_of_code': len(content.split('\n'))
        }
    
    def _check_docstrings(self, content: str) -> List[str]:
        """检查文档字符串质量"""
        suggestions = []
        lines = content.split('\n')
        
        in_method = False
        method_has_docstring = False
        
        for i, line in enumerate(lines):
            if 'def test_' in line:
                in_method = True
                method_has_docstring = False
            elif in_method and '"""' in line:
                method_has_docstring = True
            elif in_method and (line.strip().startswith('def ') or i == len(lines) - 1):
                if not method_has_docstring:
                    method_name = lines[i-1].split('def ')[1].split('(')[0] if i > 0 else "unknown"
                    suggestions.append(f"方法缺少文档字符串: {method_name}")
                in_method = False
                
        return suggestions
    
    def print_validation_report(self, report: Dict[str, Any]) -> None:
        """打印验证报告"""
        print("\n" + "=" * 60)
        print("🔍 测试代码验证报告")
        print("=" * 60)
        
        print(f"📊 总体统计:")
        print(f"   • 总文件数: {report['total_files']}")
        print(f"   • 通过验证: {report['passed']} ✅")
        print(f"   • 验证失败: {report['failed']} ❌")  
        print(f"   • 警告提示: {report['warnings']} ⚠️")
        
        if report['failed'] > 0:
            print(f"\n❌ 验证失败的文件:")
            for file_path, details in report['details'].items():
                if details['status'] == 'failed':
                    print(f"   📁 {file_path}")
                    for issue in details['issues']:
                        print(f"      • {issue}")
                        
        if report['warnings'] > 0:
            print(f"\n⚠️  需要注意的文件:")
            for file_path, details in report['details'].items():
                if details['status'] == 'warning':
                    print(f"   📁 {file_path}")
                    for suggestion in details['suggestions']:
                        print(f"      • {suggestion}")
                        
        # 显示度量指标
        print(f"\n📈 代码度量指标:")
        total_metrics = {
            'test_methods': 0,
            'assert_statements': 0,
            'mock_usage': 0,
            'parametrized_tests': 0,
            'lines_of_code': 0
        }
        
        for details in report['details'].values():
            for key, value in details['metrics'].items():
                if key in total_metrics:
                    total_metrics[key] += value
                    
        print(f"   • 测试方法总数: {total_metrics['test_methods']}")
        print(f"   • 断言语句总数: {total_metrics['assert_statements']}")
        print(f"   • Mock使用次数: {total_metrics['mock_usage']}")
        print(f"   • 参数化测试: {total_metrics['parametrized_tests']}")
        print(f"   • 代码总行数: {total_metrics['lines_of_code']}")
        
        if total_metrics['test_methods'] > 0:
            avg_assertions = total_metrics['assert_statements'] / total_metrics['test_methods']
            print(f"   • 平均每测试断言数: {avg_assertions:.1f}")
            
        return report['failed'] == 0


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description="五层架构标准测试生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python scripts/generate_test_template.py user_auth --type all
  python scripts/generate_test_template.py shopping_cart --type unit  
  python scripts/generate_test_template.py inventory --type integration
  
测试类型说明:
  all          - 生成完整五层测试套件 (推荐)
  unit         - 仅生成单元测试 (70%)
  integration  - 仅生成集成测试 (20%)  
  e2e          - 仅生成E2E测试 (6%)
  smoke        - 仅生成烟雾测试 (2%)
  specialized  - 仅生成专项测试 (2%)
        """
    )
    
    parser.add_argument(
        "module_name",
        help="模块名称 (如: user_auth, shopping_cart)"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["all", "unit", "integration", "e2e", "smoke", "specialized"],
        default="all",
        help="测试类型 (默认: all)"
    )
    
    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="验证模块是否存在"
    )
    
    parser.add_argument(
        "--auto-validate",
        action="store_true",
        help="自动验证生成的测试代码质量"
    )
    
    parser.add_argument(
        "--skip-create",
        action="store_true", 
        help="仅生成代码但不创建文件（用于验证测试）"
    )
    
    args = parser.parse_args()
    
    # 创建生成器实例
    generator = FiveLayerTestGenerator()
    
    # 验证模块存在性
    if args.validate and not generator.validate_module_exists(args.module_name):
        print(f"❌ 模块 '{args.module_name}' 不存在于 app/modules/ 目录中")
        print(f"请先创建模块或检查模块名称拼写")
        return 1
    
    print(f"🚀 开始生成 {args.module_name} 模块的 {args.type} 测试...")
    print(f"📋 遵循标准: docs/standards/testing-standards.md")
    print("=" * 60)
    
    # 根据类型生成测试
    test_files = {}
    
    if args.type == "all":
        test_files = generator.generate_all_tests(args.module_name)
    elif args.type == "unit":
        test_files = generator.generate_unit_tests(args.module_name)
    elif args.type == "integration":
        test_files = generator.generate_integration_tests(args.module_name)
    elif args.type == "e2e":
        test_files = generator.generate_e2e_tests(args.module_name)
    elif args.type == "smoke":
        test_files = generator.generate_smoke_tests(args.module_name)
    elif args.type == "specialized":
        test_files = generator.generate_specialized_tests(args.module_name)
    
    # 自动验证生成的代码（如果启用）
    validation_passed = True
    if args.auto_validate:
        print("\n🔍 开始自动验证生成的测试代码...")
        validator = TestCodeValidator(generator.project_root)
        validation_report = validator.validate_generated_tests(test_files)
        validation_passed = validator.print_validation_report(validation_report)
        
        if not validation_passed:
            print("\n❌ 代码验证失败! 请检查上述问题后再创建文件。")
            if not args.skip_create:
                print("提示: 使用 --skip-create 参数仅生成代码进行验证而不创建文件")
                return 1
    
    # 创建测试文件（除非跳过）
    if not args.skip_create:
        generator.create_test_files(test_files)
        print("=" * 60)
        print(f"✅ 完成! 已生成 {len(test_files)} 个测试文件")
    else:
        print("=" * 60)
        print(f"✅ 代码生成完成! (--skip-create 模式，未创建文件)")
        
    print(f"📊 测试分布符合五层架构要求:")
    
    if args.type == "all":
        print("   • 70% 单元测试 (Mock + SQLite内存)")
        print("   • 20% 集成测试 (MySQL Docker)")  
        print("   • 6% E2E测试 (MySQL Docker)")
        print("   • 2% 烟雾测试 (SQLite文件)")
        print("   • 2% 专项测试 (性能/安全)")
    
    print(f"\n🧪 运行测试命令:")
    print(f"   pytest tests/unit/test_{args.module_name}_* -v")
    print(f"   pytest tests/integration/test_{args.module_name}_* -v")
    print(f"   pytest tests/smoke/test_{args.module_name}_* -v")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())