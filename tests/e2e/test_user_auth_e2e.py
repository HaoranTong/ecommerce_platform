"""
User_Auth E2E测试套件

测试类型: 端到端测试 (E2E)
数据策略: MySQL Docker, mysql_e2e_db fixture
生成时间: 2025-09-20 21:34:33

根据testing-standards.md第135-155行E2E测试规范
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import User_AuthFactory, UserFactory

# Fixture导入
from tests.conftest import mysql_e2e_db, selenium_driver


@pytest.mark.e2e
@pytest.mark.slow
class TestUser_AuthE2E:
    """端到端测试 - 完整用户流程"""
    
    def setup_method(self):
        """E2E测试准备"""
        self.base_url = "http://localhost:3000"  # 前端应用URL
        self.test_user_data = UserFactory.build_dict()
        self.test_user_auth_data = User_AuthFactory.build_dict()
        
    def test_complete_user_auth_user_journey(self, selenium_driver, mysql_e2e_db: Session):
        """测试user_auth完整用户旅程"""
        driver = selenium_driver
        
        # 步骤1: 用户登录
        driver.get(f"{self.base_url}/login")
        
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
        
        # 步骤2: 导航到user_auth页面
        driver.get(f"{self.base_url}/user_auth")
        
        # 步骤3: 创建新user_auth
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"create-user_auth-btn"))
        )
        create_button.click()
        
        # 填写表单
        name_field = driver.find_element(By.ID, f"user_auth-name")
        name_field.send_keys(self.test_user_auth_data["name"])
        
        submit_button = driver.find_element(By.ID, "submit-btn")
        submit_button.click()
        
        # 步骤4: 验证创建成功
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "successfully created" in success_message.text.lower()
        
        # 步骤5: 验证数据库中存在
        from app.modules.user_auth.service import User_AuthService
        service = User_AuthService(mysql_e2e_db)
        
        created_items = service.get_all()
        assert len(created_items) > 0
        assert any(item.name == self.test_user_auth_data["name"] for item in created_items)
        
    def test_user_auth_error_handling_e2e(self, selenium_driver, mysql_e2e_db: Session):
        """测试user_auth错误处理端到端流程"""
        driver = selenium_driver
        
        # 导航到user_auth页面
        driver.get(f"{self.base_url}/user_auth")
        
        # 尝试提交无效表单
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"create-user_auth-btn"))
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
