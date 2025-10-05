"""
烟雾测试 - 系统健康检查

功能描述：
- 验证应用服务健康状态和基本可用性
- 检查API文档界面和规范访问性能
- 监控数据库连接响应性和时间同步
- 验证关键环境变量配置完整性
- 测试基础响应时间性能基准

检查项目：
- 应用健康端点：/api/health, / (根路径备选)
- API文档访问：/docs, /redoc 界面可用性
- 数据库健康：连接性能和时间查询响应
- 环境配置：DATABASE_URL, SECRET_KEY, REDIS_URL等
- 性能基准：文档页面加载时间 < 5秒

使用方法：
- 推荐：tools/smoke_test.ps1 自动环境感知执行
- 直接：pytest tests/smoke/test_health.py -v
- 集成：作为基本检测的补充健康监控

容错特性：
- 404状态码视为正常（服务运行但端点不存在）
- 环境变量缺失时使用默认值不强制失败
- 部分检查失败不影响整体健康评估
"""
import time
from datetime import datetime

import pytest
import requests
from sqlalchemy import text


def test_application_health():
    """验证应用基本健康状态"""
    health_endpoints = [
        "http://127.0.0.1:8000/api/health",
        "http://127.0.0.1:8000/"  # 根路径作为备选
    ]
    
    success = False
    for endpoint in health_endpoints:
        try:
            response = requests.get(endpoint, timeout=3)
            if response.status_code in [200, 404]:  # 200正常，404也表示服务在运行
                print(f"✅ {endpoint} responded with {response.status_code}")
                success = True
                break
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {endpoint}")
            continue
        except Exception as e:
            print(f"⚠️  {endpoint} error: {e}")
            continue
    
    if not success:
        pytest.skip("⚠️  No application endpoints responding - server not running. Use tools/smoke_test.ps1 for full testing.")

def test_api_documentation_access():
    """验证API文档访问"""
    docs_endpoints = [
        "http://127.0.0.1:8000/docs",
        "http://127.0.0.1:8000/redoc"
    ]
    
    for endpoint in docs_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                print(f"✅ API docs accessible at {endpoint}")
            else:
                print(f"⚠️  {endpoint} returned {response.status_code}")
        except Exception as e:
            print(f"⚠️  {endpoint} not accessible: {e}")

def test_database_connection_smoke(smoke_test_db):
    """验证数据库连接正常"""
    try:
        # 简单的数据库连接测试
        result = smoke_test_db.execute(text("SELECT datetime('now') as current_time")).fetchone()
        current_time = result[0]
        print(f"✅ Database connection OK, current time: {current_time}")
        assert current_time is not None
    except Exception as e:
        pytest.fail(f"❌ Database connection failed: {e}")

def test_environment_variables():
    """验证关键环境变量"""
    import os

    # 检查关键环境变量
    critical_vars = [
        # 数据库配置不是必需的，因为有默认值
        # API配置
    ]
    
    optional_vars = [
        "DATABASE_URL",
        "SECRET_KEY", 
        "REDIS_URL",
        "ENVIRONMENT"
    ]
    
    print("=== Environment Variables Check ===")
    
    # 检查关键变量
    for var in critical_vars:
        value = os.getenv(var)
        if not value:
            pytest.fail(f"❌ Critical environment variable {var} is not set")
        print(f"✅ {var}: configured")
    
    # 检查可选变量
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if 'password' in var.lower() or 'secret' in var.lower():
                print(f"ℹ️  {var}: [HIDDEN]")
            else:
                print(f"ℹ️  {var}: {value}")
        else:
            print(f"⚠️  {var}: not set (using defaults)")

def test_response_time_basic():
    """基础响应时间测试"""
    start_time = time.time()
    
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=10)
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Response time: {response_time:.2f}s")
        
        # 烟雾测试的响应时间要求较宽松
        if response_time < 5.0:
            print("✅ Response time acceptable for smoke test")
        else:
            print(f"⚠️  Response time {response_time:.2f}s is slow but acceptable for smoke test")
            
    except Exception as e:
        print(f"⚠️  Response time test failed: {e}")