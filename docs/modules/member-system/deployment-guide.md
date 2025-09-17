# 会员系统模块 - 部署指南文档

📅 **创建日期**: 2025-09-17  
👤 **运维负责人**: DevOps工程师  
✅ **评审状态**: 设计中  
🔄 **最后更新**: 2025-09-17  

## 部署概述

### 部署目标
- 确保会员系统在生产环境的高可用性和稳定性
- 支持水平扩展以应对业务增长需求
- 提供完整的监控、日志和告警机制
- 实现零停机部署和快速回滚能力
- 保障数据安全和备份恢复机制

### 部署架构
- **容器化部署**: 基于Docker容器化技术
- **编排管理**: 使用Kubernetes进行容器编排
- **负载均衡**: Nginx + Kubernetes Service
- **数据库**: MySQL主从架构 + Redis集群
- **监控告警**: Prometheus + Grafana + AlertManager
- **日志收集**: ELK Stack (Elasticsearch + Logstash + Kibana)

## 环境要求

### 1. 硬件资源需求

#### 生产环境配置
| 组件 | CPU | 内存 | 存储 | 网络 | 实例数 |
|------|-----|------|------|------|--------|
| 应用服务器 | 4核 | 8GB | 100GB SSD | 1Gbps | 3台 |
| MySQL主库 | 8核 | 16GB | 500GB SSD | 1Gbps | 1台 |
| MySQL从库 | 8核 | 16GB | 500GB SSD | 1Gbps | 2台 |
| Redis集群 | 4核 | 8GB | 100GB SSD | 1Gbps | 3台 |
| Nginx负载均衡 | 2核 | 4GB | 50GB SSD | 1Gbps | 2台 |

#### 最小资源要求
| 组件 | CPU | 内存 | 存储 |
|------|-----|------|------|
| 单实例应用 | 2核 | 4GB | 50GB |
| MySQL | 4核 | 8GB | 200GB |
| Redis | 2核 | 4GB | 50GB |

### 2. 软件环境要求

#### 操作系统
- **推荐**: Ubuntu 22.04 LTS / CentOS 8
- **内核版本**: >= 5.4.0
- **Docker版本**: >= 20.10.0
- **Kubernetes版本**: >= 1.25.0

#### 依赖软件
```bash
# 基础依赖
sudo apt-get update
sudo apt-get install -y curl wget git vim

# Docker安装
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker

# Kubernetes安装(kubeadm)
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
```

## 容器化配置

### 1. Dockerfile配置

#### 应用Dockerfile
```dockerfile
# 会员系统应用镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY ./app ./app
COPY ./docs ./docs
COPY alembic.ini .
COPY ./alembic ./alembic

# 创建非root用户
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose配置

#### 开发环境docker-compose.yml
```yaml
version: '3.8'

services:
  member-system:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENV=development
      - DATABASE_URL=mysql+aiomysql://member_user:member_pass@mysql:3306/member_system
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=dev-secret-key
      - LOG_LEVEL=DEBUG
    volumes:
      - ./app:/app/app
      - ./logs:/app/logs
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: member_system
      MYSQL_USER: member_user
      MYSQL_PASSWORD: member_pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    command: --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: unless-stopped
    
  redis:
    image: redis:7.0-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./config/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      timeout: 10s
      retries: 5
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - member-system
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

## Kubernetes部署配置

### 1. 命名空间和配置

#### namespace.yaml
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: member-system
  labels:
    name: member-system
```

#### configmap.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: member-system-config
  namespace: member-system
data:
  ENV: "production"
  LOG_LEVEL: "INFO"
  DATABASE_HOST: "mysql-service"
  DATABASE_PORT: "3306"
  DATABASE_NAME: "member_system"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  API_PREFIX: "/api/v1"
  CACHE_TTL: "300"
  
---
apiVersion: v1
kind: Secret
metadata:
  name: member-system-secrets
  namespace: member-system
type: Opaque
stringData:
  DATABASE_USER: "member_user"
  DATABASE_PASSWORD: "secure_password"
  JWT_SECRET_KEY: "production-jwt-secret-key"
  REDIS_PASSWORD: "redis_password"
  ENCRYPTION_KEY: "encryption-secret-key"
```

### 2. 数据库部署

#### mysql-deployment.yaml
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-master
  namespace: member-system
spec:
  serviceName: mysql-master
  replicas: 1
  selector:
    matchLabels:
      app: mysql-master
  template:
    metadata:
      labels:
        app: mysql-master
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: DATABASE_PASSWORD
        - name: MYSQL_DATABASE
          value: "member_system"
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: DATABASE_USER
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: DATABASE_PASSWORD
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
        livenessProbe:
          exec:
            command:
            - mysqladmin
            - ping
            - -h
            - localhost
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - mysqladmin
            - ping
            - -h
            - localhost
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: mysql-config
        configMap:
          name: mysql-config
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 200Gi
      storageClassName: fast-ssd

---
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
  namespace: member-system
spec:
  selector:
    app: mysql-master
  ports:
  - port: 3306
    targetPort: 3306
  type: ClusterIP
```

### 3. Redis集群部署

#### redis-cluster.yaml
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
  namespace: member-system
spec:
  serviceName: redis-cluster
  replicas: 3
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
      - name: redis
        image: redis:7.0-alpine
        command:
        - redis-server
        - /etc/redis/redis.conf
        ports:
        - containerPort: 6379
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: REDIS_PASSWORD
        volumeMounts:
        - name: redis-config
          mountPath: /etc/redis
        - name: redis-data
          mountPath: /data
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi

---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: member-system
spec:
  selector:
    app: redis-cluster
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```

### 4. 应用部署

#### member-system-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: member-system
  namespace: member-system
  labels:
    app: member-system
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: member-system
  template:
    metadata:
      labels:
        app: member-system
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: member-system
        image: member-system:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: member-system-config
        env:
        - name: DATABASE_URL
          value: "mysql+aiomysql://$(DATABASE_USER):$(DATABASE_PASSWORD)@$(DATABASE_HOST):$(DATABASE_PORT)/$(DATABASE_NAME)"
        - name: REDIS_URL
          value: "redis://:$(REDIS_PASSWORD)@$(REDIS_HOST):$(REDIS_PORT)/0"
        - name: DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: DATABASE_USER
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: DATABASE_PASSWORD
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: JWT_SECRET_KEY
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: REDIS_PASSWORD
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
      initContainers:
      - name: migrate-db
        image: member-system:latest
        command: ["alembic", "upgrade", "head"]
        envFrom:
        - configMapRef:
            name: member-system-config
        env:
        - name: DATABASE_URL
          value: "mysql+aiomysql://$(DATABASE_USER):$(DATABASE_PASSWORD)@$(DATABASE_HOST):$(DATABASE_PORT)/$(DATABASE_NAME)"
        - name: DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: DATABASE_USER
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: member-system-secrets
              key: DATABASE_PASSWORD

---
apiVersion: v1
kind: Service
metadata:
  name: member-system-service
  namespace: member-system
  labels:
    app: member-system
spec:
  selector:
    app: member-system
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: member-system-ingress
  namespace: member-system
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: member-system-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /api/v1/member-system
        pathType: Prefix
        backend:
          service:
            name: member-system-service
            port:
              number: 80
```

### 5. 水平自动扩缩容

#### hpa.yaml
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: member-system-hpa
  namespace: member-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: member-system
  minReplicas: 3
  maxReplicas: 10
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
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
```

## 监控和日志

### 1. Prometheus监控配置

#### prometheus-config.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "/etc/prometheus/rules/*.yml"
    
    scrape_configs:
    - job_name: 'member-system'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - member-system
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
        
    alerting:
      alertmanagers:
      - static_configs:
        - targets:
          - alertmanager:9093

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: monitoring
data:
  member-system.yml: |
    groups:
    - name: member-system-alerts
      rules:
      - alert: MemberSystemDown
        expr: up{job="member-system"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "会员系统服务不可用"
          description: "会员系统 {{ $labels.instance }} 已经停机超过1分钟"
          
      - alert: MemberSystemHighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="member-system"}[5m])) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "会员系统响应延迟过高"
          description: "会员系统95%请求延迟超过500ms"
          
      - alert: MemberSystemHighErrorRate
        expr: rate(http_requests_total{job="member-system",status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "会员系统错误率过高"
          description: "会员系统5xx错误率超过10%"
```

### 2. Grafana仪表盘配置

#### member-system-dashboard.json
```json
{
  "dashboard": {
    "title": "会员系统监控仪表盘",
    "panels": [
      {
        "title": "请求量(QPS)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{job=\"member-system\"}[5m]))",
            "legendFormat": "QPS"
          }
        ]
      },
      {
        "title": "响应时间",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{job=\"member-system\"}[5m]))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=\"member-system\"}[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{job=\"member-system\"}[5m]))",
            "legendFormat": "P99"
          }
        ]
      },
      {
        "title": "错误率",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{job=\"member-system\",status=~\"4..|5..\"}[5m])) / sum(rate(http_requests_total{job=\"member-system\"}[5m])) * 100",
            "legendFormat": "错误率(%)"
          }
        ]
      },
      {
        "title": "资源使用率",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{pod=~\"member-system-.*\"}[5m]) * 100",
            "legendFormat": "CPU使用率(%)"
          },
          {
            "expr": "container_memory_usage_bytes{pod=~\"member-system-.*\"} / container_spec_memory_limit_bytes{pod=~\"member-system-.*\"} * 100",
            "legendFormat": "内存使用率(%)"
          }
        ]
      }
    ]
  }
}
```

## 部署脚本

### 1. 自动化部署脚本

#### deploy.sh
```bash
#!/bin/bash

# 会员系统自动化部署脚本
set -e

# 配置变量
NAMESPACE="member-system"
IMAGE_TAG="${1:-latest}"
DOCKER_REGISTRY="your-registry.com"
APP_NAME="member-system"

echo "开始部署会员系统 - 版本: ${IMAGE_TAG}"

# 1. 构建Docker镜像
echo "1. 构建Docker镜像..."
docker build -t ${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG} .
docker push ${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG}

# 2. 创建命名空间
echo "2. 创建Kubernetes命名空间..."
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# 3. 应用配置文件
echo "3. 应用配置文件..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml

# 4. 部署数据库
echo "4. 部署MySQL数据库..."
kubectl apply -f k8s/mysql-deployment.yaml
kubectl wait --for=condition=Ready pod -l app=mysql-master -n ${NAMESPACE} --timeout=300s

# 5. 部署Redis
echo "5. 部署Redis集群..."
kubectl apply -f k8s/redis-cluster.yaml
kubectl wait --for=condition=Ready pod -l app=redis-cluster -n ${NAMESPACE} --timeout=300s

# 6. 数据库初始化
echo "6. 执行数据库迁移..."
kubectl run db-migrate --rm -i --restart=Never \
  --image=${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG} \
  --namespace=${NAMESPACE} \
  --env="DATABASE_URL=mysql+aiomysql://member_user:secure_password@mysql-service:3306/member_system" \
  -- alembic upgrade head

# 7. 部署应用
echo "7. 部署会员系统应用..."
sed "s|image: member-system:latest|image: ${DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG}|g" k8s/member-system-deployment.yaml | kubectl apply -f -

# 8. 等待部署完成
echo "8. 等待应用启动..."
kubectl wait --for=condition=Available deployment/${APP_NAME} -n ${NAMESPACE} --timeout=300s

# 9. 部署HPA
echo "9. 配置自动扩缩容..."
kubectl apply -f k8s/hpa.yaml

# 10. 验证部署
echo "10. 验证部署状态..."
kubectl get pods -n ${NAMESPACE}
kubectl get svc -n ${NAMESPACE}

# 11. 健康检查
echo "11. 执行健康检查..."
HEALTH_URL=$(kubectl get ingress member-system-ingress -n ${NAMESPACE} -o jsonpath='{.spec.rules[0].host}')/api/v1/member-system/health
curl -f "https://${HEALTH_URL}" || exit 1

echo "会员系统部署完成！"
echo "访问地址: https://${HEALTH_URL%/health}"
```

### 2. 回滚脚本

#### rollback.sh
```bash
#!/bin/bash

# 会员系统回滚脚本
set -e

NAMESPACE="member-system"
DEPLOYMENT="member-system"

echo "开始回滚会员系统..."

# 1. 查看部署历史
echo "1. 查看部署历史:"
kubectl rollout history deployment/${DEPLOYMENT} -n ${NAMESPACE}

# 2. 回滚到上一个版本
echo "2. 回滚到上一个版本..."
kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE}

# 3. 等待回滚完成
echo "3. 等待回滚完成..."
kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE} --timeout=300s

# 4. 验证回滚结果
echo "4. 验证回滚结果..."
kubectl get pods -n ${NAMESPACE}

# 5. 健康检查
echo "5. 执行健康检查..."
sleep 30
HEALTH_URL=$(kubectl get ingress member-system-ingress -n ${NAMESPACE} -o jsonpath='{.spec.rules[0].host}')/api/v1/member-system/health
curl -f "https://${HEALTH_URL}" || exit 1

echo "会员系统回滚完成！"
```

## 数据库管理

### 1. 数据库初始化脚本

#### init-db.sql
```sql
-- 会员系统数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS member_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER IF NOT EXISTS 'member_user'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON member_system.* TO 'member_user'@'%';

-- 创建只读用户
CREATE USER IF NOT EXISTS 'member_readonly'@'%' IDENTIFIED BY 'readonly_password';
GRANT SELECT ON member_system.* TO 'member_readonly'@'%';

FLUSH PRIVILEGES;

USE member_system;

-- 创建性能优化配置
SET GLOBAL innodb_buffer_pool_size = 1073741824;  -- 1GB
SET GLOBAL innodb_log_file_size = 268435456;      -- 256MB
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 67108864;           -- 64MB
```

### 2. 备份脚本

#### backup.sh
```bash
#!/bin/bash

# 会员系统数据库备份脚本
set -e

BACKUP_DIR="/backup/member-system"
DATE=$(date +%Y%m%d_%H%M%S)
DB_HOST="mysql-service.member-system.svc.cluster.local"
DB_NAME="member_system"
DB_USER="member_user"
DB_PASS="secure_password"

mkdir -p ${BACKUP_DIR}

echo "开始备份会员系统数据库..."

# 1. 全量备份
echo "1. 执行全量备份..."
mysqldump -h ${DB_HOST} -u ${DB_USER} -p${DB_PASS} \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  --hex-blob \
  ${DB_NAME} | gzip > ${BACKUP_DIR}/full_backup_${DATE}.sql.gz

# 2. 备份到云存储
echo "2. 上传备份到云存储..."
aws s3 cp ${BACKUP_DIR}/full_backup_${DATE}.sql.gz \
  s3://your-backup-bucket/member-system/

# 3. 清理旧备份(保留30天)
echo "3. 清理旧备份文件..."
find ${BACKUP_DIR} -name "full_backup_*.sql.gz" -mtime +30 -delete

echo "备份完成: full_backup_${DATE}.sql.gz"
```

## 安全配置

### 1. 网络策略

#### network-policy.yaml
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: member-system-netpol
  namespace: member-system
spec:
  podSelector:
    matchLabels:
      app: member-system
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mysql-master
    ports:
    - protocol: TCP
      port: 3306
  - to:
    - podSelector:
        matchLabels:
          app: redis-cluster
    ports:
    - protocol: TCP
      port: 6379
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

### 2. Pod安全策略

#### pod-security-policy.yaml
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: member-system-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: member-system-psp-use
rules:
- apiGroups: ['policy']
  resources: ['podsecuritypolicies']
  verbs: ['use']
  resourceNames:
  - member-system-psp

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: member-system-psp-use
roleRef:
  kind: ClusterRole
  name: member-system-psp-use
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: ServiceAccount
  name: default
  namespace: member-system
```

## 运维手册

### 1. 常用运维命令

```bash
# 查看服务状态
kubectl get pods -n member-system
kubectl get svc -n member-system
kubectl get ingress -n member-system

# 查看日志
kubectl logs -f deployment/member-system -n member-system
kubectl logs -f -l app=member-system -n member-system --tail=100

# 扩容缩容
kubectl scale deployment member-system --replicas=5 -n member-system

# 重启服务
kubectl rollout restart deployment/member-system -n member-system

# 进入容器调试
kubectl exec -it deployment/member-system -n member-system -- /bin/bash

# 端口转发调试
kubectl port-forward service/member-system-service 8000:80 -n member-system

# 查看资源使用
kubectl top pods -n member-system
kubectl top nodes

# 查看事件
kubectl get events -n member-system --sort-by=.metadata.creationTimestamp
```

### 2. 故障排查指南

#### 常见问题及解决方案

| 问题症状 | 可能原因 | 排查步骤 | 解决方案 |
|----------|----------|----------|----------|
| Pod启动失败 | 镜像拉取失败 | `kubectl describe pod` | 检查镜像地址和权限 |
| 服务连接失败 | 网络策略限制 | 检查NetworkPolicy | 调整网络策略规则 |
| 数据库连接失败 | 密码错误 | 检查Secret配置 | 更新数据库密码 |
| 内存溢出 | 资源限制过小 | 查看资源使用情况 | 调整资源限制 |
| 响应缓慢 | 数据库性能问题 | 检查数据库慢查询 | 优化SQL或增加索引 |

### 3. 应急响应流程

#### 紧急故障处理
1. **故障发现**: 监控告警或用户反馈
2. **快速评估**: 确定影响范围和严重程度
3. **应急处理**: 
   - P0故障: 立即回滚到上一个稳定版本
   - P1故障: 热修复或临时禁用功能
4. **根因分析**: 分析日志和监控数据
5. **永久修复**: 开发修复方案并测试
6. **复盘总结**: 更新运维文档和应急预案

这份部署指南提供了会员系统从开发到生产的完整部署方案，确保系统的高可用性、可扩展性和安全性。