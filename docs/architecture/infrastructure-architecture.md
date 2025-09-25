<!--
文档说明：
- 内容：基础设施架构设计，包括计算、存储、网络、监控、安全等基础设施组件
- 使用方法：基础设施规划和运维实施的权威指导文档
- 更新方法：基础设施架构调整或技术选型变更时更新
- 引用关系：被overview.md引用，为应用架构提供基础设施支撑
- 更新频率：基础设施架构变更时
-->

# 基础设施架构设计

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-22  
👤 **负责人**: 基础设施架构师  
🔄 **最后更新**: 2025-09-22  
📋 **版本**: v1.0.0  

## 基础设施架构概览

### 整体基础设施拓扑

```
┌─────────────────────────────────────────────────────────────────┐
│                    电商平台基础设施架构                           │
├─────────────────────────────────────────────────────────────────┤
│                          用户接入层                              │
│    CDN (全球分发) + WAF (Web防火墙) + DDoS防护                   │
├─────────────────────────────────────────────────────────────────┤
│                          负载均衡层                              │
│     Nginx/HAProxy (L4/L7负载均衡) + SSL终结                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  计算资源   │  │   存储资源   │  │   网络资源   │  │   安全资源   │ │
│  │ K8s集群     │  │  数据库集群  │  │  VPC网络    │  │  身份认证    │ │
│  │ 容器编排    │  │  对象存储   │  │  子网隔离    │  │  访问控制    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                          监控运维层                              │
│   Prometheus+Grafana + ELK Stack + 链路追踪 + 告警系统          │
└─────────────────────────────────────────────────────────────────┘
```

## 计算资源架构

> **具体部署配置方案**: 详见 [部署实现设计](../design/system/deployment-design.md)

### 容器化部署策略

**容器编排原则**:
- **高可用部署**: 应用服务至少3个实例，支持滚动更新和零停机部署
- **资源隔离**: 通过Namespace和ResourceQuota实现多环境资源隔离
- **健康检查**: 配置存活性和就绪性检查，确保服务健康状态
- **配置分离**: 敏感配置通过Secret管理，普通配置通过ConfigMap

**服务发现机制**:
- **内部服务**: 通过Kubernetes Service实现服务间发现和负载均衡
- **外部暴露**: 通过Ingress Controller统一入口和路由管理
- **服务网格**: 未来可考虑引入Istio实现更复杂的服务治理
- **DNS解析**: 基于CoreDNS的内部服务名称解析

### 自动扩缩容架构

**水平扩缩容策略**:
- **CPU指标**: CPU使用率超过70%时自动扩容，低于30%时缩容
- **内存指标**: 内存使用率超过80%时自动扩容，避免OOM
- **自定义指标**: 基于QPS、响应时间等业务指标的扩缩容
- **时间窗口**: 扩容立即生效，缩容需要稳定观察窗口

```yaml
# HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ecommerce-web-hpa
  namespace: ecommerce-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ecommerce-web
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

## 存储资源架构

### 数据库集群架构

```yaml
# MySQL高可用集群配置
# 主数据库配置
mysql_master:
  image: mysql:8.0
  environment:
    - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
## 存储资源架构

### 数据库架构策略

**高可用部署**:
- **主从架构**: 一主多从的读写分离架构，主库负责写入，从库负责读取
- **故障切换**: 自动检测主库故障并切换到从库，最小化服务中断时间
- **数据同步**: 基于二进制日志的异步复制，确保数据最终一致性
- **备份策略**: 定时全量备份和增量备份，支持点时间恢复

**连接池管理**:
- **连接复用**: 通过连接池减少连接建立开销，提升数据库性能
- **连接监控**: 监控连接池状态，及时发现连接泄露和异常
- **动态调整**: 根据业务负载动态调整连接池大小
- **超时控制**: 合理设置连接超时和查询超时时间

### 缓存架构策略

**Redis集群部署**:
- **高可用集群**: 采用Redis Cluster模式，支持数据分片和自动故障转移
- **主从复制**: 每个主节点配置从节点，提供数据冗余和读取扩展
- **哨兵监控**: 部署Redis Sentinel监控集群状态，自动故障发现和切换
- **数据持久化**: 配置RDB快照和AOF日志双重持久化机制

**缓存策略原则**:
- **多层缓存**: 应用内存缓存、Redis分布式缓存、CDN边缘缓存
- **缓存预热**: 系统启动时预加载热点数据，减少冷启动影响
- **失效策略**: 基于TTL和LRU的缓存失效策略，合理利用内存资源
- **一致性保证**: 缓存与数据库的数据一致性保证机制

### 对象存储架构

**云存储集成**:
- **多云支持**: 支持阿里云OSS、腾讯云COS、AWS S3等主流对象存储
- **存储分层**: 热数据标准存储，冷数据归档存储，降低存储成本
- **访问控制**: 基于权限的文件访问控制，防止未授权访问
- **备份冗余**: 跨地域备份，确保数据安全和可用性

**CDN加速策略**:
- **全球分发**: 通过CDN节点就近访问，提升静态资源加载速度
- **智能缓存**: 根据访问频率和地理位置智能缓存热点内容
- **HTTPS加速**: 全站HTTPS传输，兼顾安全性和性能
- **实时刷新**: 支持缓存内容的实时刷新和预加载
    - pattern: "*.jpg,*.png,*.gif"
      ttl: 86400  # 图片缓存24小时
    - pattern: "*.js,*.css"
      ttl: 3600   # 静态文件缓存1小时
```

## 网络架构设计

### VPC网络规划

```
VPC: ecommerce-platform-vpc (10.0.0.0/16)
├── 公网子网 (10.0.1.0/24) - 负载均衡、NAT网关
├── 应用子网 (10.0.2.0/24) - Web应用服务器
├── 数据库子网 (10.0.3.0/24) - 数据库集群
├── 缓存子网 (10.0.4.0/24) - Redis集群
├── 监控子网 (10.0.5.0/24) - 监控系统
└── 管理子网 (10.0.6.0/24) - 堡垒机、跳板机
```

### 负载均衡配置

```nginx
# Nginx负载均衡配置
upstream ecommerce_backend {
    least_conn;
    server app1.internal:8000 max_fails=3 fail_timeout=30s;
    server app2.internal:8000 max_fails=3 fail_timeout=30s;
    server app3.internal:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# API网关配置
server {
    listen 80;
    listen 443 ssl http2;
    server_name api.ecommerce-platform.com;
    
    # SSL配置
    ssl_certificate /etc/nginx/ssl/ecommerce-platform.crt;
    ssl_certificate_key /etc/nginx/ssl/ecommerce-platform.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 安全头配置
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Strict-Transport-Security "max-age=31536000";
    
    # 限流配置
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://ecommerce_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态资源代理
    location /static/ {
        alias /var/www/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

## 电商特色基础设施

### 高并发处理架构

```yaml
# 秒杀场景基础设施
seckill_infrastructure:
  # 流量削峰
  message_queue:
    type: "RabbitMQ"
    queues:
      - name: "seckill_queue"
        max_length: 100000
        message_ttl: 300000  # 5分钟TTL
  
  # 缓存预热
  cache_warming:
    redis_cluster:
      - key_pattern: "seckill:product:*"
        preload_time: "before_activity_5min"
        ttl: 3600
  
  # 限流策略
  rate_limiting:
    - path: "/api/v1/seckill/*"
      rate: "1000r/s"
      burst: 2000
      scope: "global"
    - path: "/api/v1/orders"
      rate: "100r/s" 
      burst: 200
      scope: "per_user"
```

### 直播基础设施

```yaml
# 直播推流基础设施
live_streaming:
  # 流媒体服务器
  media_server:
    type: "SRS"  # Simple Realtime Server
    config:
      rtmp_port: 1935
      http_port: 8080
      hls_enabled: true
      dash_enabled: true
      
  # CDN分发
  streaming_cdn:
    provider: "aliyun_live"
    regions: ["cn-hangzhou", "cn-beijing", "cn-shenzhen"]
    bandwidth_limit: "1000Mbps"
    
  # 录制存储
  recording:
    storage: "oss"
    format: ["mp4", "flv"]
    auto_delete_after: "30days"
```

### 区块链基础设施

```yaml
# 溯源区块链基础设施
blockchain_infrastructure:
  # 区块链节点
  blockchain_node:
    type: "hyperledger_fabric"
    network: "traceability_network"
    organizations:
      - name: "ecommerce_platform"
        peers: 2
        ca: true
      - name: "suppliers"
        peers: 1
        ca: true
        
  # IPFS存储节点
  ipfs_cluster:
    nodes: 3
    replication_factor: 2
    storage_max: "1TB"
    
  # 智能合约
  smart_contracts:
    - name: "traceability_contract"
      version: "v1.0.0"
      functions: ["addRecord", "getHistory", "verify"]
```

## 监控运维架构

### 监控体系设计

```yaml
# Prometheus监控配置
monitoring:
  prometheus:
    scrape_configs:
      - job_name: 'ecommerce-web'
        static_configs:
          - targets: ['ecommerce-web:8000']
        metrics_path: '/metrics'
        scrape_interval: 15s
        
      - job_name: 'mysql'
        static_configs:
          - targets: ['mysql-exporter:9104']
        scrape_interval: 30s
        
      - job_name: 'redis'
        static_configs:
          - targets: ['redis-exporter:9121']
        scrape_interval: 30s
        
      - job_name: 'node-exporter'
        static_configs:
          - targets: ['node-exporter:9100']
        scrape_interval: 15s
        
    # 告警规则
    rule_files:
      - "/etc/prometheus/rules/*.yml"
    
    # 存储配置
    storage:
      tsdb:
        retention_time: "30d"
        retention_size: "100GB"
        
  # Grafana仪表盘
  grafana:
    dashboards:
      - name: "应用性能监控"
        panels: ["QPS", "响应时间", "错误率", "CPU使用率"]
      - name: "数据库监控"  
        panels: ["连接数", "慢查询", "锁等待", "复制延迟"]
      - name: "业务监控"
        panels: ["订单量", "支付成功率", "用户活跃度", "GMV"]
```

### 日志聚合架构

```yaml
# ELK Stack日志聚合
logging:
  elasticsearch:
    cluster_name: "ecommerce-logs"
    nodes: 3
    heap_size: "2g"
    indices:
      - name: "application-logs"
        retention: "30d"
        shards: 5
        replicas: 1
      - name: "access-logs"
        retention: "7d"
        shards: 3
        replicas: 1
        
  logstash:
    pipelines:
      - name: "application"
        input: "beats"
        filter: "json_parser"
        output: "elasticsearch"
      - name: "nginx"
        input: "filebeat"
        filter: "grok_parser"
        output: "elasticsearch"
        
  kibana:
    dashboards:
      - "应用日志分析"
      - "访问日志分析"
      - "错误日志监控"
      - "性能分析"
```

## 安全基础设施

### 网络安全配置

```yaml
# 网络安全策略
security:
  # WAF (Web Application Firewall)
  waf:
    provider: "aliyun_waf"
    rules:
      - name: "SQL注入防护"
        enabled: true
        action: "block"
      - name: "XSS攻击防护"
        enabled: true  
        action: "block"
      - name: "CC攻击防护"
        enabled: true
        threshold: "1000req/min"
        
  # DDoS防护
  ddos_protection:
    provider: "aliyun_ddos"
    bandwidth_threshold: "1Gbps"
    pps_threshold: "100k"
    
  # SSL/TLS配置
  ssl_config:
    certificate_provider: "letsencrypt"
    auto_renewal: true
    protocols: ["TLSv1.2", "TLSv1.3"]
    cipher_suites: "HIGH:!aNULL:!MD5"
```

### 访问控制配置

```yaml
# IAM (Identity and Access Management)
iam:
  # 服务账户
  service_accounts:
    - name: "ecommerce-web"
      permissions:
        - "database:read"
        - "database:write"
        - "cache:read"
        - "cache:write"
        - "storage:read"
        - "storage:write"
        
    - name: "monitoring"
      permissions:
        - "metrics:read"
        - "logs:read"
        
  # 网络策略
  network_policies:
    - name: "web-to-db"
      from: ["ecommerce-web"]
      to: ["mysql", "redis"]
      ports: [3306, 6379]
      
    - name: "monitoring-access"
      from: ["prometheus", "grafana"]
      to: ["all"]
      ports: [8000, 9090, 9100]
```

## 灾备与高可用

### 数据备份策略

```yaml
# 备份配置
backup:
  # 数据库备份
  mysql_backup:
    type: "mysqldump"
    schedule: "0 2 * * *"  # 每天凌晨2点
    retention: "30d"
    storage: "oss"
    encryption: true
    
  # Redis备份
  redis_backup:
    type: "rdb_snapshot"
    schedule: "0 */6 * * *"  # 每6小时一次
    retention: "7d"
    storage: "oss"
    
  # 应用数据备份
  app_backup:
    type: "volume_snapshot"
    schedule: "0 1 * * *"  # 每天凌晨1点
    retention: "7d"
```

### 故障恢复策略

```yaml
# 灾难恢复配置
disaster_recovery:
  # RTO (Recovery Time Objective)
  rto: "1h"
  
  # RPO (Recovery Point Objective)  
  rpo: "15min"
  
  # 故障切换策略
  failover:
    database:
      type: "auto"
      health_check_interval: "10s"
      failover_timeout: "30s"
      
    application:
      type: "auto"
      health_check_endpoint: "/health"
      unhealthy_threshold: 3
      healthy_threshold: 2
```

## 成本优化策略

### 资源优化配置

```yaml
# 成本优化配置
cost_optimization:
  # 弹性伸缩
  auto_scaling:
    scale_out_threshold: 70  # CPU使用率>70%扩容
    scale_in_threshold: 30   # CPU使用率<30%缩容
    cooldown_period: 300     # 冷却期5分钟
    
  # 竞价实例
  spot_instances:
    enabled: true
    max_price: "0.1"  # 最大竞价
    fallback_to_on_demand: true
    
  # 预留实例
  reserved_instances:
    term: "1year"
    payment_option: "partial_upfront"
    instance_types: ["c5.large", "r5.large"]
```

## 相关文档

- [技术架构总览](overview.md) - 整体技术架构设计
- [应用架构设计](application-architecture.md) - 应用层架构实现
- [数据架构设计](data-architecture.md) - 数据存储架构
- [架构演进路线](migration-roadmap.md) - 基础设施演进规划
