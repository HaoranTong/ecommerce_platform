"""
Shopping_Cart E2E测试套件

测试类型: 端到端测试 (E2E)
数据策略: MySQL Docker, mysql_e2e_db fixture
生成时间: 2025-09-20 09:43:58

根据testing-standards.md第135-155行E2E测试规范
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import Shopping_CartFactory, UserFactory

# Fixture导入
from tests.conftest import mysql_e2e_db, selenium_driver


@pytest.mark.e2e
@pytest.mark.slow
class TestShopping_CartE2E:
    """端到端测试 - 完整用户流程"""
    
    def setup_method(self):
        """E2E测试准备"""
        self.base_url = "http://localhost:3000"  # 前端应用URL
        self.test_user_data = UserFactory.build_dict()
        self.test_shopping_cart_data = Shopping_CartFactory.build_dict()
        
    def test_complete_shopping_cart_user_journey(self, selenium_driver, mysql_e2e_db: Session):
        """测试shopping_cart完整用户旅程"""
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
        
        # 步骤2: 导航到shopping_cart页面
        driver.get(f"{self.base_url}/shopping_cart")
        
        # 步骤3: 创建新shopping_cart
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"create-shopping_cart-btn"))
        )
        create_button.click()
        
        # 填写表单
        name_field = driver.find_element(By.ID, f"shopping_cart-name")
        name_field.send_keys(self.test_shopping_cart_data["name"])
        
        submit_button = driver.find_element(By.ID, "submit-btn")
        submit_button.click()
        
        # 步骤4: 验证创建成功
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "successfully created" in success_message.text.lower()
        
        # 步骤5: 验证数据库中存在
        from app.modules.shopping_cart.service import Shopping_CartService
        service = Shopping_CartService(mysql_e2e_db)
        
        created_items = service.get_all()
        assert len(created_items) > 0
        assert any(item.name == self.test_shopping_cart_data["name"] for item in created_items)
        
    def test_shopping_cart_error_handling_e2e(self, selenium_driver, mysql_e2e_db: Session):
        """测试shopping_cart错误处理端到端流程"""
        driver = selenium_driver
        
        # 导航到shopping_cart页面
        driver.get(f"{self.base_url}/shopping_cart")
        
        # 尝试提交无效表单
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"create-shopping_cart-btn"))
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
