# 运维故障排除指南

## 文档说明
- **内容**：常见故障诊断、问题解决流程、应急响应、故障预防
- **使用者**：运维人员、开发人员、值班工程师
- **更新频率**：故障案例和解决方案更新时维护
- **关联文档**：[部署指南](deployment.md)、[监控告警](monitoring.md)、[运维手册](runbook.md)

**[CHECK:DOC-001]** 故障排除流程必须在生产部署前完善

---

## 🚨 应急响应流程

### 故障等级定义
| 等级 | 影响范围 | 响应时间 | 处理优先级 |
|------|----------|----------|------------|
| **P0 - 紧急** | 服务完全不可用 | 15分钟 | 最高 |
| **P1 - 严重** | 核心功能受影响 | 1小时 | 高 |
| **P2 - 中等** | 部分功能异常 | 4小时 | 中 |
| **P3 - 轻微** | 性能下降或非关键问题 | 1天 | 低 |

### 应急响应步骤
```
1. 故障确认 (2分钟)
   ├─ 监控告警验证
   ├─ 用户反馈确认
   └─ 影响范围评估

2. 启动应急 (3分钟)
   ├─ 通知相关人员
   ├─ 建立故障沟通群
   └─ 开始故障记录

3. 快速止损 (10分钟)
   ├─ 服务降级
   ├─ 流量切换
   └─ 回滚操作

4. 根因分析 (后续)
   ├─ 日志分析
   ├─ 代码审查
   └─ 基础设施检查

5. 修复验证 (30分钟)
   ├─ 修复部署
   ├─ 功能测试
   └─ 监控确认

6. 故障总结 (3天内)
   ├─ 根因报告
   ├─ 改进措施
   └─ 预防方案
```

**[CHECK:DOC-003]** 应急响应流程必须定期演练验证

---

## 🔧 系统故障诊断

### 1. 服务不可用问题

#### 症状识别
- HTTP 502/503/504错误
- 连接超时
- 监控显示服务DOWN

#### 诊断步骤
```bash
# 1. 检查服务状态
docker ps | grep ecommerce-app
kubectl get pods -n ecommerce

# 2. 查看服务日志
docker logs ecommerce-app --tail=100
kubectl logs -f deployment/ecommerce-app -n ecommerce

# 3. 检查资源使用
docker stats ecommerce-app
kubectl top pods -n ecommerce

# 4. 验证网络连通性
curl -I http://localhost:8000/api/health
nslookup api.ecommerce.com
```

#### 常见原因及解决方案
| 原因 | 解决方案 | 预防措施 |
|------|----------|----------|
| 内存溢出 | 重启服务，调整内存限制 | 设置内存监控告警 |
| 端口冲突 | 修改端口配置，重启服务 | 端口管理标准化 |
| 配置错误 | 修正配置文件，重新部署 | 配置验证流程 |
| 依赖服务故障 | 检查数据库/Redis连接 | 依赖服务监控 |

#### 快速恢复操作
```bash
# 容器环境恢复
docker-compose restart app
docker-compose up -d --force-recreate app

# K8s环境恢复  
kubectl rollout restart deployment/ecommerce-app -n ecommerce
kubectl scale deployment ecommerce-app --replicas=0 -n ecommerce
kubectl scale deployment ecommerce-app --replicas=3 -n ecommerce
```

### 2. 数据库连接问题

#### 症状识别
- 数据库连接超时
- "Too many connections"错误
- 查询响应缓慢

#### 诊断命令
```bash
# 检查MySQL状态
docker exec -it mysql mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
docker exec -it mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# 检查连接池状态
docker logs ecommerce-app | grep "database"
docker logs ecommerce-app | grep -i "connection"

# 网络连接检查
telnet mysql-host 3306
nc -zv mysql-host 3306
```

#### 解决方案
```sql
-- 查看连接数配置
SHOW VARIABLES LIKE 'max_connections';
SHOW STATUS LIKE 'Threads_connected';

-- 杀死僵死连接
SELECT Id, User, Host, db, Command, Time, State, Info 
FROM information_schema.PROCESSLIST 
WHERE Command != 'Sleep' AND Time > 300;

KILL [connection_id];

-- 临时增加连接数
SET GLOBAL max_connections = 200;
```

#### 预防配置
```python
# 数据库连接池优化
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "max_overflow": 30,
    "pool_pre_ping": True
}
```

### 3. Redis连接问题

#### 诊断步骤
```bash
# 检查Redis状态
docker exec -it redis redis-cli ping
docker exec -it redis redis-cli info clients

# 检查连接数
docker exec -it redis redis-cli config get maxclients
docker exec -it redis redis-cli client list | wc -l

# 内存使用检查
docker exec -it redis redis-cli info memory
```

#### 常见问题处理
```bash
# 清理过期连接
redis-cli client kill type normal

# 内存清理
redis-cli flushall  # 谨慎使用!

# 配置调优
redis-cli config set maxmemory 2gb
redis-cli config set maxmemory-policy allkeys-lru
```

**[CHECK:DOC-002]** 数据库故障处理必须有备份恢复预案

---

## 📊 性能问题诊断

### 1. API响应慢问题

#### 性能分析工具
```bash
# 应用性能分析
curl -o /dev/null -s -w "时间详情: 连接:%{time_connect} 首字节:%{time_starttransfer} 总时间:%{time_total}\n" http://api.ecommerce.com/api/health

# 数据库慢查询
docker exec -it mysql mysql -u root -p -e "
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
SHOW VARIABLES LIKE 'slow_query%';"

# 系统资源监控
htop
iotop
nethogs
```

#### 性能优化检查清单
- [ ] 数据库索引优化
- [ ] SQL查询性能分析
- [ ] Redis缓存命中率
- [ ] 应用代码性能分析
- [ ] 网络延迟检查
- [ ] 系统资源瓶颈

### 2. 内存泄漏诊断

#### 监控内存使用趋势
```bash
# 容器内存使用
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# 应用内存分析
python -m memory_profiler your_script.py
py-spy top --pid [process_id]
```

#### 内存泄漏处理
```python
# 内存使用监控代码
import psutil
import gc

def check_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # 强制垃圾回收
    gc.collect()
```

---

## 🔐 安全问题处理

### 1. 异常访问检测

#### 日志分析脚本
```bash
# 检查异常IP访问
tail -f /var/log/nginx/access.log | grep -E "(404|403|500)" | cut -d' ' -f1 | sort | uniq -c | sort -rn

# 检查可疑请求
grep -E "(admin|config|wp-|\.php|\.asp)" /var/log/nginx/access.log | tail -20

# SQL注入尝试检测
grep -i "union\|select\|drop\|insert\|update" /var/log/nginx/access.log
```

#### 应急处理措施
```bash
# 临时IP封禁
iptables -A INPUT -s [suspicious_ip] -j DROP

# Nginx访问限制
# 在nginx.conf中添加
location / {
    limit_req zone=one burst=10 nodelay;
    deny [suspicious_ip];
}
```

### 2. 密钥泄露应急处理

#### 处理流程
1. **立即轮换**：更换所有相关密钥
2. **影响评估**：检查泄露密钥的使用范围
3. **访问审计**：分析可疑的访问记录
4. **通知相关方**：及时通知相关团队和用户

#### 密钥轮换脚本
```bash
#!/bin/bash
# 密钥轮换脚本
echo "开始密钥轮换流程..."

# 1. 生成新密钥
NEW_JWT_SECRET=$(openssl rand -base64 32)
NEW_DB_PASSWORD=$(openssl rand -base64 16)

# 2. 更新K8s Secret
kubectl create secret generic app-secrets-new \
  --from-literal=JWT_SECRET_KEY=$NEW_JWT_SECRET \
  --from-literal=DB_PASSWORD=$NEW_DB_PASSWORD \
  -n ecommerce

# 3. 更新应用配置
kubectl patch deployment ecommerce-app -n ecommerce -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","env":[{"name":"JWT_SECRET_KEY","valueFrom":{"secretKeyRef":{"name":"app-secrets-new","key":"JWT_SECRET_KEY"}}}]}]}}}}'

# 4. 等待部署完成
kubectl rollout status deployment/ecommerce-app -n ecommerce

echo "密钥轮换完成"
```

**[CHECK:DOC-007]** 安全事件处理必须有完整的审计记录

---

## 🛠️ 基础设施问题

### 1. 磁盘空间不足

#### 快速清理操作
```bash
# 查看磁盘使用情况
df -h
du -h --max-depth=1 /

# Docker清理
docker system prune -a -f
docker volume prune -f

# 日志清理
find /var/log -type f -name "*.log" -mtime +30 -delete
journalctl --vacuum-time=7d

# 临时文件清理
rm -rf /tmp/*
rm -rf /var/tmp/*
```

#### 磁盘扩容脚本
```bash
#!/bin/bash
# AWS EBS卷扩容脚本
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
VOLUME_ID=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId' --output text)

# 扩容卷到100GB
aws ec2 modify-volume --volume-id $VOLUME_ID --size 100

# 扩展文件系统
sudo resize2fs /dev/xvda1
```

### 2. 网络连接问题

#### 网络诊断命令
```bash
# 基础网络检查
ping -c 4 8.8.8.8
nslookup api.ecommerce.com
traceroute api.ecommerce.com

# 端口连通性检查
telnet api.ecommerce.com 443
nc -zv api.ecommerce.com 80 443

# 防火墙规则检查
iptables -L -n
ufw status verbose

# DNS解析检查
dig api.ecommerce.com
host api.ecommerce.com
```

#### 网络问题修复
```bash
# 重启网络服务
systemctl restart networking
systemctl restart systemd-resolved

# 刷新DNS缓存
systemd-resolve --flush-caches
resolvectl flush-caches

# 修复路由表
ip route add default via [gateway_ip]
```

---

## 📋 故障处理检查清单

### 故障响应检查清单
- [ ] **确认故障等级**：评估影响范围和严重程度
- [ ] **建立沟通渠道**：创建故障处理群组
- [ ] **记录故障信息**：详细记录故障现象和时间
- [ ] **执行应急措施**：优先恢复服务可用性
- [ ] **收集诊断信息**：保存日志、监控数据、配置信息
- [ ] **实施修复方案**：根据根因分析结果修复
- [ ] **验证修复效果**：确认服务完全恢复
- [ ] **更新监控告警**：完善监控和告警规则
- [ ] **编写故障报告**：总结经验教训和改进措施
- [ ] **分享处理经验**：团队知识共享和培训

### 预防措施检查清单
- [ ] **完善监控覆盖**：确保关键指标都有监控
- [ ] **优化告警规则**：减少误报，提高准确性
- [ ] **定期演练**：模拟故障场景进行应急演练
- [ ] **容量规划**：基于监控数据进行容量评估
- [ ] **备份策略**：确保数据备份完整可用
- [ ] **文档更新**：及时更新故障处理文档
- [ ] **自动化改进**：提高故障处理的自动化程度

**[CHECK:DOC-001]** 故障处理流程必须定期审查更新

---

## 🔍 常见错误代码解决方案

### HTTP状态码问题

| 状态码 | 常见原因 | 解决方案 |
|--------|----------|----------|
| 502 | 后端服务不可用 | 检查应用服务状态，重启服务 |
| 503 | 服务临时不可用 | 检查负载均衡配置，扩容实例 |
| 504 | 网关超时 | 优化应用性能，调整超时配置 |
| 500 | 服务器内部错误 | 查看应用日志，修复代码bug |
| 404 | 资源未找到 | 检查路由配置，确认资源路径 |

### 数据库错误码

| 错误码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| 1040 | Too many connections | 增加连接数限制或优化连接池 |
| 1062 | Duplicate entry | 检查唯一键约束，处理重复数据 |
| 1146 | Table doesn't exist | 执行数据库迁移，创建缺失表 |
| 2003 | Can't connect to server | 检查网络连接和数据库服务状态 |

### 应用错误处理

```python
# 通用错误处理中间件
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # 区分错误类型
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )
    
    # 生产环境隐藏详细错误
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

---

## 📞 应急联系方式

### 值班责任人
- **运维值班**: ops-oncall@ecommerce.com
- **开发值班**: dev-oncall@ecommerce.com
- **安全值班**: security@ecommerce.com

### 升级路径
1. **一线处理**: 值班工程师 (15分钟响应)
2. **二线支持**: 技术主管 (30分钟响应)
3. **三线支持**: 技术总监 (1小时响应)

### 外部支持
- **云服务商支持**: [云平台技术支持热线]
- **监控服务商**: [监控平台支持联系方式]

**[CHECK:DOC-002]** 应急联系方式必须保持最新状态

---

## 相关文档
- [部署指南](deployment.md) - 部署相关故障排除
- [监控告警](monitoring.md) - 监控配置和告警处理
- [运维手册](runbook.md) - 日常运维操作指南  
- [MASTER工作流程](../../MASTER.md) - 故障处理检查点
