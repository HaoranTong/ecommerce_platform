# 系统监控和告警配置指南

## 文档说明
- **内容**：系统监控配置、性能指标、告警规则、监控工具
- **使用者**：运维人员、系统管理员、开发团队
- **更新频率**：监控配置变更时更新
- **关联文档**：[部署指南](deployment.md)、[故障排除](troubleshooting.md)、[运维手册](runbook.md)

**[CHECK:DOC-001]** 监控配置必须在部署前完成验证

---

## 监控架构概览

### 监控技术栈
```
[Prometheus] → 指标收集和存储
[Grafana] → 数据可视化和仪表盘
[AlertManager] → 告警规则和通知
[Node Exporter] → 系统指标收集
[Blackbox Exporter] → 服务健康检查
```

### 监控层次划分
- **基础设施监控**：服务器、网络、存储
- **应用监控**：业务指标、性能指标
- **业务监控**：用户体验、业务流程
- **安全监控**：访问控制、异常行为

**[CHECK:DOC-003]** 监控层次必须覆盖所有关键系统组件

---

## Prometheus配置

### 核心配置文件
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # 应用监控
  - job_name: 'ecommerce-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
    
  # 数据库监控
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']
      
  # Redis监控
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
      
  # 系统监控
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
      
  # 服务健康检查
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://api.ecommerce.com/api/health
        - https://api.ecommerce.com/api/metrics
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

### 告警规则配置
```yaml
# alert_rules.yml
groups:
- name: ecommerce.rules
  rules:
  # 应用可用性告警
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "服务 {{ $labels.job }} 不可用"
      description: "{{ $labels.job }} 服务已停止响应超过1分钟"
      
  # 响应时间告警
  - alert: HighResponseTime
    expr: http_request_duration_seconds{quantile="0.95"} > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "API响应时间过高"
      description: "95%分位数响应时间超过2秒，当前值: {{ $value }}s"
      
  # 错误率告警
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "HTTP 5xx错误率过高"
      description: "5xx错误率超过10%，当前值: {{ $value }}"
      
  # 数据库连接告警
  - alert: DatabaseConnectionHigh
    expr: mysql_global_status_threads_connected / mysql_global_variables_max_connections > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "数据库连接数过高"
      description: "MySQL连接使用率超过80%，当前: {{ $value }}%"
      
  # 内存使用告警
  - alert: HighMemoryUsage
    expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 0.9
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "内存使用率过高"
      description: "服务器内存使用率超过90%，当前: {{ $value }}%"
      
  # 磁盘空间告警
  - alert: DiskSpaceLow
    expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} < 0.1
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "磁盘空间不足"
      description: "根分区可用空间小于10%，剩余: {{ $value }}%"
      
  # CPU使用告警
  - alert: HighCpuUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "CPU使用率过高"
      description: "CPU使用率持续10分钟超过85%，当前: {{ $value }}%"
```

**[CHECK:DOC-002]** 告警规则必须与业务SLA保持一致

---

## AlertManager配置

### 告警路由配置
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alerts@ecommerce.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: critical-alerts
  - match:
      severity: warning
    receiver: warning-alerts

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://webhook:5000/alerts'

- name: critical-alerts
  email_configs:
  - to: 'ops-team@ecommerce.com'
    subject: '🚨 严重告警: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    body: |
      告警详情:
      {{ range .Alerts }}
      - 告警: {{ .Annotations.summary }}
      - 描述: {{ .Annotations.description }}
      - 时间: {{ .StartsAt }}
      {{ end }}
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts'
    title: '严重告警'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

- name: warning-alerts
  email_configs:
  - to: 'dev-team@ecommerce.com'
    subject: '⚠️  警告告警: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

---

## 应用指标配置

### FastAPI指标集成
```python
# app/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps

# 定义指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_database_connections',
    'Number of active database connections'
)

BUSINESS_METRICS = {
    'user_registrations': Counter('user_registrations_total', 'Total user registrations'),
    'orders_created': Counter('orders_created_total', 'Total orders created'),
    'payments_processed': Counter('payments_processed_total', 'Total payments processed'),
}

def monitor_requests(func):
    """请求监控装饰器"""
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        start_time = time.time()
        method = request.method
        endpoint = request.url.path
        
        try:
            response = await func(request, *args, **kwargs)
            status = response.status_code
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
            return response
        except Exception as e:
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
            raise
        finally:
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
    
    return wrapper

def track_business_event(event_type: str):
    """业务事件追踪"""
    if event_type in BUSINESS_METRICS:
        BUSINESS_METRICS[event_type].inc()
```

### 健康检查端点
```python
# app/health.py
from fastapi import APIRouter
from app.database import SessionLocal
from app.core.redis import redis_client
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    """系统健康检查"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "external_services": await check_external_services()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }

async def check_database():
    """数据库连接检查"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception:
        return False

async def check_redis():
    """Redis连接检查"""
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False
```

**[CHECK:DOC-001]** 健康检查端点必须在负载均衡器配置中启用

---

## Grafana仪表盘

### 系统概览仪表盘
- **服务状态面板**：所有服务的在线状态
- **性能指标面板**：响应时间、吞吐量、错误率
- **资源使用面板**：CPU、内存、磁盘使用率
- **业务指标面板**：用户注册、订单量、支付成功率

### 应用监控仪表盘
```json
{
  "dashboard": {
    "title": "电商平台应用监控",
    "panels": [
      {
        "title": "请求QPS",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "响应时间分布",
        "type": "heatmap",
        "targets": [
          {
            "expr": "rate(http_request_duration_seconds_bucket[5m])"
          }
        ]
      },
      {
        "title": "错误率",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## 日志监控

### 集中日志收集
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
      
  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      
  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
      
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.10.0
    volumes:
      - /var/log:/var/log:ro
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml
```

### 日志解析配置
```ruby
# logstash/pipeline/logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "ecommerce-app" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ecommerce-logs-%{+YYYY.MM.dd}"
  }
}
```

**[CHECK:DOC-003]** 日志监控配置必须包含敏感信息过滤规则

---

## 性能监控指标

### 关键业务指标
| 指标类型 | 指标名称 | 目标值 | 告警阈值 |
|----------|----------|--------|----------|
| 可用性 | 服务可用率 | > 99.9% | < 99% |
| 性能 | API响应时间(P95) | < 500ms | > 2s |
| 性能 | 数据库查询时间(P95) | < 100ms | > 500ms |
| 容量 | 并发用户数 | 1000+ | > 5000 |
| 错误 | 错误率 | < 0.1% | > 1% |

### 系统资源指标
| 资源类型 | 指标名称 | 正常范围 | 告警阈值 |
|----------|----------|----------|----------|
| CPU | 使用率 | < 70% | > 85% |
| 内存 | 使用率 | < 80% | > 90% |
| 磁盘 | 使用率 | < 85% | > 95% |
| 网络 | 带宽使用率 | < 70% | > 90% |

---

## Docker监控配置

### 容器监控
```yaml
# docker-compose.monitoring.yml (续)
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      
  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
```

---

## 监控最佳实践

### 1. 指标设计原则
- **RED方法**：Rate(速率)、Errors(错误)、Duration(持续时间)
- **USE方法**：Utilization(使用率)、Saturation(饱和度)、Errors(错误)
- **四个黄金信号**：延迟、流量、错误、饱和度

### 2. 告警策略
- **分级告警**：Critical > Warning > Info
- **告警抑制**：避免告警风暴
- **告警升级**：自动升级未处理的关键告警

### 3. 监控治理
- **指标标准化**：统一命名规范
- **仪表盘管理**：按角色和场景分类
- **容量规划**：基于监控数据进行容量评估

**[CHECK:DOC-002]** 监控配置变更必须同步更新相关文档

---

## 相关文档
- [部署指南](deployment.md) - 监控组件部署配置
- [故障排除](troubleshooting.md) - 监控告警处理流程
- [运维手册](runbook.md) - 日常监控操作指南
- [MASTER工作流程](../MASTER.md) - 监控配置检查点
