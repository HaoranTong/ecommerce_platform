# 生产环境配置指南

## 文档说明
- **内容**：生产环境部署、环境变量配置、安全配置、性能优化、监控告警
- **使用者**：运维人员、系统管理员、DevOps工程师
- **更新频率**：生产环境变更时更新
- **关联文档**：[部署指南](deployment.md)、[监控告警](monitoring.md)、[运维手册](runbook.md)

**[CHECK:DOC-004]** 生产环境配置必须经过安全审计

---

## 🏭 生产环境架构

### 基础设施架构
```
[CDN/CloudFlare] 
        ↓
[负载均衡器 ALB] 
        ↓
[Web服务器集群 (Nginx)]
        ↓
[应用服务器集群 (6台)]
        ↓  
[数据库集群 (MySQL主从)]
        ↓
[缓存集群 (Redis)]
        ↓
[文件存储 (S3/OSS)]
```

### 网络架构
```
公网 → WAF → ALB → 公有子网(Web层) 
                  ↓
              私有子网(应用层) 
                  ↓
              私有子网(数据层)
```

**[CHECK:ARCH-001]** 生产架构必须实现多层安全隔离

---

## � 生产环境变量配置

### 环境变量分类

#### 应用基础配置
```bash
# 生产环境标识
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# 应用信息
PROJECT_NAME=电商平台
VERSION=1.0.0
API_V1_STR=/api/v1

# 服务端口
PORT=8000
HOST=0.0.0.0
```

#### 数据库配置
```bash
# 生产数据库（从环境变量获取敏感信息）
DATABASE_URL=mysql+pymysql://${PROD_DB_USER}:${PROD_DB_PASSWORD}@${PROD_DB_HOST}:3306/${PROD_DB_NAME}

# 连接池配置
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_MAX_OVERFLOW=30
```

#### 缓存配置
```bash
# 生产Redis
REDIS_URL=redis://:${PROD_REDIS_PASSWORD}@${PROD_REDIS_HOST}:6379/0

# Redis连接池
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
```

#### 安全配置
```bash
# 生产JWT配置（高安全性）
JWT_SECRET_KEY=${PROD_JWT_SECRET}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120  # 2小时

# SSL配置
SSL_CERT_PATH=/etc/ssl/certs/production.crt
SSL_KEY_PATH=/etc/ssl/private/production.key

# 安全策略
CORS_ORIGINS=${PROD_CORS_ORIGINS}
ALLOWED_HOSTS=${PROD_ALLOWED_HOSTS}
```

#### 第三方服务配置
```bash
# 监控配置
SENTRY_DSN=${PROD_SENTRY_DSN}
NEW_RELIC_LICENSE_KEY=${PROD_NEW_RELIC_KEY}
PROMETHEUS_METRICS_PORT=9090

# 生产支付服务
ALIPAY_APP_ID=${PROD_ALIPAY_APP_ID}
ALIPAY_PRIVATE_KEY_PATH=/etc/ssl/keys/alipay_private.pem
WECHAT_APP_ID=${PROD_WECHAT_APP_ID}
WECHAT_SECRET=${PROD_WECHAT_SECRET}

# 生产文件存储
UPLOAD_STORAGE=s3
S3_BUCKET=${PROD_S3_BUCKET}
S3_REGION=${PROD_S3_REGION}
CDN_URL=${PROD_CDN_URL}
```

#### 性能配置
```bash
# 应用服务器配置
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
WORKER_CLASS=uvicorn.workers.UvicornWorker

# 资源限制
MAX_UPLOAD_SIZE=100MB
REQUEST_TIMEOUT=60
```

**[CHECK:DOC-001]** 生产环境变量必须通过外部密钥管理系统注入

---

## �🐳 容器化生产部署

### 生产Docker配置
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: ${REGISTRY_URL}/ecommerce-app:${VERSION}
    deploy:
      replicas: 6
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 10s
        max_attempts: 3
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${PROD_DATABASE_URL}
      - REDIS_URL=${PROD_REDIS_URL}
      - JWT_SECRET_KEY=${PROD_JWT_SECRET}
      - LOG_LEVEL=WARNING
    secrets:
      - db_password
      - jwt_secret
      - redis_password
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80" 
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/ssl/certs:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - app
    networks:
      - app-network
    deploy:
      replicas: 2
      
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - app-network
    deploy:
      replicas: 1
      
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/my.cnf:/etc/mysql/my.cnf:ro
    secrets:
      - db_password
      - db_root_password
    networks:
      - db-network
    deploy:
      replicas: 1

secrets:
  db_password:
    external: true
  db_root_password:
    external: true
  jwt_secret:
    external: true
  redis_password:
    external: true

networks:
  app-network:
    driver: overlay
    encrypted: true
  db-network:
    driver: overlay
    encrypted: true

volumes:
  mysql_data:
    driver: local
  redis_data:
    driver: local
  nginx_logs:
    driver: local
```

### 生产Dockerfile
```dockerfile
# Dockerfile.prod
# 多阶段构建 - 构建阶段
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装依赖
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# 运行阶段
FROM python:3.11-slim

# 创建非root用户
RUN groupadd --gid 1001 appuser \
    && useradd --uid 1001 --gid appuser --shell /bin/bash --create-home appuser

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# 从构建阶段复制wheels
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# 安装Python包
RUN pip install --no-cache /wheels/*

# 复制应用代码
COPY --chown=appuser:appuser . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令（生产模式）
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
```

---

## ☸️ Kubernetes生产部署

### Namespace和资源配额
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce-prod
  labels:
    name: ecommerce-prod
    environment: production

---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: ecommerce-prod
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "10"
```

### ConfigMap和Secret
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: ecommerce-prod
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "WARNING"
  API_V1_STR: "/api/v1"
  PROJECT_NAME: "电商平台"
  VERSION: "1.0.0"
  GUNICORN_WORKERS: "4"
  GUNICORN_TIMEOUT: "120"

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: ecommerce-prod
type: Opaque
stringData:
  DATABASE_URL: "mysql+pymysql://user:password@mysql:3306/ecommerce"
  REDIS_URL: "redis://redis:6379/0"
  JWT_SECRET_KEY: "your-production-secret-key"
  REDIS_PASSWORD: "your-redis-password"
```

### 生产Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-app
  namespace: ecommerce-prod
  labels:
    app: ecommerce-app
    version: v1.0.0
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  selector:
    matchLabels:
      app: ecommerce-app
  template:
    metadata:
      labels:
        app: ecommerce-app
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: ecommerce-service-account
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
      - name: app
        image: registry.example.com/ecommerce-app:v1.0.0
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: REDIS_URL
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /api/health
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp-volume
          mountPath: /tmp
        - name: logs-volume  
          mountPath: /var/log/app
      volumes:
      - name: tmp-volume
        emptyDir: {}
      - name: logs-volume
        emptyDir: {}
      imagePullSecrets:
      - name: registry-secret
```

### HPA自动扩缩容
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ecommerce-app-hpa
  namespace: ecommerce-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ecommerce-app
  minReplicas: 6
  maxReplicas: 20
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
```

**[CHECK:DOC-004]** K8s生产配置必须包含资源限制和安全策略

---

## 🔒 安全配置

### SSL/TLS配置
```nginx
# nginx/prod.conf
# SSL配置
ssl_certificate /etc/ssl/certs/ecommerce.crt;
ssl_certificate_key /etc/ssl/private/ecommerce.key;

# SSL安全配置
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# 其他安全头
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;" always;

# 隐藏服务器版本
server_tokens off;
```

### 网络安全策略
```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ecommerce-network-policy
  namespace: ecommerce-prod
spec:
  podSelector:
    matchLabels:
      app: ecommerce-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # 仅允许来自Ingress Controller的流量
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  # 仅允许访问数据库和Redis
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
  # 允许DNS查询
  - to: []
    ports:
    - protocol: UDP
      port: 53
```

### Pod安全策略
```yaml
# k8s/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: ecommerce-psp
  namespace: ecommerce-prod
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
  supplementalGroups:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
```

---

## 🗄️ 数据库生产配置

### MySQL生产配置
```ini
# mysql/my.cnf
[mysqld]
# 基础配置
port = 3306
bind-address = 0.0.0.0
default_authentication_plugin = mysql_native_password

# InnoDB配置
innodb_buffer_pool_size = 2G
innodb_log_file_size = 512M
innodb_log_buffer_size = 16M
innodb_flush_log_at_trx_commit = 2
innodb_file_per_table = 1

# 连接配置
max_connections = 200
max_connect_errors = 1000000
wait_timeout = 600
interactive_timeout = 600

# 查询缓存
query_cache_type = 1
query_cache_size = 128M
query_cache_limit = 1M

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 2

# 二进制日志
log-bin = mysql-bin
binlog_format = ROW
expire_logs_days = 7
max_binlog_size = 100M

# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4

[client]
default-character-set = utf8mb4
```

### Redis生产配置
```conf
# redis/redis.conf
# 网络配置
bind 0.0.0.0
port 6379
protected-mode yes

# 内存配置
maxmemory 2gb
maxmemory-policy allkeys-lru

# 持久化配置
save 900 1
save 300 10
save 60 10000
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb

# AOF配置
appendonly yes
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# 安全配置
requirepass your_redis_password

# 客户端配置
maxclients 10000
timeout 300
tcp-keepalive 300

# 日志配置
loglevel notice
logfile /var/log/redis/redis-server.log
```

---

## 📊 性能优化配置

### 应用性能配置
```python
# app/core/config.py - 生产配置
class ProductionConfig:
    # 数据库连接池
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 20,
        "pool_timeout": 30,
        "pool_recycle": 3600,
        "max_overflow": 30,
        "pool_pre_ping": True,
        "echo": False
    }
    
    # Redis配置
    REDIS_CONFIG = {
        "connection_pool_kwargs": {
            "max_connections": 50,
            "retry_on_timeout": True,
            "socket_timeout": 5,
            "socket_connect_timeout": 5
        }
    }
    
    # 日志配置
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "file": {
                "level": "WARNING", 
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "/var/log/app/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "root": {
            "level": "WARNING",
            "handlers": ["file"]
        }
    }
```

### Nginx性能优化
```nginx
# nginx/prod.conf
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # 基础优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 缓存配置
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
    
    # 限流配置
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    upstream app_backend {
        least_conn;
        server app1:8000 max_fails=3 fail_timeout=30s;
        server app2:8000 max_fails=3 fail_timeout=30s;
        server app3:8000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }
    
    server {
        listen 443 ssl http2;
        server_name api.ecommerce.com;
        
        # 限流
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://app_backend;
        }
        
        location /api/auth/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://app_backend;
        }
        
        # 静态文件缓存
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

**[CHECK:DOC-004]** 性能配置必须经过压力测试验证

---

## 🔍 监控和日志配置

### 生产环境变量
```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# 数据库配置（从环境变量或密钥管理系统获取）
DATABASE_URL=mysql+pymysql://${PROD_DB_USER}:${PROD_DB_PASSWORD}@${PROD_DB_HOST}:3306/${PROD_DB_NAME}

# Redis配置
REDIS_URL=redis://:{PROD_REDIS_PASSWORD}@${PROD_REDIS_HOST}:6379/0

# JWT配置（高安全性）
JWT_SECRET_KEY=${PROD_JWT_SECRET}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# SSL配置
SSL_CERT_PATH=/etc/ssl/certs/production.crt
SSL_KEY_PATH=/etc/ssl/private/production.key

# 安全配置
CORS_ORIGINS=${PROD_CORS_ORIGINS}
ALLOWED_HOSTS=${PROD_ALLOWED_HOSTS}

# 监控配置
SENTRY_DSN=${PROD_SENTRY_DSN}
NEW_RELIC_LICENSE_KEY=${PROD_NEW_RELIC_KEY}
PROMETHEUS_METRICS_PORT=9090

# 第三方服务（生产）
ALIPAY_APP_ID=${PROD_ALIPAY_APP_ID}
ALIPAY_PRIVATE_KEY_PATH=/etc/ssl/keys/alipay_private.pem
WECHAT_APP_ID=${PROD_WECHAT_APP_ID}

# 文件存储
UPLOAD_STORAGE=s3
S3_BUCKET=${PROD_S3_BUCKET}
S3_REGION=${PROD_S3_REGION}
CDN_URL=${PROD_CDN_URL}
```

### 日志聚合配置
```yaml
# 日志收集配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: ecommerce-prod
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/ecommerce-app*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      format json
    </source>
    
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      index_name ecommerce-logs
      type_name _doc
    </match>
```

---

## 🚀 部署和发布策略

### 蓝绿部署脚本
```bash
#!/bin/bash
# scripts/blue_green_deploy.sh
set -e

NAMESPACE="ecommerce-prod"
NEW_VERSION=$1
CURRENT_COLOR=$(kubectl get service ecommerce-app-service -n $NAMESPACE -o jsonpath='{.spec.selector.color}')

if [[ "$CURRENT_COLOR" == "blue" ]]; then
    NEW_COLOR="green"
else
    NEW_COLOR="blue"
fi

echo "执行蓝绿部署: $CURRENT_COLOR -> $NEW_COLOR (版本: $NEW_VERSION)"

# 部署新版本
kubectl set image deployment/ecommerce-app-$NEW_COLOR app=registry.example.com/ecommerce-app:$NEW_VERSION -n $NAMESPACE

# 等待新版本就绪
kubectl rollout status deployment/ecommerce-app-$NEW_COLOR -n $NAMESPACE --timeout=600s

# 运行健康检查
echo "执行健康检查..."
for i in {1..5}; do
    if curl -f "http://ecommerce-app-$NEW_COLOR:8000/api/health"; then
        echo "健康检查通过"
        break
    fi
    sleep 10
done

# 切换流量
kubectl patch service ecommerce-app-service -n $NAMESPACE -p '{"spec":{"selector":{"color":"'$NEW_COLOR'"}}}'

# 验证新版本
sleep 30
if curl -f "https://api.ecommerce.com/api/health"; then
    echo "✅ 蓝绿部署成功完成"
    
    # 清理旧版本
    kubectl scale deployment ecommerce-app-$CURRENT_COLOR --replicas=0 -n $NAMESPACE
else
    echo "❌ 部署验证失败，回滚..."
    kubectl patch service ecommerce-app-service -n $NAMESPACE -p '{"spec":{"selector":{"color":"'$CURRENT_COLOR'"}}}'
    exit 1
fi
```

### 滚动更新配置
```yaml
# 滚动更新策略
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%        # 最多可以超出副本数的25%
      maxUnavailable: 25%  # 最多可以有25%的副本不可用
  progressDeadlineSeconds: 600  # 部署超时时间
  revisionHistoryLimit: 10      # 保留的历史版本数
```

---

## 📋 生产环境检查清单

### 部署前检查清单
- [ ] **安全配置**: SSL证书、密钥管理、网络策略已配置
- [ ] **资源配置**: CPU、内存、存储资源配额已设置  
- [ ] **高可用配置**: 多副本、负载均衡、故障转移已配置
- [ ] **监控告警**: 监控指标、告警规则、通知渠道已配置
- [ ] **备份策略**: 数据备份、备份验证流程已建立
- [ ] **日志收集**: 日志聚合、日志轮转配置已完成
- [ ] **性能优化**: 缓存策略、连接池、索引优化已实施
- [ ] **安全扫描**: 漏洞扫描、依赖检查已通过

### 运行时检查清单
- [ ] **服务健康**: 所有服务健康检查正常
- [ ] **性能指标**: 响应时间、错误率在正常范围
- [ ] **资源使用**: CPU、内存、磁盘使用率正常
- [ ] **网络连接**: 数据库、缓存连接正常
- [ ] **外部依赖**: 第三方服务连接正常
- [ ] **数据一致性**: 数据库主从同步正常
- [ ] **缓存状态**: Redis缓存命中率正常
- [ ] **日志输出**: 应用日志输出正常，无错误堆积

**[CHECK:DOC-004]** 生产环境检查清单必须严格执行

---

## 🆘 应急处理

### 生产故障快速响应
```bash
#!/bin/bash
# 生产环境应急脚本
NAMESPACE="ecommerce-prod"

case $1 in
    "rollback")
        echo "执行应急回滚..."
        kubectl rollout undo deployment/ecommerce-app -n $NAMESPACE
        kubectl rollout status deployment/ecommerce-app -n $NAMESPACE
        ;;
    "scale-up")
        echo "紧急扩容..."
        kubectl scale deployment ecommerce-app --replicas=12 -n $NAMESPACE
        ;;
    "restart")
        echo "重启服务..."
        kubectl rollout restart deployment/ecommerce-app -n $NAMESPACE
        ;;
    "status")
        echo "检查服务状态..."
        kubectl get pods -n $NAMESPACE
        kubectl get svc -n $NAMESPACE
        kubectl top pods -n $NAMESPACE
        ;;
esac
```

### 数据库应急处理
```bash
#!/bin/bash
# 数据库应急处理脚本

# 主从切换
switch_mysql_master() {
    echo "执行MySQL主从切换..."
    
    # 停止从库复制
    mysql -h slave-host -e "STOP SLAVE;"
    
    # 更新应用配置指向新主库
    kubectl patch configmap app-config -n ecommerce-prod -p '{"data":{"DATABASE_URL":"mysql://new-master:3306/ecommerce"}}'
    
    # 重启应用
    kubectl rollout restart deployment/ecommerce-app -n ecommerce-prod
}
```

---

## 相关文档
- [部署指南](deployment.md) - 详细部署流程和策略
- [监控告警](monitoring.md) - 生产环境监控配置
- [故障排除](troubleshooting.md) - 生产故障处理流程
- [环境变量管理](environment-variables.md) - 生产环境变量管理
