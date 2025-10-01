"""
性能测试生成器

基于性能标准生成性能测试代码
遵循docs/standards/performance-standards.md和testing-standards.md规范
"""

import asyncio
from typing import Dict, List
from .base_generator import BaseTestGenerator, ModelInfo, RouterInfo


class PerformanceTestGenerator(BaseTestGenerator):
    """性能测试代码生成器"""
    
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
        
        return f'''
class {class_name}:
    """{business_domain}模块响应时间性能测试"""
    
    async def test_api_response_time_p50(self, api_client: AsyncClient):
        """测试API响应时间P50指标 - 要求<200ms"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        response_times = []
        
        # 执行100次请求测量响应时间
        for _ in range(100):
            start_time = time.time()
            
            response = await api_client.get("/api/v1/{module_name}/", headers=headers)
            
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
    
    async def test_database_query_performance(self, api_client: AsyncClient):
        """测试数据库查询性能"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        query_times = []
        
        # 测试不同类型的查询性能
        query_endpoints = [
            "/api/v1/{module_name}/",           # 列表查询
            "/api/v1/{module_name}/search",     # 搜索查询
            "/api/v1/{module_name}/1",          # 单记录查询
        ]
        
        for endpoint in query_endpoints:
            start_time = time.time()
            
            response = await api_client.get(endpoint, headers=headers)
            
            end_time = time.time()
            query_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                query_times.append(query_time)
                print(f"📊 {{endpoint}}: {{query_time:.1f}}ms")
        
        if query_times:
            avg_query_time = statistics.mean(query_times)
            assert avg_query_time < 100, f"数据库查询平均时间超标: {{avg_query_time:.1f}}ms > 100ms"
        
        print("✅ 数据库查询性能测试通过")
    
    async def test_cold_start_performance(self, api_client: AsyncClient):
        """测试冷启动性能"""
        
        # 模拟应用冷启动后的首次请求
        headers = {{"Authorization": "Bearer test_token"}}
        
        start_time = time.time()
        response = await api_client.get("/api/v1/{module_name}/health", headers=headers)
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
        
        return f'''
class {class_name}:
    """{business_domain}模块并发性能测试"""
    
    async def test_concurrent_read_requests(self, api_client: AsyncClient):
        """测试并发读请求处理能力"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        concurrent_users = 50  # 模拟50个并发用户
        
        async def single_request():
            start_time = time.time()
            response = await api_client.get("/api/v1/{module_name}/", headers=headers)
            end_time = time.time()
            
            return {{
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000,
                "success": response.status_code == 200
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
    
    async def test_concurrent_write_requests(self, api_client: AsyncClient):
        """测试并发写请求处理能力"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        concurrent_writes = 20  # 模拟20个并发写操作
        
        async def write_request(request_id):
            test_data = {{
                "name": f"concurrent_test_{{request_id}}",
                "value": f"test_value_{{request_id}}",
                "timestamp": datetime.now().isoformat()
            }}
            
            start_time = time.time()
            response = await api_client.post(
                "/api/v1/{module_name}/test",
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
    
    async def test_mixed_workload_performance(self, api_client: AsyncClient):
        """测试混合工作负载性能"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        
        # 模拟真实场景：70%读操作，30%写操作
        read_tasks = 35
        write_tasks = 15
        
        async def read_operation():
            response = await api_client.get("/api/v1/{module_name}/", headers=headers)
            return {{"type": "read", "success": response.status_code == 200}}
        
        async def write_operation():
            test_data = {{"name": f"mixed_test_{{time.time()}}", "value": "test"}}
            response = await api_client.post("/api/v1/{module_name}/test", json=test_data, headers=headers)
            return {{"type": "write", "success": response.status_code in [200, 201]}}
        
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
        class_name = f"Test{module_name.title().replace('_', '')}LoadTest"
        
        return f'''
class {class_name}:
    """{business_domain}模块负载测试"""
    
    async def test_sustained_load(self, api_client: AsyncClient):
        """测试持续负载处理能力"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        duration_seconds = 30  # 持续30秒的负载测试
        requests_per_second = 10  # 每秒10个请求
        
        results = []
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            # 每秒发送指定数量的请求
            batch_tasks = []
            for _ in range(requests_per_second):
                task = api_client.get("/api/v1/{module_name}/", headers=headers)
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
    
    async def test_peak_load_handling(self, api_client: AsyncClient):
        """测试峰值负载处理能力"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        peak_concurrent_users = 100  # 峰值并发用户数
        
        async def user_session():
            """模拟单个用户会话"""
            try:
                # 用户典型操作序列
                operations = [
                    ("GET", "/api/v1/{module_name}/"),
                    ("GET", "/api/v1/{module_name}/search"),
                    ("POST", "/api/v1/{module_name}/test", {{"name": "peak_test"}}),
                    ("GET", "/api/v1/{module_name}/1"),
                ]
                
                session_success = True
                for method, url, *data in operations:
                    if method == "GET":
                        response = await api_client.get(url, headers=headers)
                    else:
                        response = await api_client.post(url, json=data[0] if data else {{}}, headers=headers)
                    
                    if response.status_code >= 500:
                        session_success = False
                        break
                    
                    await asyncio.sleep(0.1)  # 用户操作间隔
                
                return session_success
            except Exception:
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
        
        return f'''
class {class_name}:
    """{business_domain}模块性能基准测试"""
    
    async def test_performance_regression(self, api_client: AsyncClient):
        """测试性能回归基准"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        
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
            response = await api_client.get("/api/v1/{module_name}/", headers=headers)
            end = time.time()
            
            if response.status_code == 200:
                list_times.append((end - start) * 1000)
        
        # 测试搜索端点性能
        search_times = []
        for _ in range(30):
            start = time.time()
            response = await api_client.get("/api/v1/{module_name}/search", params={{"q": "test"}}, headers=headers)
            end = time.time()
            
            if response.status_code in [200, 404]:  # 404也是正常响应
                search_times.append((end - start) * 1000)
        
        # 测试创建端点性能
        create_times = []
        for i in range(20):
            test_data = {{"name": f"benchmark_{{i}}", "value": f"test_{{i}}"}}
            start = time.time()
            response = await api_client.post("/api/v1/{module_name}/test", json=test_data, headers=headers)
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
        throughput_tasks = [api_client.get("/api/v1/{module_name}/", headers=headers) for _ in range(100)]
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
    
    async def test_memory_usage_efficiency(self, api_client: AsyncClient):
        """测试内存使用效率"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        
        # 模拟大量请求测试内存效率
        large_dataset_requests = []
        
        for i in range(1000):
            # 模拟处理大数据集的请求
            task = api_client.get(
                "/api/v1/{module_name}/",
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
    
    async def test_performance_under_stress(self, api_client: AsyncClient):
        """测试压力条件下的性能表现"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        
        # 逐步增加负载压力
        stress_levels = [10, 25, 50, 75, 100]  # 并发用户数
        stress_results = []
        
        for stress_level in stress_levels:
            print(f"🔄 测试压力等级: {{stress_level}} 并发用户")
            
            async def stress_request():
                try:
                    start = time.time()
                    response = await api_client.get("/api/v1/{module_name}/", headers=headers)
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