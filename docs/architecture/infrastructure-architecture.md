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

### 容器化基础设施

```yaml
# Kubernetes集群架构
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce-platform

---
# 应用部署配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-web
  namespace: ecommerce-platform
spec:
  replicas: 3  # 高可用部署
  selector:
    matchLabels:
      app: ecommerce-web
  template:
    metadata:
      labels:
        app: ecommerce-web
    spec:
      containers:
      - name: web
        image: ecommerce-platform:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# 负载均衡服务
apiVersion: v1
kind: Service
metadata:
  name: ecommerce-web-service
  namespace: ecommerce-platform
spec:
  selector:
    app: ecommerce-web
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 自动扩缩容策略

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
    - MYSQL_DATABASE=ecommerce_platform
    - MYSQL_USER=ecommerce_user
    - MYSQL_PASSWORD=${DB_PASSWORD}
  volumes:
    - mysql_master_data:/var/lib/mysql
    - ./conf/mysql/master.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf
  command: --server-id=1 --log-bin=mysql-bin --binlog-format=ROW
  
# 从数据库配置  
mysql_slave:
  image: mysql:8.0
  environment:
    - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
  volumes:
    - mysql_slave_data:/var/lib/mysql
    - ./conf/mysql/slave.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf
  command: --server-id=2 --relay-log=mysql-relay-bin
  depends_on:
    - mysql_master

# 数据库连接池配置
connection_pool:
  max_connections: 100
  min_connections: 10
  connection_timeout: 30
  idle_timeout: 600
  max_lifetime: 3600
```

### Redis集群架构

```yaml
# Redis集群配置
redis_cluster:
  image: redis/redis-stack:latest
  deploy:
    replicas: 6  # 3主3从
  command: 
    - redis-server
    - /usr/local/etc/redis/redis.conf
    - --cluster-enabled yes
    - --cluster-config-file nodes.conf
    - --cluster-node-timeout 5000
    - --appendonly yes
  volumes:
    - redis_data:/data
  environment:
    - REDIS_PASSWORD=${REDIS_PASSWORD}

# Redis哨兵配置
redis_sentinel:
  image: redis:7.0-alpine
  deploy:
    replicas: 3
  command:
    - redis-sentinel
    - /usr/local/etc/redis/sentinel.conf
  volumes:
    - ./conf/redis/sentinel.conf:/usr/local/etc/redis/sentinel.conf
```

### 对象存储架构

```yaml
# 对象存储配置 (兼容S3 API)
object_storage:
  provider: "aliyun_oss"  # 或 "tencent_cos", "aws_s3"
  config:
    endpoint: "https://oss-cn-hangzhou.aliyuncs.com"
    bucket_name: "ecommerce-platform-assets"
    access_key_id: "${OSS_ACCESS_KEY}"
    access_key_secret: "${OSS_ACCESS_SECRET}"
    region: "cn-hangzhou"
    
# CDN加速配置
cdn_config:
  provider: "aliyun_cdn"
  domains:
    - "assets.ecommerce-platform.com"  # 静态资源域名
    - "images.ecommerce-platform.com"  # 图片资源域名
  cache_rules:
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