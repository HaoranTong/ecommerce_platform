# 部署实现设计

## 文档概述
**承接架构层**: [infrastructure-architecture.md](../../architecture/infrastructure-architecture.md) - 基础设施架构策略  
**设计职责**: 具体部署配置、容器编排、运维脚本  
**边界约束**: 部署技术实现，不涉及架构决策  

## Kubernetes部署配置

### 应用部署配置
```yaml
# 命名空间配置
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce-platform
  labels:
    environment: production

---
# 应用部署配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-web
  namespace: ecommerce-platform
  labels:
    app: ecommerce-web
    version: v1.0.0
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
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: redis-url
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
```

### 服务和负载均衡配置
```yaml
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

---
# Ingress配置
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
  namespace: ecommerce-platform
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.ecommerce-platform.com
    secretName: ecommerce-tls
  rules:
  - host: api.ecommerce-platform.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ecommerce-web-service
            port:
              number: 80
```

### 自动扩缩容配置
```yaml
# HPA配置
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
- [安全设计方案](./security-design.md)
- [性能设计方案](./performance-design.md)
