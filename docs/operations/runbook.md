# 日常运维操作手册

## 文档说明
- **内容**：日常运维任务、操作流程、维护计划、运维工具
- **使用者**：运维人员、系统管理员、值班工程师
- **更新频率**：运维流程变更时更新
- **关联文档**：[部署指南](deployment.md)、[监控告警](monitoring.md)、[故障排除](troubleshooting.md)

**[CHECK:DOC-001]** 运维操作必须遵循标准化流程

---

## 📋 日常运维任务清单

### 每日检查任务
```bash
# 每日运维检查脚本
#!/bin/bash
echo "=== 每日运维检查 $(date) ==="

# 1. 系统资源检查
echo "1. 系统资源状况:"
df -h | grep -v tmpfs
free -h
uptime

# 2. 服务状态检查
echo "2. 关键服务状态:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 3. 应用健康检查
echo "3. 应用健康状况:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/metrics

# 4. 数据库状态
echo "4. 数据库连接状况:"
docker exec mysql mysql -u root -p$MYSQL_ROOT_PASSWORD -e "SELECT COUNT(*) as active_connections FROM information_schema.PROCESSLIST;"

# 5. 备份状态检查
echo "5. 备份状态检查:"
ls -la /backup/ | tail -5

echo "=== 检查完成 ==="
```

### 每周维护任务
- [ ] **性能报告生成**：分析系统性能趋势
- [ ] **容量规划评估**：检查资源使用趋势  
- [ ] **安全补丁更新**：系统和依赖包更新
- [ ] **备份验证测试**：验证备份文件完整性
- [ ] **监控规则优化**：调整告警阈值和规则
- [ ] **日志轮转清理**：清理过期日志文件
- [ ] **SSL证书检查**：检查证书有效期

### 每月运维任务
- [ ] **灾备演练**：执行完整的灾难恢复演练
- [ ] **性能优化评估**：数据库和应用性能调优
- [ ] **安全审计**：访问权限和安全配置审查
- [ ] **容量扩容评估**：基于趋势分析制定扩容计划
- [ ] **运维文档更新**：更新操作手册和流程文档

**[CHECK:DOC-003]** 运维任务必须有执行记录和结果验证

---

## 🔄 服务管理操作

### Docker环境管理

#### 服务启动停止
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启特定服务
docker-compose restart app

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f app
docker-compose logs --tail=100 mysql
```

#### 服务扩缩容
```bash
# 扩容应用服务
docker-compose up -d --scale app=3

# 查看扩容结果
docker ps | grep ecommerce-app
```

#### 镜像管理
```bash
# 构建新镜像
docker build -t ecommerce-app:latest .

# 推送镜像到仓库
docker tag ecommerce-app:latest registry.example.com/ecommerce-app:latest
docker push registry.example.com/ecommerce-app:latest

# 清理无用镜像
docker image prune -f
docker system prune -a -f
```

### Kubernetes环境管理

#### Pod管理
```bash
# 查看Pod状态
kubectl get pods -n ecommerce
kubectl describe pod <pod-name> -n ecommerce

# 重启Deployment
kubectl rollout restart deployment/ecommerce-app -n ecommerce

# 扩缩容
kubectl scale deployment ecommerce-app --replicas=5 -n ecommerce

# 查看Pod日志
kubectl logs -f deployment/ecommerce-app -n ecommerce
kubectl logs <pod-name> -n ecommerce --previous
```

#### 配置管理
```bash
# 更新ConfigMap
kubectl create configmap app-config --from-file=config.yaml -n ecommerce -o yaml --dry-run=client | kubectl apply -f -

# 更新Secret
kubectl create secret generic app-secrets --from-literal=JWT_SECRET=newsecret -n ecommerce -o yaml --dry-run=client | kubectl apply -f -

# 查看配置
kubectl get configmap app-config -n ecommerce -o yaml
kubectl get secret app-secrets -n ecommerce -o yaml
```

#### 服务发现和网络
```bash
# 查看Service状态
kubectl get svc -n ecommerce
kubectl describe svc ecommerce-app-service -n ecommerce

# 查看Ingress状态
kubectl get ingress -n ecommerce
kubectl describe ingress ecommerce-ingress -n ecommerce

# 网络连通性测试
kubectl run test-pod --image=busybox -n ecommerce --rm -it -- sh
# 在test-pod中执行: wget -qO- http://ecommerce-app-service:8000/api/health
```

**[CHECK:DOC-002]** 服务变更操作必须记录在运维日志中

---

## 💾 备份和恢复操作

### 数据库备份

#### 自动化备份脚本
```bash
#!/bin/bash
# 数据库备份脚本
BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="ecommerce"
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${DATE}.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
docker exec mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD \
  --single-transaction \
  --routines \
  --triggers \
  --all-databases > $BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_FILE

# 备份到远程存储
aws s3 cp ${BACKUP_FILE}.gz s3://ecommerce-backups/mysql/

# 清理本地老备份（保留7天）
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "数据库备份完成: ${BACKUP_FILE}.gz"
```

#### 数据库恢复
```bash
#!/bin/bash
# 数据库恢复脚本
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "使用方法: $0 <备份文件路径>"
    exit 1
fi

# 停止应用服务
docker-compose stop app

# 恢复数据库
if [[ $BACKUP_FILE == *.gz ]]; then
    zcat $BACKUP_FILE | docker exec -i mysql mysql -u root -p$MYSQL_ROOT_PASSWORD
else
    docker exec -i mysql mysql -u root -p$MYSQL_ROOT_PASSWORD < $BACKUP_FILE
fi

# 重启应用服务
docker-compose start app

echo "数据库恢复完成"
```

### 文件备份
```bash
#!/bin/bash
# 应用文件备份脚本
BACKUP_DIR="/backup/files"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份上传文件
tar -czf ${BACKUP_DIR}/uploads_${DATE}.tar.gz ./uploads/

# 备份配置文件
tar -czf ${BACKUP_DIR}/config_${DATE}.tar.gz \
  .env \
  docker-compose.yml \
  nginx/

# 同步到远程存储
rsync -avz ${BACKUP_DIR}/ backup-server:/backup/ecommerce/
```

### 备份验证
```bash
#!/bin/bash
# 备份完整性验证脚本
BACKUP_FILE=$1

echo "验证备份文件: $BACKUP_FILE"

# 检查文件完整性
if [[ $BACKUP_FILE == *.gz ]]; then
    gzip -t $BACKUP_FILE
    if [ $? -eq 0 ]; then
        echo "✓ 压缩文件完整性检查通过"
    else
        echo "✗ 压缩文件损坏"
        exit 1
    fi
fi

# 检查SQL语法
if [[ $BACKUP_FILE == *.sql* ]]; then
    # 解压并检查前100行SQL语法
    if [[ $BACKUP_FILE == *.gz ]]; then
        zcat $BACKUP_FILE | head -100 | mysql -u root -p$MYSQL_ROOT_PASSWORD --syntax-check
    else
        head -100 $BACKUP_FILE | mysql -u root -p$MYSQL_ROOT_PASSWORD --syntax-check
    fi
    
    if [ $? -eq 0 ]; then
        echo "✓ SQL语法检查通过"
    else
        echo "✗ SQL语法错误"
        exit 1
    fi
fi

echo "✓ 备份文件验证完成"
```

**[CHECK:DOC-001]** 备份恢复流程必须定期测试验证

---

## 📊 性能监控和优化

### 系统性能监控

#### 实时性能监控脚本
```bash
#!/bin/bash
# 系统性能实时监控
while true; do
    clear
    echo "=== 系统性能监控 $(date) ==="
    
    # CPU使用率
    echo "CPU使用率:"
    top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4"%"}'
    
    # 内存使用率
    echo "内存使用率:"
    free | awk 'NR==2{printf "%.2f%%\n", $3*100/$2}'
    
    # 磁盘使用率
    echo "磁盘使用率:"
    df -h | awk '$NF=="/"{printf "%s\n", $5}'
    
    # 网络连接数
    echo "网络连接数:"
    ss -tuln | wc -l
    
    # Docker容器状态
    echo "容器状态:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    sleep 5
done
```

#### 应用性能分析
```bash
# API响应时间测试
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# 数据库性能分析
docker exec mysql mysql -u root -p$MYSQL_ROOT_PASSWORD -e "
SHOW GLOBAL STATUS LIKE 'Com_%';
SHOW GLOBAL STATUS LIKE 'Questions';
SHOW GLOBAL STATUS LIKE 'Uptime';
"

# Redis性能分析
docker exec redis redis-cli info stats
docker exec redis redis-cli info memory
```

### 性能优化操作

#### 数据库优化
```sql
-- 慢查询分析
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 查看慢查询
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;

-- 索引分析
SHOW INDEX FROM users;
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- 表优化
OPTIMIZE TABLE users;
ANALYZE TABLE users;
```

#### 应用缓存优化
```python
# Redis缓存监控脚本
import redis
import json
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, db=0)

def cache_stats():
    info = r.info()
    stats = {
        'connected_clients': info['connected_clients'],
        'used_memory': info['used_memory_human'],
        'keyspace_hits': info['keyspace_hits'],
        'keyspace_misses': info['keyspace_misses'],
        'hit_rate': info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses']) * 100
    }
    
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    cache_stats()
```

---

## 🔐 安全运维操作

### 访问控制管理

#### 用户权限审计
```bash
#!/bin/bash
# 系统用户权限审计
echo "=== 用户权限审计 $(date) ==="

# 查看系统用户
echo "系统用户列表:"
cat /etc/passwd | grep -v nologin | grep -v false

# 查看sudo权限
echo "Sudo权限用户:"
grep -Po '^sudo.+:\K.*$' /etc/group

# 查看最近登录
echo "最近登录记录:"
last -10

# SSH密钥审计
echo "SSH授权密钥:"
find /home -name "authorized_keys" -exec ls -la {} \;
```

#### SSL证书管理
```bash
#!/bin/bash
# SSL证书检查和续期
DOMAIN="api.ecommerce.com"

# 检查证书有效期
openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | \
openssl x509 -noout -dates

# Let's Encrypt证书续期
certbot renew --dry-run

# Nginx配置重载
nginx -t && nginx -s reload
```

#### 安全扫描
```bash
#!/bin/bash
# 基础安全扫描
echo "=== 安全扫描 $(date) ==="

# 检查开放端口
echo "开放端口扫描:"
nmap -sT -O localhost

# 检查可疑进程
echo "进程检查:"
ps aux | grep -v "grep" | grep -E "(nc|netcat|python -c|bash -i)"

# 检查系统完整性
echo "系统文件完整性:"
find /bin /sbin /usr/bin /usr/sbin -type f -perm +6000 -ls

# 日志异常检查
echo "登录失败尝试:"
grep "Failed password" /var/log/auth.log | tail -10
```

### 漏洞管理
```bash
#!/bin/bash
# 系统漏洞扫描和更新
echo "=== 系统安全更新 ==="

# Ubuntu/Debian系统
apt update
apt list --upgradable | grep -i security

# 安装安全更新
apt-get -s upgrade | grep -i security

# Docker镜像安全扫描
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image ecommerce-app:latest
```

**[CHECK:DOC-007]** 安全运维操作必须有完整的审计日志

---

## 📈 容量规划和扩容

### 资源使用趋势分析
```bash
#!/bin/bash
# 生成资源使用趋势报告
REPORT_FILE="/tmp/capacity_report_$(date +%Y%m%d).txt"

echo "=== 容量规划报告 $(date) ===" > $REPORT_FILE

# CPU使用趋势（过去7天平均）
echo "CPU使用趋势:" >> $REPORT_FILE
sar -u -f /var/log/sa/sa$(date +%d -d '7 days ago') | grep Average >> $REPORT_FILE

# 内存使用趋势
echo "内存使用趋势:" >> $REPORT_FILE
sar -r -f /var/log/sa/sa$(date +%d -d '7 days ago') | grep Average >> $REPORT_FILE

# 磁盘IO趋势
echo "磁盘IO趋势:" >> $REPORT_FILE
sar -d -f /var/log/sa/sa$(date +%d -d '7 days ago') | grep Average >> $REPORT_FILE

# 网络使用趋势
echo "网络使用趋势:" >> $REPORT_FILE
sar -n DEV -f /var/log/sa/sa$(date +%d -d '7 days ago') | grep Average >> $REPORT_FILE

echo "报告生成完成: $REPORT_FILE"
```

### 自动扩容脚本
```bash
#!/bin/bash
# K8s自动扩容脚本
NAMESPACE="ecommerce"
DEPLOYMENT="ecommerce-app"

# 获取当前副本数
CURRENT_REPLICAS=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.replicas}')

# 获取平均CPU使用率
AVG_CPU=$(kubectl top pods -n $NAMESPACE --selector=app=ecommerce-app --no-headers | awk '{sum+=$2} END {print sum/NR}' | sed 's/%//')

echo "当前副本数: $CURRENT_REPLICAS"
echo "平均CPU使用率: ${AVG_CPU}%"

# 扩容条件判断
if (( $(echo "$AVG_CPU > 70" | bc -l) )); then
    NEW_REPLICAS=$((CURRENT_REPLICAS + 2))
    if [ $NEW_REPLICAS -le 10 ]; then
        kubectl scale deployment $DEPLOYMENT --replicas=$NEW_REPLICAS -n $NAMESPACE
        echo "扩容到 $NEW_REPLICAS 个副本"
    fi
elif (( $(echo "$AVG_CPU < 30" | bc -l) )); then
    NEW_REPLICAS=$((CURRENT_REPLICAS - 1))
    if [ $NEW_REPLICAS -ge 2 ]; then
        kubectl scale deployment $DEPLOYMENT --replicas=$NEW_REPLICAS -n $NAMESPACE
        echo "缩容到 $NEW_REPLICAS 个副本"
    fi
fi
```

---

## 📝 运维日志和报告

### 运维操作记录
```bash
# 运维操作日志记录函数
log_operation() {
    local operation=$1
    local result=$2
    local log_file="/var/log/operations.log"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $USER: $operation - $result" >> $log_file
}

# 使用示例
log_operation "应用重启" "成功"
log_operation "数据库备份" "失败 - 磁盘空间不足"
```

### 周报生成脚本
```bash
#!/bin/bash
# 运维周报自动生成
WEEK_START=$(date -d 'last monday' +%Y-%m-%d)
WEEK_END=$(date -d 'next sunday' +%Y-%m-%d)
REPORT_FILE="/tmp/weekly_report_$(date +%Y%m%d).md"

cat > $REPORT_FILE << EOF
# 运维周报 ($WEEK_START 至 $WEEK_END)

## 系统状态概览
- 服务可用率: $(calculate_uptime)%
- 平均响应时间: $(calculate_avg_response_time)ms
- 告警数量: $(count_alerts)次

## 主要运维活动
$(grep "$WEEK_START\|$WEEK_END" /var/log/operations.log)

## 性能指标
- CPU平均使用率: $(calculate_cpu_usage)%
- 内存平均使用率: $(calculate_memory_usage)%
- 磁盘使用率: $(calculate_disk_usage)%

## 问题和改进
$(list_issues_and_improvements)

EOF

echo "周报生成完成: $REPORT_FILE"
```

### 月度容量报告
```python
#!/usr/bin/env python3
# 月度容量和性能报告生成
import json
import datetime
from collections import defaultdict

def generate_monthly_report():
    report = {
        "report_date": datetime.datetime.now().isoformat(),
        "period": "monthly",
        "metrics": {
            "cpu_usage": get_cpu_metrics(),
            "memory_usage": get_memory_metrics(),
            "storage_usage": get_storage_metrics(),
            "network_traffic": get_network_metrics()
        },
        "capacity_recommendations": generate_recommendations(),
        "incidents": get_incident_summary()
    }
    
    with open(f'monthly_report_{datetime.datetime.now().strftime("%Y%m")}.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"月度报告已生成: {f.name}")

if __name__ == "__main__":
    generate_monthly_report()
```

**[CHECK:DOC-003]** 运维报告必须定期生成并归档保存

---

## 🛠️ 运维工具和脚本

### 一键环境检查脚本
```bash
#!/bin/bash
# 一键环境健康检查
echo "=== 环境健康检查 $(date) ==="

# 检查项目数组
checks=(
    "系统负载:check_load"
    "磁盘空间:check_disk"
    "内存使用:check_memory"
    "服务状态:check_services"
    "数据库连接:check_database"
    "Redis连接:check_redis"
    "应用健康:check_app_health"
    "SSL证书:check_ssl_cert"
)

# 执行检查
for check in "${checks[@]}"; do
    name=$(echo $check | cut -d: -f1)
    func=$(echo $check | cut -d: -f2)
    
    echo -n "检查 $name ... "
    if $func; then
        echo "✓ 正常"
    else
        echo "✗ 异常"
    fi
done

echo "=== 检查完成 ==="
```

### 批量操作脚本
```bash
#!/bin/bash
# 批量服务器操作脚本
SERVERS=("server1" "server2" "server3")
COMMAND=$1

if [ -z "$COMMAND" ]; then
    echo "使用方法: $0 <command>"
    exit 1
fi

for server in "${SERVERS[@]}"; do
    echo "在 $server 上执行: $COMMAND"
    ssh $server "$COMMAND"
done
```

---

## 📞 运维值班指南

### 值班职责
1. **监控告警响应**: 及时响应所有监控告警
2. **系统巡检**: 执行日常系统健康检查
3. **问题处理**: 处理用户反馈的问题
4. **文档记录**: 记录所有运维操作和问题
5. **升级支持**: 必要时联系上级支持

### 值班交接清单
- [ ] **当前系统状态**: 检查所有服务运行状态
- [ ] **未解决问题**: 说明正在处理的问题
- [ ] **计划维护**: 告知计划中的维护活动
- [ ] **监控告警**: 检查告警状态和处理情况
- [ ] **备份状态**: 确认最新备份完成情况
- [ ] **文档更新**: 移交期间的操作记录

### 紧急联系方式
- **技术主管**: [联系方式]
- **安全团队**: security@ecommerce.com
- **云服务商**: [技术支持热线]

**[CHECK:DOC-002]** 值班交接必须有完整的书面记录

---

## 相关文档
- [部署指南](deployment.md) - 部署操作和流程
- [监控告警](monitoring.md) - 监控配置和告警处理
- [故障排除](troubleshooting.md) - 故障诊断和处理流程
- [MASTER工作流程](../MASTER.md) - 运维操作检查点
