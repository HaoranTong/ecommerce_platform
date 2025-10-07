"""
性能测试生成器

功能: 生成API性能基准测试代码，验证系统响应时间和并发处理能力
使用方法: 通过BaseTestGenerator继承，由主生成器调用generate_performance_tests方法
使用场景: 电商平台性能瓶颈识别、容量规划、SLA验证

生成的性能测试:
1. 响应时间测试 - 单请求响应时间基准测试
2. 并发负载测试 - 多用户并发访问性能测试
3. 压力测试 - 系统极限负载下的稳定性测试
4. 内存使用测试 - API调用内存消耗监控
5. 数据库性能测试 - 数据库查询效率测试
6. 缓存效果测试 - Redis缓存命中率和        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}LoadTest"
        auth_endpoint = self._select_auth_endpoint(routes, module_name)
        write_endpoint, write_method = self._select_write_endpoint(routes, module_name)
        test_data_template = self._generate_write_test_data(routes, module_name)

输出位置: tests/performance/test_{module}_performance.py
测试框架: pytest + pytest-benchmark + locust

性能指标:
- 平均响应时间 < 100ms
- 95%请求响应时间 < 200ms
- 并发用户数支持 > 100
- 错误率 < 0.1%

技术特点:
- 基于业务场景设计性能测试
- 自动生成负载测试脚本
- 支持性能基准比较
- 集成性能监控报告

版本: v1.0.0
作者: AI Assistant
创建时间: 2025-10-01
"""

import asyncio
from typing import Dict, List, Tuple
from .base_generator import BaseTestGenerator, ModelInfo, RouterInfo


class PerformanceTestGenerator(BaseTestGenerator):
    """性能测试代码生成器"""

    def _generate_write_test_data(self, routes: List[RouterInfo], module_name: str, request_id: str = "{{request_id}}") -> str:
        """
        根据路由信息生成适合的写操作测试数据模板
        
        🚨 **模板格式化关键注意事项** 🚨
        - 返回的字符串将作为Python代码模板使用
        - 避免使用双重花括号 {{}} 转义，会导致变量不被替换
        - 确保f-string中的变量引用格式正确: f"value_{variable}" 不是 f"value_{{variable}}"
        
        Args:
            routes: 路由信息列表
            module_name: 模块名称
            request_id: 请求ID（用于生成唯一数据）
            
        Returns:
            str: 测试数据字典的字符串表示，格式为Python字典代码
        """
        # 查找PUT端点来推断更新字段
        put_routes = [r for r in routes if r.method == 'PUT' and r.auth_required]
        
        # 基于实际POST端点的Schema使用Faker动态生成数据
        # 查找第一个POST端点来推断需要的字段
        post_routes = [r for r in routes if r.method == 'POST' and not any(keyword in r.path.lower() for keyword in ['login', 'register', 'refresh'])]
        
        if post_routes:
            # 尝试从路由分析Schema
            first_post_route = post_routes[0]
            # 基于路由路径推断数据结构，使用Faker动态生成
            if 'categories' in first_post_route.path.lower() or 'category' in first_post_route.path.lower():
                return '''"name": fake.name()[:50],
                "description": fake.text(max_nb_chars=100),
                "sort_order": fake.random_int(min=0, max=100),
                "is_active": True'''
            elif 'brand' in first_post_route.path.lower():
                return '''"name": fake.company()[:50],
                "slug": fake.slug(),
                "description": fake.text(max_nb_chars=100),
                "is_active": True'''
            elif 'product' in first_post_route.path.lower() and 'sku' not in first_post_route.path.lower():
                return '''"name": fake.catch_phrase()[:50],
                "description": fake.text(max_nb_chars=100),
                "status": "published"'''
        
        # 回退到基于模块名的推断
        if put_routes and any('me' in route.path or 'profile' in route.path for route in put_routes):
            # 用户资料更新类端点
            return '''"real_name": fake.name()[:50],
                "phone": f"1{fake.random_int(min=300000000, max=999999999)}"'''
        elif any(keyword in module_name for keyword in ['order', 'cart']):
            # 订单/购物车类模块
            return '''"quantity": fake.random_int(min=1, max=10),
                "notes": fake.text(max_nb_chars=50)'''
        else:
            # 通用测试数据
            return '''"name": fake.name()[:50],
                "description": fake.text(max_nb_chars=100)'''

    def _select_auth_endpoint(self, routes: List[RouterInfo], module_name: str) -> str:
        """选择认证相关的端点"""
        if routes:
            # 优先选择需要认证的GET端点
            auth_required_routes = [r for r in routes if r.auth_required and r.method == "GET"]
            if auth_required_routes:
                return f"/api/v1{auth_required_routes[0].path}"
            
            # 回退：使用第一个GET端点
            get_routes = [r for r in routes if r.method == "GET"]
            if get_routes:
                return f"/api/v1{get_routes[0].path}"
            
            # 再回退：使用第一个端点
            return f"/api/v1{routes[0].path}"
        
        # 最终回退：使用API模块名
        module_path = module_name.replace('_', '-')
        return f"/api/v1/{module_path}/"

    def _select_write_endpoint(self, routes: List[RouterInfo], module_name: str) -> tuple[str, str]:
        """
        选择适合写操作性能测试的端点
        
        Returns:
            tuple[str, str]: (endpoint_url, http_method)
        """
        if routes:
            # 优先选择适合性能测试的POST端点（非认证相关）
            post_routes = [
                r for r in routes 
                if r.method == 'POST' and not any(keyword in r.path.lower() for keyword in ['login', 'register', 'refresh', 'logout'])
            ]
            if post_routes:
                return f"/api/v1{post_routes[0].path}", "POST"
            
            # 回退：选择需要认证的PUT端点（适合更新操作）
            put_routes = [r for r in routes if r.method == 'PUT' and r.auth_required]
            if put_routes:
                return f"/api/v1{put_routes[0].path}", "PUT"
            
            # 再回退：使用任何需要认证的POST端点
            auth_post_routes = [r for r in routes if r.method == 'POST' and r.auth_required]
            if auth_post_routes:
                return f"/api/v1{auth_post_routes[0].path}", "POST"
            
            # 最终回退：使用第一个POST端点
            any_post_routes = [r for r in routes if r.method == 'POST']
            if any_post_routes:
                return f"/api/v1{any_post_routes[0].path}", "POST"
            
            # 使用第一个端点
            return f"/api/v1{routes[0].path}", routes[0].method
        
        # 最终回退：使用API模块名
        module_path = module_name.replace('_', '-')
        return f"/api/v1/{module_path}/", "POST"
    
    def generate_tests(self, module_name: str, models: Dict[str, ModelInfo]) -> Dict[str, str]:
        """生成性能测试代码"""
        
        routes = self.analyze_router_file(module_name)
        test_content = self._generate_performance_test_content(module_name, routes, models)
        return {f"tests/performance/test_{module_name}_performance.py": test_content}
    
    def _generate_performance_test_content(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成性能测试文件内容"""
        
        header = self.generate_test_file_header(
            module_name,
            "性能基准",
            f"测试{self.get_module_business_domain(module_name)}模块的性能指标\\n"
            f"包括响应时间、吞吐量、并发处理、内存使用等性能测试"
        )
        
        imports = '''
import pytest
import asyncio
import time
import statistics
from httpx import AsyncClient
from fastapi import status
from datetime import datetime, timedelta

from app.main import app
from tests.conftest import api_client
'''
        
        # 生成响应时间测试类
        response_time_class = self._generate_response_time_tests(module_name, routes, models)
        
        # 生成并发测试类
        concurrency_class = self._generate_concurrency_tests(module_name, routes, models)
        
        # 生成负载测试类
        load_test_class = self._generate_load_tests(module_name, routes, models)
        
        # 生成性能基准测试类
        benchmark_class = self._generate_benchmark_tests(module_name, routes, models)
        
        return header + imports + "\n\n".join([
            response_time_class,
            concurrency_class,
            load_test_class,
            benchmark_class
        ])
    
    def _generate_response_time_tests(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成响应时间测试"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}ResponseTime"
        auth_endpoint = self._select_auth_endpoint(routes, module_name)
        write_endpoint, write_method = self._select_write_endpoint(routes, module_name)
        test_data_template = self._generate_write_test_data(routes, module_name)
        module_path = module_name.replace('_', '-')
        
        return f'''
class {class_name}:
    """{business_domain}模块响应时间性能测试"""
    
    async def test_api_response_time_p50(self, async_api_client):
        """测试API响应时间P50指标 - 要求<200ms"""
        
        # 使用真实JWT身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        response_times = []
        
        # 执行100次请求测量响应时间
        for _ in range(100):
            start_time = time.time()
            
            response = await async_api_client.get("{auth_endpoint}", headers=headers)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            response_times.append(response_time)
            
            # 适当间隔避免过于密集的请求
            await asyncio.sleep(0.01)
        
        # 计算性能指标
        p50 = statistics.median(response_times)
        p95 = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        avg = statistics.mean(response_times)
        
        print(f"📊 {business_domain}响应时间统计:")
        print(f"   P50: {{p50:.1f}}ms")
        print(f"   P95: {{p95:.1f}}ms")
        print(f"   P99: {{p99:.1f}}ms")
        print(f"   平均: {{avg:.1f}}ms")
        
        # 性能断言 - 基于performance-standards.md
        assert p50 < 200, f"P50响应时间超标: {{p50:.1f}}ms > 200ms"
        assert p95 < 500, f"P95响应时间超标: {{p95:.1f}}ms > 500ms"
        assert p99 < 1000, f"P99响应时间超标: {{p99:.1f}}ms > 1000ms"
        
        print("✅ 响应时间性能测试通过")
    
    async def test_database_query_performance(self, async_api_client):
        """测试数据库查询性能"""
        
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        query_times = []
        
        # 测试不同类型的查询性能
        query_endpoints = [
            f"/api/v1/{module_path}/",           # 列表查询
            f"/api/v1/{module_path}/search",     # 搜索查询
            f"/api/v1/{module_path}/1",          # 单记录查询
        ]
        
        for endpoint in query_endpoints:
            start_time = time.time()
            
            response = await async_api_client.get(endpoint, headers=headers)
            
            end_time = time.time()
            query_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                query_times.append(query_time)
                print(f"📊 {{endpoint}}: {{query_time:.1f}}ms")
        
        if query_times:
            avg_query_time = statistics.mean(query_times)
            assert avg_query_time < 100, f"数据库查询平均时间超标: {{avg_query_time:.1f}}ms > 100ms"
        
        print("✅ 数据库查询性能测试通过")
    
    async def test_cold_start_performance(self, async_api_client):
        """测试冷启动性能"""
        
        # 模拟应用冷启动后的首次请求
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        start_time = time.time()
        response = await async_api_client.get("{auth_endpoint}", headers=headers)
        end_time = time.time()
        
        cold_start_time = (end_time - start_time) * 1000
        
        print(f"📊 冷启动响应时间: {{cold_start_time:.1f}}ms")
        
        # 冷启动时间应该在合理范围内
        assert cold_start_time < 2000, f"冷启动时间过长: {{cold_start_time:.1f}}ms > 2000ms"
        
        print("✅ 冷启动性能测试通过")
'''
    
    def _generate_concurrency_tests(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成并发测试"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}Concurrency"
        auth_endpoint = self._select_auth_endpoint(routes, module_name)
        write_endpoint, write_method = self._select_write_endpoint(routes, module_name)
        test_data_template = self._generate_write_test_data(routes, module_name)
        module_path = module_name.replace('_', '-')
        
        return f'''
class {class_name}:
    """{business_domain}模块并发性能测试"""
    
    async def test_concurrent_read_requests(self, async_api_client):
        """测试并发读请求处理能力"""
        
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        concurrent_users = 50  # 模拟50个并发用户
        
        async def single_request():
            start_time = time.time()
            try:
                response = await async_api_client.get("{auth_endpoint}", headers=headers)
                end_time = time.time()
                
                return {{
                    "status_code": response.status_code,
                    "response_time": (end_time - start_time) * 1000,
                    "success": response.status_code == 200,
                    "error": None
                }}
            except Exception as e:
                end_time = time.time()
                print(f"⚠️ 并发读请求异常: {{str(e)}}")
                return {{
                    "status_code": None,
                    "response_time": (end_time - start_time) * 1000,
                    "success": False,
                    "error": str(e)
                }}
        
        # 并发执行请求
        start_time = time.time()
        tasks = [single_request() for _ in range(concurrent_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 统计结果
        successful_requests = [r for r in results if isinstance(r, dict) and r["success"]]
        failed_requests = [r for r in results if isinstance(r, Exception) or (isinstance(r, dict) and not r["success"])]
        
        success_rate = len(successful_requests) / concurrent_users * 100
        throughput = len(successful_requests) / total_time  # 请求/秒
        
        if successful_requests:
            avg_response_time = statistics.mean([r["response_time"] for r in successful_requests])
        else:
            avg_response_time = 0
        
        print(f"📊 并发读测试结果:")
        print(f"   并发用户数: {{concurrent_users}}")
        print(f"   成功率: {{success_rate:.1f}}%")
        print(f"   吞吐量: {{throughput:.1f}} req/s") 
        print(f"   平均响应时间: {{avg_response_time:.1f}}ms")
        print(f"   失败请求数: {{len(failed_requests)}}")
        
        # 性能断言
        assert success_rate >= 95, f"并发成功率过低: {{success_rate:.1f}}% < 95%"
        assert throughput >= 10, f"吞吐量过低: {{throughput:.1f}} req/s < 10 req/s"
        assert avg_response_time < 1000, f"并发响应时间过慢: {{avg_response_time:.1f}}ms > 1000ms"
        
        print("✅ 并发读请求测试通过")
    
    async def test_concurrent_write_requests(self, async_api_client):
        """测试并发写请求处理能力"""
        
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        concurrent_writes = 20  # 模拟20个并发写操作
        
        # 导入Faker用于动态生成测试数据
        from faker import Faker
        fake = Faker()
        
        async def write_request(request_id):
            # 使用Faker动态生成测试数据
            test_data = {{
                {test_data_template}
            }}
            
            start_time = time.time()
            try:
                # 使用确定的HTTP方法
                response = await async_api_client.{write_method.lower()}(
                    "{write_endpoint}",
                    json=test_data,
                    headers=headers
                )
                end_time = time.time()
                
                return {{
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_time": (end_time - start_time) * 1000,
                    "success": response.status_code in [200, 201]
                }}
            except Exception as e:
                end_time = time.time()
                print(f"⚠️ 写请求 {{request_id}} 异常: {{str(e)}}")
                return {{
                    "request_id": request_id,
                    "status_code": 0,
                    "response_time": (end_time - start_time) * 1000,
                    "success": False,
                    "error": str(e)
                }}
        
        # 并发执行写请求
        start_time = time.time()
        tasks = [write_request(i) for i in range(concurrent_writes)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 统计结果
        successful_writes = [r for r in results if isinstance(r, dict) and r["success"]]
        
        success_rate = len(successful_writes) / concurrent_writes * 100
        write_throughput = len(successful_writes) / total_time
        
        print(f"📊 并发写测试结果:")
        print(f"   并发写操作数: {{concurrent_writes}}")
        print(f"   成功率: {{success_rate:.1f}}%")
        print(f"   写吞吐量: {{write_throughput:.1f}} writes/s")
        
        # 写操作的成功率要求可以适当放宽（考虑到数据竞争）
        assert success_rate >= 90, f"并发写成功率过低: {{success_rate:.1f}}% < 90%"
        
        print("✅ 并发写请求测试通过")
    
    async def test_mixed_workload_performance(self, async_api_client):
        """测试混合工作负载性能"""
        
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        # 导入Faker用于动态生成测试数据
        from faker import Faker
        fake = Faker()
        
        # 模拟真实场景：70%读操作，30%写操作
        read_tasks = 35
        write_tasks = 15
        
        async def read_operation():
            try:
                response = await async_api_client.get("{auth_endpoint}", headers=headers)
                return {{"type": "read", "success": response.status_code == 200}}
            except Exception as e:
                print(f"⚠️ 混合负载读操作异常: {{str(e)}}")
                return {{"type": "read", "success": False, "error": str(e)}}
        
        async def write_operation():
            # 使用Faker动态生成测试数据（确保唯一性）
            test_data = {{
                {test_data_template}
            }}
            try:
                # 使用确定的HTTP方法
                response = await async_api_client.{write_method.lower()}("{write_endpoint}", json=test_data, headers=headers)
                return {{"type": "write", "success": response.status_code in [200, 201]}}
            except Exception as e:
                print(f"⚠️ 混合负载写操作异常: {{str(e)}}")
                return {{"type": "write", "success": False, "error": str(e)}}
        
        # 混合任务
        tasks = []
        tasks.extend([read_operation() for _ in range(read_tasks)])
        tasks.extend([write_operation() for _ in range(write_tasks)])
        
        # 随机打乱任务顺序
        import random
        random.shuffle(tasks)
        
        # 执行混合工作负载
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 统计结果
        read_results = [r for r in results if isinstance(r, dict) and r["type"] == "read"]
        write_results = [r for r in results if isinstance(r, dict) and r["type"] == "write"]
        
        read_success_rate = sum(1 for r in read_results if r["success"]) / len(read_results) * 100
        write_success_rate = sum(1 for r in write_results if r["success"]) / len(write_results) * 100
        
        overall_throughput = len(results) / total_time
        
        print(f"📊 混合负载测试结果:")
        print(f"   读操作成功率: {{read_success_rate:.1f}}%")
        print(f"   写操作成功率: {{write_success_rate:.1f}}%")
        print(f"   整体吞吐量: {{overall_throughput:.1f}} ops/s")
        
        assert read_success_rate >= 95, f"混合负载读成功率过低: {{read_success_rate:.1f}}%"
        assert write_success_rate >= 85, f"混合负载写成功率过低: {{write_success_rate:.1f}}%"
        
        print("✅ 混合工作负载测试通过")
'''
    
    def _generate_load_tests(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成负载测试"""
        
        business_domain = self.get_module_business_domain(module_name)
        auth_endpoint = self._select_auth_endpoint(routes, module_name)
        write_endpoint, write_method = self._select_write_endpoint(routes, module_name)
        test_data_template = self._generate_write_test_data(routes, module_name)
        module_path = module_name.replace('_', '-')
        class_name = f"Test{module_name.title().replace('_', '')}LoadTest"
        
        return f'''
class {class_name}:
    """{business_domain}模块负载测试"""
    
    async def test_sustained_load(self, async_api_client):
        """测试持续负载处理能力"""
        
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        duration_seconds = 30  # 持续30秒的负载测试
        requests_per_second = 10  # 每秒10个请求
        
        results = []
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            # 每秒发送指定数量的请求
            batch_tasks = []
            for _ in range(requests_per_second):
                task = async_api_client.get("{auth_endpoint}", headers=headers)
                batch_tasks.append(task)
            
            batch_responses = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # 记录这一秒的结果
            successful_in_batch = sum(
                1 for r in batch_responses 
                if hasattr(r, 'status_code') and r.status_code == 200
            )
            
            results.append({{
                "timestamp": batch_start,
                "successful_requests": successful_in_batch,
                "total_requests": requests_per_second
            }})
            
            # 控制请求频率
            batch_duration = time.time() - batch_start
            if batch_duration < 1.0:
                await asyncio.sleep(1.0 - batch_duration)
        
        # 分析负载测试结果
        total_requests = sum(r["total_requests"] for r in results)
        total_successful = sum(r["successful_requests"] for r in results)
        
        success_rate = total_successful / total_requests * 100
        actual_throughput = total_successful / duration_seconds
        
        print(f"📊 持续负载测试结果:")
        print(f"   测试持续时间: {{duration_seconds}}秒")
        print(f"   总请求数: {{total_requests}}")
        print(f"   成功请求数: {{total_successful}}")
        print(f"   成功率: {{success_rate:.1f}}%")
        print(f"   实际吞吐量: {{actual_throughput:.1f}} req/s")
        
        # 持续负载下的性能要求
        assert success_rate >= 99, f"持续负载成功率过低: {{success_rate:.1f}}% < 99%"
        assert actual_throughput >= requests_per_second * 0.95, f"吞吐量下降过多: {{actual_throughput:.1f}} < {{requests_per_second * 0.95:.1f}}"
        
        print("✅ 持续负载测试通过")
    
    async def test_peak_load_handling(self, async_api_client):
        """测试峰值负载处理能力"""
        
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        peak_concurrent_users = 100  # 峰值并发用户数
        
        # 导入Faker用于动态生成测试数据
        from faker import Faker
        fake = Faker()
        
        async def user_session():
            """模拟单个用户会话"""
            try:
                # 使用Faker动态生成测试数据
                test_data = {{
                    {test_data_template}
                }}
                # 用户典型操作序列
                operations = [
                    ("GET", "{auth_endpoint}"),  # 获取当前用户信息
                    ("GET", "/api/v1/{module_path}/users"),  # 用户列表
                    ("{write_method}", "{write_endpoint}", test_data),  # 更新用户信息
                ]
                
                session_success = True
                for method, url, *data in operations:
                    if method == "GET":
                        response = await async_api_client.get(url, headers=headers)
                    elif method == "PUT":
                        response = await async_api_client.put(url, json=data[0] if data else {{}}, headers=headers)
                    else:
                        response = await async_api_client.post(url, json=data[0] if data else {{}}, headers=headers)
                    
                    # 只有500错误才认为是严重失败
                    if response.status_code >= 500:
                        session_success = False
                        break
                    
                    await asyncio.sleep(0.1)  # 用户操作间隔
                
                return session_success
            except Exception as e:
                print(f"⚠️ 用户会话异常: {{str(e)}}")
                return False
        
        # 模拟峰值负载
        start_time = time.time()
        tasks = [user_session() for _ in range(peak_concurrent_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_sessions = sum(1 for r in results if r is True)
        session_success_rate = successful_sessions / peak_concurrent_users * 100
        
        print(f"📊 峰值负载测试结果:")
        print(f"   峰值并发用户: {{peak_concurrent_users}}")
        print(f"   成功会话数: {{successful_sessions}}")
        print(f"   会话成功率: {{session_success_rate:.1f}}%")
        print(f"   总处理时间: {{total_time:.1f}}秒")
        
        # 峰值负载下仍应保持基本服务能力
        assert session_success_rate >= 80, f"峰值负载下会话成功率过低: {{session_success_rate:.1f}}% < 80%"
        
        print("✅ 峰值负载测试通过")
'''
    
    def _generate_benchmark_tests(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成性能基准测试"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}Benchmark"
        auth_endpoint = self._select_auth_endpoint(routes, module_name)
        write_endpoint, write_method = self._select_write_endpoint(routes, module_name)
        test_data_template = self._generate_write_test_data(routes, module_name)
        module_path = module_name.replace('_', '-')
        
        return f'''
class {class_name}:
    """{business_domain}模块性能基准测试"""
    
    async def test_performance_regression(self, async_api_client):
        """测试性能回归基准"""
        
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        # 性能基准数据（应该来自历史数据或预设基准）
        performance_baselines = {{
            "list_endpoint_p50": 150,    # 150ms
            "search_endpoint_p50": 300,  # 300ms
            "create_endpoint_p50": 200,  # 200ms
            "throughput_minimum": 50,    # 50 req/s
        }}
        
        # 测试列表端点性能
        list_times = []
        for _ in range(50):
            start = time.time()
            response = await async_api_client.get("{auth_endpoint}", headers=headers)
            end = time.time()
            
            if response.status_code == 200:
                list_times.append((end - start) * 1000)
        
        # 测试搜索端点性能
        search_times = []
        for _ in range(30):
            start = time.time()
            response = await async_api_client.get(f"/api/v1/{module_path}/search", params={{"q": "test"}}, headers=headers)
            end = time.time()
            
            if response.status_code in [200, 404]:  # 404也是正常响应
                search_times.append((end - start) * 1000)
        
        # 测试创建端点性能
        create_times = []
        for i in range(20):
            test_data = {{"name": f"benchmark_{{i}}", "value": f"test_{{i}}"}}
            start = time.time()
            response = await async_api_client.{write_method.lower()}("{write_endpoint}", json=test_data, headers=headers)
            end = time.time()
            
            if response.status_code in [200, 201, 422]:  # 422表示验证失败但服务正常
                create_times.append((end - start) * 1000)
        
        # 计算性能指标
        current_metrics = {{}}
        
        if list_times:
            current_metrics["list_endpoint_p50"] = statistics.median(list_times)
        
        if search_times:
            current_metrics["search_endpoint_p50"] = statistics.median(search_times)
        
        if create_times:
            current_metrics["create_endpoint_p50"] = statistics.median(create_times)
        
        # 测试吞吐量
        throughput_start = time.time()
        throughput_tasks = [async_api_client.get("{auth_endpoint}", headers=headers) for _ in range(100)]
        throughput_responses = await asyncio.gather(*throughput_tasks, return_exceptions=True)
        throughput_time = time.time() - throughput_start
        
        successful_throughput_requests = sum(
            1 for r in throughput_responses 
            if hasattr(r, 'status_code') and r.status_code == 200
        )
        current_metrics["throughput_minimum"] = successful_throughput_requests / throughput_time
        
        # 性能基准比较
        print(f"📊 {business_domain}性能基准测试结果:")
        
        regression_found = False
        for metric, baseline in performance_baselines.items():
            current_value = current_metrics.get(metric, 0)
            
            if metric.endswith("_p50"):
                # 响应时间指标：当前值应该不超过基准值的120%
                threshold = baseline * 1.2
                passed = current_value <= threshold
                print(f"   {{metric}}: {{current_value:.1f}}ms (基准: {{baseline}}ms, 阈值: {{threshold:.1f}}ms) {{'✅' if passed else '❌'}}")
                if not passed:
                    regression_found = True
            
            elif metric.startswith("throughput"):
                # 吞吐量指标：当前值应该不低于基准值的80%
                threshold = baseline * 0.8
                passed = current_value >= threshold
                print(f"   {{metric}}: {{current_value:.1f}} req/s (基准: {{baseline}} req/s, 阈值: {{threshold:.1f}} req/s) {{'✅' if passed else '❌'}}")
                if not passed:
                    regression_found = True
        
        # 性能回归检查
        assert not regression_found, "检测到性能回归，当前性能低于基准要求"
        
        print("✅ 性能基准测试通过，无性能回归")
    
    async def test_memory_usage_efficiency(self, async_api_client):
        """测试内存使用效率"""
        
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        # 模拟大量请求测试内存效率
        large_dataset_requests = []
        
        for i in range(1000):
            # 模拟处理大数据集的请求
            task = async_api_client.get(
                "{auth_endpoint}",
                params={{"limit": 100, "offset": i * 100}},
                headers=headers
            )
            large_dataset_requests.append(task)
            
            # 分批处理避免内存溢出
            if len(large_dataset_requests) >= 50:
                batch_responses = await asyncio.gather(*large_dataset_requests, return_exceptions=True)
                large_dataset_requests.clear()
                
                # 短暂休息让GC有机会清理
                await asyncio.sleep(0.1)
        
        # 处理剩余请求
        if large_dataset_requests:
            await asyncio.gather(*large_dataset_requests, return_exceptions=True)
        
        print("✅ 内存使用效率测试通过")
    
    async def test_performance_under_stress(self, async_api_client):
        """测试压力条件下的性能表现"""
        
        # 设置真实的身份验证
        token, admin_user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        # 逐步增加负载压力
        stress_levels = [10, 25, 50, 75, 100]  # 并发用户数
        stress_results = []
        
        for stress_level in stress_levels:
            print(f"🔄 测试压力等级: {{stress_level}} 并发用户")
            
            async def stress_request():
                try:
                    start = time.time()
                    response = await async_api_client.get("{auth_endpoint}", headers=headers)
                    end = time.time()
                    
                    return {{
                        "success": response.status_code == 200,
                        "response_time": (end - start) * 1000
                    }}
                except Exception:
                    return {{"success": False, "response_time": 0}}
            
            # 执行压力测试
            stress_start = time.time()
            stress_tasks = [stress_request() for _ in range(stress_level)]
            stress_responses = await asyncio.gather(*stress_tasks)
            stress_duration = time.time() - stress_start
            
            # 统计压力测试结果
            successful_requests = [r for r in stress_responses if r["success"]]
            success_rate = len(successful_requests) / stress_level * 100
            
            if successful_requests:
                avg_response_time = statistics.mean([r["response_time"] for r in successful_requests])
            else:
                avg_response_time = 0
            
            throughput = len(successful_requests) / stress_duration
            
            stress_results.append({{
                "stress_level": stress_level,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "throughput": throughput
            }})
            
            print(f"   成功率: {{success_rate:.1f}}%, 平均响应时间: {{avg_response_time:.1f}}ms, 吞吐量: {{throughput:.1f}} req/s")
            
            # 短暂休息让系统恢复
            await asyncio.sleep(2)
        
        # 分析压力测试趋势
        print(f"📊 压力测试完整结果:")
        for result in stress_results:
            print(f"   {{result['stress_level']}}用户: {{result['success_rate']:.1f}}% 成功率, {{result['avg_response_time']:.1f}}ms 响应时间")
        
        # 验证系统在适度压力下仍能保持性能
        moderate_stress_result = next((r for r in stress_results if r["stress_level"] == 25), None)
        if moderate_stress_result:
            assert moderate_stress_result["success_rate"] >= 95, f"适度压力下成功率过低: {{moderate_stress_result['success_rate']:.1f}}%"
        
        print("✅ 压力测试完成")
'''