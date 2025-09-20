# 性能测试目录

## 📋 目录说明

本目录包含系统性能测试，验证应用程序在各种负载条件下的表现，确保满足性能要求。

## 📁 文件结构

```
performance/
├── README.md                           # 本说明文档
└── test_shopping_cart_performance.py   # 购物车性能测试
```

## 🎯 测试范围

### 性能测试类型
- **负载测试**: 验证正常用户负载下的系统表现
- **压力测试**: 测试系统在极限负载下的稳定性
- **响应时间测试**: 验证API响应时间符合要求
- **并发测试**: 测试多用户同时操作的性能影响

### 当前测试模块
- **购物车性能**: 测试购物车添加、更新、删除操作的性能指标

## 📊 性能指标

### 响应时间要求
- **API响应时间**: < 200ms (90th percentile)
- **数据库查询**: < 100ms (平均)
- **页面加载时间**: < 2s (完整页面)

### 吞吐量要求
- **并发用户数**: 支持100+并发用户
- **每秒请求数**: > 500 RPS
- **数据处理能力**: > 1000 records/second

## 🛠️ 执行方法

### 运行性能测试
```powershell
# 执行所有性能测试
pytest tests/performance/ -v

# 执行特定模块性能测试
pytest tests/performance/test_shopping_cart_performance.py -v

# 生成性能报告
pytest tests/performance/ --benchmark-only --benchmark-sort=mean
```

### 性能分析
```powershell
# 使用memory_profiler分析内存使用
python -m memory_profiler tests/performance/test_shopping_cart_performance.py

# 使用cProfile分析函数调用
python -m cProfile -o profile_output tests/performance/test_shopping_cart_performance.py
```

## 🔧 工具和依赖

### 性能测试工具
- **pytest-benchmark**: 微基准测试框架
- **locust**: 负载测试和压力测试
- **memory_profiler**: 内存使用分析
- **cProfile**: 函数调用分析

### 监控工具
- **APM工具**: 应用性能监控
- **数据库监控**: SQL查询性能分析
- **系统监控**: CPU、内存、IO使用情况

## 📚 相关文档

- **[测试标准文档](../../docs/standards/testing-standards.md)** - 性能测试规范
- **[性能标准](../../docs/standards/performance-standards.md)** - 性能指标要求