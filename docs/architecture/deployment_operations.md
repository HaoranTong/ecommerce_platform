# 部署与运维规范

## 🎯 部署策略

### 核心原则
1. **基础设施即代码**: 所有环境配置代码化管理
2. **蓝绿部署**: 零停机时间部署
3. **容器化优先**: Docker容器化部署
4. **自动化流水线**: CI/CD自动化部署
5. **环境一致性**: 开发、测试、生产环境保持一致

### 部署架构
```mermaid
graph TB
    A[Git Repository] --> B[CI/CD Pipeline]
    B --> C[Build Docker Images]
    C --> D[Push to Registry]
    D --> E[Deploy to Staging]
    E --> F[Automated Tests]
    F --> G{Tests Pass?}
    G -->|Yes| H[Deploy to Production]
    G -->|No| I[Rollback & Alert]
    H --> J[Health Check]
    J --> K[Monitor & Alert]
```

## 🐳 容器化配置

### Docker基础配置
```yaml
# 配置文件: config/deployment/docker.yaml
docker_config:
  # 基础镜像策略
  base_images:
    python: "python:3.11-slim"
    node: "node:18-alpine"
    nginx: "nginx:1.24-alpine"
    
  # 镜像构建配置
  build:
    multi_stage: true
    layer_caching: true
    security_scanning: true
    size_optimization: true
    
  # 容器运行配置
  runtime:
    security:
      non_root_user: true
      read_only_filesystem: true
      no_new_privileges: true
    resources:
      memory_limit: "512Mi"
      cpu_limit: "500m"
      memory_request: "256Mi"
      cpu_request: "250m"
```

### 多阶段Dockerfile
```dockerfile
# Dockerfile
# 第一阶段：构建阶段
FROM python:3.11-slim as builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.11-slim as runtime

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制依赖
COPY --from=builder /root/.local /home/appuser/.local

# 设置环境变量
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 复制应用代码
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# 设置权限
RUN chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  # 应用服务
  app:
    build: 
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:password@mysql:3306/ecommerce
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    restart: unless-stopped
    
  # 数据库服务
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ecommerce
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    restart: unless-stopped
    
  # Redis缓存服务
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M
    restart: unless-stopped
    
  # Nginx反向代理
  nginx:
    image: nginx:1.24-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

## ☸️ Kubernetes部署

### Kubernetes配置
```yaml
# 配置文件: config/deployment/kubernetes.yaml
kubernetes_config:
  # 集群配置
  cluster:
    namespace: "ecommerce-prod"
    replicas: 3
    rolling_update:
      max_surge: 1
      max_unavailable: 1
    
  # 资源配置
  resources:
    requests:
      cpu: "250m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"
      
  # 网络配置
  networking:
    service_type: "ClusterIP"
    ingress_enabled: true
    ssl_enabled: true
    
  # 存储配置
  storage:
    persistent_volumes: true
    storage_class: "fast-ssd"
    backup_enabled: true
```

### Deployment配置
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-app
  namespace: ecommerce-prod
  labels:
    app: ecommerce
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: ecommerce
  template:
    metadata:
      labels:
        app: ecommerce
        version: v1
    spec:
      containers:
      - name: app
        image: registry.example.com/ecommerce:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: redis-config
              key: url
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
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
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
```

### Service和Ingress配置
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ecommerce-service
  namespace: ecommerce-prod
spec:
  selector:
    app: ecommerce
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
  namespace: ecommerce-prod
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.ecommerce.com
    secretName: ecommerce-tls
  rules:
  - host: api.ecommerce.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ecommerce-service
            port:
              number: 80
```

## 🚀 CI/CD流水线

### GitHub Actions工作流
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.image.outputs.image }}
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Output image
      id: image
      run: echo "image=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}" >> $GITHUB_OUTPUT

  security-scan:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ needs.build.outputs.image }}
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'

  deploy-staging:
    needs: [build, security-scan]
    runs-on: ubuntu-latest
    environment: staging
    steps:
    - name: Deploy to staging
      run: |
        kubectl set image deployment/ecommerce-app app=${{ needs.build.outputs.image }} -n ecommerce-staging
        kubectl rollout status deployment/ecommerce-app -n ecommerce-staging
        
    - name: Run smoke tests
      run: |
        curl -f https://staging-api.ecommerce.com/health
        pytest tests/smoke/ --base-url=https://staging-api.ecommerce.com

  deploy-production:
    needs: [build, security-scan, deploy-staging]
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        kubectl set image deployment/ecommerce-app app=${{ needs.build.outputs.image }} -n ecommerce-prod
        kubectl rollout status deployment/ecommerce-app -n ecommerce-prod
        
    - name: Verify deployment
      run: |
        curl -f https://api.ecommerce.com/health
        kubectl get pods -n ecommerce-prod
```

### 部署脚本配置
```yaml
# 配置文件: config/deployment/scripts.yaml
deployment_scripts:
  # 预部署检查
  pre_deploy:
    - name: "数据库备份"
      command: "scripts/backup_database.sh"
      required: true
    - name: "健康检查"
      command: "scripts/health_check.sh"
      required: true
    - name: "依赖检查"
      command: "scripts/dependency_check.sh"
      required: true
      
  # 部署步骤
  deploy:
    - name: "应用更新"
      command: "kubectl apply -f k8s/"
      timeout: "300s"
    - name: "等待就绪"
      command: "kubectl rollout status deployment/ecommerce-app"
      timeout: "600s"
    - name: "数据库迁移"
      command: "kubectl exec -it deployment/ecommerce-app -- alembic upgrade head"
      timeout: "120s"
      
  # 部署后验证
  post_deploy:
    - name: "API健康检查"
      command: "scripts/api_health_check.sh"
      required: true
    - name: "数据库连接测试"
      command: "scripts/db_connection_test.sh"
      required: true
    - name: "缓存连接测试"
      command: "scripts/redis_connection_test.sh"
      required: true
    - name: "烟雾测试"
      command: "pytest tests/smoke/"
      required: true
```

## 📊 监控与日志

### 监控配置
```yaml
# 配置文件: config/deployment/monitoring.yaml
monitoring_config:
  # 应用监控
  application:
    health_endpoints:
      - "/health"      # 应用健康检查
      - "/ready"       # 就绪检查
      - "/metrics"     # Prometheus指标
    metrics:
      - "request_count"
      - "request_duration"
      - "error_rate"
      - "active_users"
      
  # 基础设施监控
  infrastructure:
    cpu_threshold: 80
    memory_threshold: 85
    disk_threshold: 90
    network_threshold: 80
    
  # 业务监控
  business:
    - name: "用户注册数"
      metric: "user_registrations_total"
      alert_threshold: "< 10/hour"
    - name: "订单成功率"
      metric: "order_success_rate"
      alert_threshold: "< 95%"
    - name: "支付成功率"
      metric: "payment_success_rate"
      alert_threshold: "< 98%"
      
  # 告警配置
  alerts:
    channels: ["slack", "email", "pagerduty"]
    severity_levels: ["critical", "warning", "info"]
    escalation_rules:
      critical: "immediate"
      warning: "15m"
      info: "1h"
```

### Prometheus配置
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
  - job_name: 'ecommerce-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 日志配置
```yaml
# 配置文件: config/deployment/logging.yaml
logging_config:
  # 日志级别
  levels:
    root: "INFO"
    app: "INFO"
    sqlalchemy: "WARNING"
    uvicorn: "INFO"
    
  # 日志格式
  formatters:
    json:
      format: |
        {
          "timestamp": "%(asctime)s",
          "level": "%(levelname)s",
          "logger": "%(name)s",
          "message": "%(message)s",
          "module": "%(module)s",
          "function": "%(funcName)s",
          "line": %(lineno)d,
          "trace_id": "%(trace_id)s",
          "span_id": "%(span_id)s"
        }
        
  # 日志输出
  handlers:
    console:
      class: "logging.StreamHandler"
      formatter: "json"
      level: "INFO"
    file:
      class: "logging.handlers.RotatingFileHandler"
      filename: "/var/log/app/app.log"
      maxBytes: 104857600  # 100MB
      backupCount: 10
      formatter: "json"
      
  # 日志采集
  collection:
    agent: "fluentd"
    destination: "elasticsearch"
    retention: "30d"
    compression: true
```

## 🔐 安全配置

### 安全策略
```yaml
# 配置文件: config/deployment/security.yaml
security_config:
  # 容器安全
  container:
    scan_images: true
    vulnerability_threshold: "HIGH"
    runtime_security: true
    network_policies: true
    
  # 网络安全
  network:
    ssl_termination: "ingress"
    certificate_management: "cert-manager"
    security_headers: true
    rate_limiting: true
    
  # 数据安全
  data:
    encryption_at_rest: true
    encryption_in_transit: true
    backup_encryption: true
    key_rotation: "monthly"
    
  # 访问控制
  access:
    rbac_enabled: true
    service_mesh: "istio"
    mTLS: true
    authentication: "oauth2"
```

### 安全策略示例
```yaml
# k8s/security-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ecommerce-network-policy
  namespace: ecommerce-prod
spec:
  podSelector:
    matchLabels:
      app: ecommerce
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: nginx-ingress
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mysql
    ports:
    - protocol: TCP
      port: 3306
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

## 🔄 备份与恢复

### 备份策略
```yaml
# 配置文件: config/deployment/backup.yaml
backup_config:
  # 数据库备份
  database:
    frequency: "daily"
    time: "02:00"
    retention: "30d"
    compression: true
    encryption: true
    verification: true
    
  # 文件备份
  files:
    frequency: "weekly"
    retention: "90d"
    incremental: true
    exclude_patterns: ["*.tmp", "*.log", "__pycache__"]
    
  # 配置备份
  configuration:
    frequency: "on_change"
    retention: "180d"
    version_control: true
    
  # 灾难恢复
  disaster_recovery:
    rpo: "1h"    # Recovery Point Objective
    rto: "4h"    # Recovery Time Objective
    backup_sites: 2
    testing_frequency: "quarterly"
```

### 备份脚本
```bash
#!/bin/bash
# scripts/backup_database.sh

set -e

# 配置变量
BACKUP_DIR="/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="ecommerce_backup_${DATE}.sql.gz"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行数据库备份
mysqldump \
  --host=${DB_HOST} \
  --user=${DB_USER} \
  --password=${DB_PASSWORD} \
  --single-transaction \
  --routines \
  --triggers \
  ecommerce | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# 验证备份文件
if [ ! -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
  echo "备份失败: 文件不存在"
  exit 1
fi

# 检查备份文件大小
file_size=$(stat -c%s "${BACKUP_DIR}/${BACKUP_FILE}")
if [ $file_size -lt 1000 ]; then
  echo "备份失败: 文件大小异常"
  exit 1
fi

# 清理旧备份
find $BACKUP_DIR -name "ecommerce_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "数据库备份完成: ${BACKUP_FILE}"
```

## 📈 性能优化

### 应用层优化
```yaml
# 配置文件: config/deployment/performance.yaml
performance_config:
  # 应用优化
  application:
    workers: 4
    worker_connections: 1000
    keepalive_timeout: 65
    client_max_body_size: "10M"
    
  # 数据库优化
  database:
    connection_pool_size: 20
    max_overflow: 30
    pool_timeout: 30
    pool_recycle: 3600
    query_timeout: 30
    
  # 缓存优化
  cache:
    redis_pool_size: 50
    redis_timeout: 5
    cache_ttl: 3600
    compression: true
    
  # CDN配置
  cdn:
    provider: "cloudflare"
    cache_everything: false
    browser_cache_ttl: 86400
    edge_cache_ttl: 604800
```

## 🎯 运维最佳实践

### 部署检查清单
```yaml
# 配置文件: config/deployment/checklist.yaml
deployment_checklist:
  pre_deployment:
    - "✅ 代码审查完成"
    - "✅ 自动化测试通过"
    - "✅ 安全扫描通过"
    - "✅ 性能测试通过"
    - "✅ 数据库备份完成"
    - "✅ 回滚计划准备完成"
    
  deployment:
    - "✅ 蓝绿部署就绪"
    - "✅ 流量切换策略确认"
    - "✅ 监控告警配置"
    - "✅ 日志收集配置"
    
  post_deployment:
    - "✅ 健康检查通过"
    - "✅ 烟雾测试通过"
    - "✅ 业务指标正常"
    - "✅ 性能指标正常"
    - "✅ 错误率监控正常"
```

## 🎯 总结

这套部署与运维规范提供了：

1. **完整的容器化方案**: 从Docker到Kubernetes的完整部署
2. **自动化CI/CD**: GitHub Actions驱动的自动化流水线
3. **全面监控体系**: 应用、基础设施、业务全方位监控
4. **安全最佳实践**: 容器安全、网络安全、数据安全
5. **备份恢复策略**: 完整的数据保护和灾难恢复方案
6. **性能优化**: 应用层到基础设施的性能调优
7. **运维自动化**: 配置驱动的运维管理

通过这套规范，确保电商平台的高可用、高性能、高安全的稳定运行。
