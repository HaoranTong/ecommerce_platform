# 用户角色字段迁移文档

## 文档说明
- **内容**: 为User模型添加role字段的数据库迁移设计
- **使用方法**: 数据库迁移开发的指导文档
- **更新方法**: 数据模型变更时更新
- **引用关系**: 基于auth-integration-design.md
- **更新频率**: 数据模型变更时

## 迁移目标

### 变更目标
1. **添加角色字段** - 在users表中添加role列
2. **设置默认值** - 现有用户默认为普通用户角色
3. **数据完整性** - 确保角色值有效性约束
4. **向下兼容** - 迁移不影响现有功能

### 数据模型设计

#### User模型扩展
```python
class User(Base):
    __tablename__ = 'users'
    
    # 现有字段...
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # 新增角色字段
    role = Column(String(20), nullable=False, default='user')
    
    # 其他字段...
```

#### 角色值约束
```sql
-- 角色枚举值
CONSTRAINT user_role_check CHECK (role IN ('user', 'admin', 'super_admin'))
```

## 迁移计划

### 第1步：数据模型修改
**文件**: `app/models.py`

**修改内容**:
```python
# 在User类中添加
role = Column(String(20), nullable=False, default='user')

# 添加表约束（可选，通过SQLAlchemy）
__table_args__ = (
    CheckConstraint("role IN ('user', 'admin', 'super_admin')", name='user_role_check'),
    Index('idx_username_email', 'username', 'email'),
)
```

### 第2步：Alembic迁移脚本
**自动生成命令**:
```bash
alembic revision --autogenerate -m "add_user_role_field"
```

**预期迁移内容**:
```python
def upgrade():
    # 添加role列，默认值为'user'
    op.add_column('users', sa.Column('role', sa.String(20), nullable=False, server_default='user'))
    
    # 添加检查约束
    op.create_check_constraint(
        'user_role_check',
        'users', 
        "role IN ('user', 'admin', 'super_admin')"
    )

def downgrade():
    # 删除约束
    op.drop_constraint('user_role_check', 'users', type_='check')
    
    # 删除列
    op.drop_column('users', 'role')
```

### 第3步：数据初始化
**管理员用户创建脚本** (可选):
```python
# 创建默认管理员用户的脚本
def create_default_admin():
    admin_user = User(
        username="admin",
        email="admin@example.com", 
        password_hash=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    # 数据库操作...
```

## Schema更新

### UserRead Schema
```python
class UserRead(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str  # 新增字段
    phone: Optional[str] = None
    real_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
```

### UserCreate Schema  
```python
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"  # 默认为普通用户
    phone: Optional[str] = None
    real_name: Optional[str] = None
```

## 验证计划

### 迁移验证
- [ ] 迁移脚本语法正确
- [ ] 迁移up/down操作可逆
- [ ] 现有数据不受影响
- [ ] 新字段默认值正确

### 功能验证
- [ ] 新用户注册包含角色字段
- [ ] 现有用户角色为默认值'user'
- [ ] 角色约束正常工作
- [ ] API响应包含角色信息

### 兼容性验证
- [ ] 现有认证功能正常
- [ ] API接口向下兼容
- [ ] 数据库查询性能无影响

## 风险控制

### 迁移风险
- **数据丢失风险** - 低，只是添加字段
- **性能影响** - 低，添加单列操作较快
- **回滚风险** - 低，可以安全删除新增列

### 应对措施
1. **备份数据库** - 迁移前完整备份
2. **测试环境验证** - 先在测试环境执行
3. **监控迁移过程** - 记录迁移时间和影响
4. **回滚方案** - 准备快速回滚脚本

---

## 实施检查清单

### 开发前
- [x] 设计数据模型变更
- [x] 规划迁移步骤
- [x] 评估风险和影响
- [ ] 准备测试数据

### 开发中  
- [ ] 修改User模型
- [ ] 生成迁移脚本
- [ ] 更新Schema定义
- [ ] 测试迁移过程

### 开发后
- [ ] 验证迁移结果
- [ ] 测试新功能
- [ ] 更新API文档
- [ ] 命名规范检查

---

*迁移文档创建时间: 2025-09-11*  
*下一次更新: 迁移完成后*
