# 部署运维指南

## 文档说明
- **内容**：系统部署流程、环境配置、发布策略、回滚方案
- **使用者**：运维团队、部署管理员、项目负责人
- **更新频率**：部署流程变更时更新
- **关联文档**：[监控告警](monitoring.md)、[故障排除](troubleshooting.md)、[运维手册](runbook.md)

**[CHECK:DOC-003]** 部署流程必须确保环境隔离和安全性

---

## 🏗️ 部署架构概览

### 环境分层
```
生产环境 (Production)    ← 正式服务环境
    ↑
预生产环境 (Staging)     ← 生产前验证
    ↑
测试环境 (Testing)       ← 集成测试
    ↑
开发环境 (Development)   ← 本地开发
```

**[CHECK:DOC-003]** 环境分层必须确保逐级部署和验证

### 基础设施架构
```
[负载均衡器 (ALB)] 
        ↓
[Web服务器集群 (3台)]
        ↓
[应用服务器集群 (6台)]
        ↓  
[数据库集群 (MySQL主从)]
        ↓
[缓存集群 (Redis)]
        ↓
[文件存储 (OSS)]
```

**[CHECK:DOC-003]** 基础设施架构必须支持高可用和负载均衡

---

## 🏭 生产环境部署配置

### 基础设施配置
```yaml
# production infrastructure
Load Balancer:
  - Type: Application Load Balancer
  - Health Check: /api/health
  - SSL Termination: Yes
  
Web Servers:
  - Count: 3
  - Instance Type: t3.medium
  - Auto Scaling: Yes (2-6 instances)
  - Health Check: ELB + Custom
  
App Servers:
  - Count: 6
  - Instance Type: t3.large
  - Auto Scaling: Yes (4-12 instances)
  - Container: Docker + ECS
  
Database:
  - Type: MySQL 8.0 RDS
  - Instance: db.r5.xlarge
  - Multi-AZ: Yes
  - Read Replicas: 2
  - Backup: Automated (7 days)
  
Cache:
  - Type: Redis ElastiCache
  - Instance: cache.r6g.large
  - Cluster Mode: Yes
  - Backup: Daily snapshot
  
Storage:
  - Type: S3 + CloudFront CDN
  - Encryption: Server-side
  - Versioning: Enabled
```

**[CHECK:DOC-003]** 生产环境必须确保数据安全和性能优化

---

## 🐳 容器化部署

**[CHECK:DOC-003]** 容器化部署必须确保镜像安全和资源优化

### Docker镜像构建

#### 多阶段构建Dockerfile
```dockerfile
# Dockerfile.prod
# 构建阶段
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装Python依赖
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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 从构建阶段复制wheels
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# 安装Python包
RUN pip install --no-cache /wheels/*

# 复制应用代码
COPY --chown=appuser:appuser . .

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### 镜像构建脚本
```bash
#!/bin/bash
# scripts/build_image.sh

set -e

# 配置变量
IMAGE_NAME="ecommerce-app"
REGISTRY="your-registry.com"
VERSION=${1:-$(git rev-parse --short HEAD)}
ENVIRONMENT=${2:-production}

echo "构建镜像: ${IMAGE_NAME}:${VERSION}"

# 构建镜像
docker build \
    -f Dockerfile.${ENVIRONMENT} \
    -t ${IMAGE_NAME}:${VERSION} \
    -t ${IMAGE_NAME}:latest \
    --build-arg VERSION=${VERSION} \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    .

# 推送到镜像仓库
echo "推送镜像到仓库..."
docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:${VERSION}
docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${IMAGE_NAME}:latest

docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
docker push ${REGISTRY}/${IMAGE_NAME}:latest

echo "镜像构建完成: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
```

---

## ☸️ Kubernetes部署

**[CHECK:DOC-003]** K8s部署必须确保服务高可用和自动扩缩容

### K8s部署配置

#### Namespace和ConfigMap
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce
  labels:
    name: ecommerce
    environment: production

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: ecommerce
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  REDIS_URL: "redis://redis-service:6379/0"
  API_PREFIX: "/api/v1"
```

#### Secret配置
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: ecommerce
type: Opaque
data:
  DATABASE_URL: <base64-encoded-value>
  JWT_SECRET_KEY: <base64-encoded-value>
  REDIS_PASSWORD: <base64-encoded-value>
```

#### Deployment配置
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-app
  namespace: ecommerce
  labels:
    app: ecommerce-app
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
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
    spec:
      containers:
      - name: app
        image: your-registry.com/ecommerce-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        envFrom:
        - configMapRef:
            name: app-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Service和Ingress
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ecommerce-app-service
  namespace: ecommerce
spec:
  selector:
    app: ecommerce-app
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
  namespace: ecommerce
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
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
            name: ecommerce-app-service
            port:
              number: 80
```

---

## 🚀 CI/CD流水线

**[CHECK:DOC-003]** CI/CD流水线必须包含完整的测试和安全检查

### GitHub Actions工作流
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ecommerce-app

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
    - uses: actions/checkout@v3
    
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
          type=sha,prefix={{branch}}-
          
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        file: Dockerfile.prod
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # kubectl commands here
        
  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # kubectl commands here
```

### 部署脚本

**[CHECK:DOC-003]** 部署脚本必须包含完整的验证和错误处理

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}
NAMESPACE="ecommerce"

echo "部署到环境: $ENVIRONMENT"
echo "镜像标签: $IMAGE_TAG"

# 验证环境
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    echo "错误: 无效的环境参数 ($ENVIRONMENT)"
    echo "使用方法: ./deploy.sh [staging|production] [image-tag]"
    exit 1
fi

# 设置kubeconfig
export KUBECONFIG="~/.kube/config-$ENVIRONMENT"

# 检查集群连接
echo "检查Kubernetes集群连接..."
kubectl cluster-info

# 更新镜像
echo "更新应用镜像..."
kubectl set image deployment/ecommerce-app app=ghcr.io/ecommerce-app:$IMAGE_TAG -n $NAMESPACE

# 等待部署完成
echo "等待部署完成..."
kubectl rollout status deployment/ecommerce-app -n $NAMESPACE --timeout=300s

# 验证部署
echo "验证部署状态..."
kubectl get pods -n $NAMESPACE -l app=ecommerce-app

# 运行烟雾测试
echo "运行烟雾测试..."
if [[ "$ENVIRONMENT" == "staging" ]]; then
    API_URL="https://staging-api.ecommerce.com"
else
    API_URL="https://api.ecommerce.com"
fi

# 健康检查
response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/api/health)
if [[ $response == "200" ]]; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败 (HTTP $response)"
    exit 1
fi

echo "🎉 部署成功完成!"
```

---

## 数据库部署和迁移

### 数据库迁移流程
```bash
#!/bin/bash
# scripts/db_migrate.sh

set -e

ENVIRONMENT=${1:-staging}
MIGRATION_TYPE=${2:-upgrade}

echo "数据库迁移: $ENVIRONMENT - $MIGRATION_TYPE"

# 设置数据库连接
case $ENVIRONMENT in
    "development")
        DB_URL="mysql+pymysql://root:devpass@localhost:3307/ecommerce_dev"
        ;;
    "staging")
        DB_URL=$STAGING_DATABASE_URL
        ;;
    "production")
        DB_URL=$PRODUCTION_DATABASE_URL
        ;;
esac

export DATABASE_URL=$DB_URL

# 备份数据库 (生产环境)
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "创建数据库备份..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME > backup_${timestamp}.sql
    echo "备份完成: backup_${timestamp}.sql"
fi

# 执行迁移
case $MIGRATION_TYPE in
    "upgrade")
        echo "执行数据库升级..."
        alembic upgrade head
        ;;
    "downgrade")
        echo "执行数据库降级..."
        read -p "确认降级到版本: " revision
        alembic downgrade $revision
        ;;
    "current")
        echo "当前数据库版本:"
        alembic current
        ;;
    "history")
        echo "迁移历史:"
        alembic history --verbose
        ;;
esac

echo "数据库迁移完成"
```

### 数据库初始化
```python
# scripts/init_db.py
"""数据库初始化脚本"""

import asyncio
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models import Base
from app.core.security import get_password_hash

async def init_database():
    """初始化数据库"""
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建初始数据
    db = SessionLocal()
    try:
        # 检查是否已初始化
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE email = 'admin@ecommerce.com'"))
        if result.scalar() > 0:
            print("数据库已初始化")
            return
            
        # 创建管理员用户
        admin_user = {
            "email": "admin@ecommerce.com",
            "username": "admin",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True,
            "is_superuser": True
        }
        
        db.execute(text("""
            INSERT INTO users (email, username, hashed_password, is_active, is_superuser)
            VALUES (:email, :username, :hashed_password, :is_active, :is_superuser)
        """), admin_user)
        
        # 创建默认分类
        categories = [
            {"name": "电子产品", "description": "电子设备和配件"},
            {"name": "服装", "description": "男女服装"},
            {"name": "家居", "description": "家具和装饰用品"},
        ]
        
        for category in categories:
            db.execute(text("""
                INSERT INTO categories (name, description)
                VALUES (:name, :description)
            """), category)
            
        db.commit()
        print("数据库初始化完成")
        
    except Exception as e:
        db.rollback()
        print(f"数据库初始化失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(init_database())
```

---

## 🎯 发布策略

**[CHECK:DOC-003]** 发布策略必须确保零停机部署和风险控制

### 蓝绿部署
```bash
#!/bin/bash
# scripts/blue_green_deploy.sh

set -e

NAMESPACE="ecommerce"
NEW_VERSION=$1
CURRENT_COLOR=$(kubectl get service ecommerce-app-service -n $NAMESPACE -o jsonpath='{.spec.selector.color}')

# 确定新颜色
if [[ "$CURRENT_COLOR" == "blue" ]]; then
    NEW_COLOR="green"
else
    NEW_COLOR="blue"
fi

echo "当前版本: $CURRENT_COLOR"
echo "新版本: $NEW_COLOR"

# 部署新版本
echo "部署新版本到 $NEW_COLOR 环境..."
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-app-$NEW_COLOR
  namespace: $NAMESPACE
spec:
  replicas: 6
  selector:
    matchLabels:
      app: ecommerce-app
      color: $NEW_COLOR
  template:
    metadata:
      labels:
        app: ecommerce-app
        color: $NEW_COLOR
    spec:
      containers:
      - name: app
        image: ghcr.io/ecommerce-app:$NEW_VERSION
        # ... 其他配置
EOF

# 等待新版本就绪
echo "等待新版本就绪..."
kubectl rollout status deployment/ecommerce-app-$NEW_COLOR -n $NAMESPACE

# 运行健康检查
echo "运行健康检查..."
./scripts/health_check.sh $NEW_COLOR

# 切换流量
echo "切换流量到新版本..."
kubectl patch service ecommerce-app-service -n $NAMESPACE -p '{"spec":{"selector":{"color":"'$NEW_COLOR'"}}}'

# 验证新版本
echo "验证新版本..."
sleep 30
./scripts/health_check.sh production

# 清理旧版本
echo "清理旧版本..."
kubectl delete deployment ecommerce-app-$CURRENT_COLOR -n $NAMESPACE

echo "蓝绿部署完成!"
```

### 金丝雀发布
```bash
#!/bin/bash
# scripts/canary_deploy.sh

set -e

NAMESPACE="ecommerce"
NEW_VERSION=$1
CANARY_PERCENTAGE=${2:-10}

echo "开始金丝雀发布: $NEW_VERSION (流量比例: $CANARY_PERCENTAGE%)"

# 创建金丝雀部署
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-app-canary
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ecommerce-app
      version: canary
  template:
    metadata:
      labels:
        app: ecommerce-app
        version: canary
    spec:
      containers:
      - name: app
        image: ghcr.io/ecommerce-app:$NEW_VERSION
EOF

# 等待金丝雀版本就绪
kubectl rollout status deployment/ecommerce-app-canary -n $NAMESPACE

# 配置流量分割 (使用Istio)
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: ecommerce-app
  namespace: $NAMESPACE
spec:
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: ecommerce-app-service
        subset: canary
  - route:
    - destination:
        host: ecommerce-app-service
        subset: stable
      weight: $((100-CANARY_PERCENTAGE))
    - destination:
        host: ecommerce-app-service
        subset: canary
      weight: $CANARY_PERCENTAGE
EOF

echo "金丝雀发布完成，流量分割已配置"
echo "监控指标并逐步增加流量比例"
```

---

## 🔄 回滚策略

**[CHECK:DOC-003]** 回滚策略必须确保快速恢复和数据一致性

### 快速回滚脚本
```bash
#!/bin/bash
# scripts/rollback.sh

set -e

ENVIRONMENT=${1:-production}
NAMESPACE="ecommerce"

echo "开始回滚操作: $ENVIRONMENT"

# 获取部署历史
echo "部署历史:"
kubectl rollout history deployment/ecommerce-app -n $NAMESPACE

# 获取上一个版本
PREVIOUS_REVISION=$(kubectl rollout history deployment/ecommerce-app -n $NAMESPACE | tail -2 | head -1 | awk '{print $1}')

echo "回滚到版本: $PREVIOUS_REVISION"

# 确认回滚
read -p "确认回滚到版本 $PREVIOUS_REVISION? (yes/no): " confirm
if [[ $confirm != "yes" ]]; then
    echo "回滚操作已取消"
    exit 0
fi

# 执行回滚
echo "执行回滚..."
kubectl rollout undo deployment/ecommerce-app -n $NAMESPACE --to-revision=$PREVIOUS_REVISION

# 等待回滚完成
echo "等待回滚完成..."
kubectl rollout status deployment/ecommerce-app -n $NAMESPACE

# 验证回滚
echo "验证回滚状态..."
./scripts/health_check.sh $ENVIRONMENT

echo "回滚完成!"
```

### 数据库回滚
```bash
#!/bin/bash
# scripts/db_rollback.sh

set -e

ENVIRONMENT=$1
BACKUP_FILE=$2

if [[ -z "$BACKUP_FILE" ]]; then
    echo "错误: 请指定备份文件"
    echo "使用方法: ./db_rollback.sh [environment] [backup_file]"
    exit 1
fi

echo "数据库回滚: $ENVIRONMENT"
echo "备份文件: $BACKUP_FILE"

# 确认操作
read -p "警告: 这将覆盖现有数据。确认继续? (yes/no): " confirm
if [[ $confirm != "yes" ]]; then
    echo "回滚操作已取消"
    exit 0
fi

# 创建当前备份
echo "创建当前数据备份..."
timestamp=$(date +%Y%m%d_%H%M%S)
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME > rollback_backup_${timestamp}.sql

# 恢复数据
echo "恢复数据库..."
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME < $BACKUP_FILE

echo "数据库回滚完成"
```

---

## 安全配置

### SSL/TLS配置
```nginx
# nginx/ssl.conf
server {
    listen 443 ssl http2;
    server_name api.ecommerce.com;

    # SSL配置
    ssl_certificate /etc/ssl/certs/ecommerce.crt;
    ssl_certificate_key /etc/ssl/private/ecommerce.key;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # 代理配置
    location / {
        proxy_pass http://app-backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 网络安全策略
```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ecommerce-network-policy
  namespace: ecommerce
spec:
  podSelector:
    matchLabels:
      app: ecommerce-app
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
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 3306
  - to:
    - namespaceSelector:
        matchLabels:
          name: redis
    ports:
    - protocol: TCP
      port: 6379
```

---

## 📚 相关文档
- [监控告警](monitoring.md) - 系统监控和告警配置
- [故障排除](troubleshooting.md) - 常见问题解决方案  
- [运维手册](runbook.md) - 日常运维操作指南
- [开发环境配置](../development/dev-env-setup.md) - 开发环境详细配置
- [测试环境配置](../../tests/README.md) - 测试环境配置管理
- [生产环境配置](production-env-setup.md) - 生产环境安全配置和环境变量管理
- [MASTER工作流程](../../MASTER.md) - 部署流程检查点

**[CHECK:DOC-003]** 相关文档必须保持最新和准确的交叉引用
