# 质量控制模块 API实施细节

## 模块概述
质量控制模块API负责农产品质量认证证书的管理，提供证书的创建、查询和删除功能的具体实现。

### 开发进度
- **设计阶段**: ✅ 已完成
- **开发阶段**: ✅ 已完成（基础功能）
- **测试阶段**: 🔄 进行中

## 技术实施方案

### 1. 路由实现
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.shared.models import Certificate
from .schemas import CertificateRead, CertificateCreate

router = APIRouter()

@router.post("/certificates", response_model=CertificateRead, status_code=status.HTTP_201_CREATED)
def create_certificate(payload: CertificateCreate, db: Session = Depends(get_db)):
    """创建新证书"""
    # 检查序列号唯一性
    existing = db.query(Certificate).filter(Certificate.serial == payload.serial).first()
    if existing:
        raise HTTPException(status_code=400, detail="证书序列号已存在")
    
    # 创建证书记录
    cert = Certificate(
        name=payload.name, 
        issuer=payload.issuer, 
        serial=payload.serial, 
        description=payload.description
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert

@router.get("/certificates", response_model=List[CertificateRead])
def list_certificates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取证书列表"""
    certs = db.query(Certificate).offset(skip).limit(limit).all()
    return certs

@router.get("/certificates/{cert_id}", response_model=CertificateRead)
def get_certificate(cert_id: int, db: Session = Depends(get_db)):
    """获取指定证书信息"""
    cert = db.query(Certificate).get(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="证书不存在")
    return cert

@router.delete("/certificates/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certificate(cert_id: int, db: Session = Depends(get_db)):
    """删除证书"""
    cert = db.query(Certificate).get(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="证书不存在")
    db.delete(cert)
    db.commit()
    return None
```

### 2. 数据模型实现
```python
# 使用共享数据模型 app.shared.models.Certificate
class Certificate(Base):
    __tablename__ = 'certificates'
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    issuer = Column(String(200), nullable=True)
    serial = Column(String(200), unique=True, nullable=False)
    
    # 注意：当前模型缺少description字段，需要扩展
```

### 3. 请求响应模型实现
```python
# schemas.py（待实现）
from pydantic import BaseModel, Field
from typing import Optional

class CertificateBase(BaseModel):
    name: str = Field(..., max_length=200, description="证书名称")
    issuer: Optional[str] = Field(None, max_length=200, description="发证机构")
    serial: str = Field(..., max_length=200, description="证书序列号")
    description: Optional[str] = Field(None, description="证书描述")

class CertificateCreate(CertificateBase):
    pass

class CertificateRead(CertificateBase):
    id: int
    
    class Config:
        from_attributes = True
```

## 实施细节

### 路由注册实现
```python
# app/main.py 中的路由注册
from app.modules.quality_control.router import router as quality_control_router

app.include_router(
    quality_control_router, 
    prefix="/api/v1/quality-control", 
    tags=["质量控制"]
)
```

### 数据库连接实现
```python
# 使用共享的数据库连接
from app.core.database import get_db

# 依赖注入数据库会话
def create_certificate(payload: CertificateCreate, db: Session = Depends(get_db)):
    # 业务逻辑实现
    pass
```

### 错误处理实现
```python
from fastapi import HTTPException

# 标准错误处理
def handle_certificate_not_found():
    raise HTTPException(status_code=404, detail="证书不存在")

def handle_duplicate_serial():
    raise HTTPException(status_code=400, detail="证书序列号已存在")
```

## 当前实现状态

### 已实现功能
- ✅ **证书创建**: POST /certificates - 支持基本字段创建
- ✅ **证书列表**: GET /certificates - 支持分页查询
- ✅ **证书详情**: GET /certificates/{id} - 根据ID获取详情
- ✅ **证书删除**: DELETE /certificates/{id} - 根据ID删除证书

### 实现限制
1. **数据模型限制**: 当前Certificate模型缺少description字段
2. **Schema缺失**: schemas.py文件为空，需要实现Pydantic模型
3. **Service层缺失**: service.py文件为空，业务逻辑直接在路由中实现
4. **权限控制**: 尚未实现用户权限验证
5. **输入验证**: 基础的长度和格式验证需要完善

### 待扩展功能
- ⏳ **证书搜索**: 基于名称、发证机构的搜索功能
- ⏳ **证书验证**: 对接第三方机构API验证证书真实性
- ⏳ **文件上传**: 支持证书图片/PDF文件上传
- ⏳ **批量操作**: 支持批量创建和删除证书
- ⏳ **审核工作流**: 证书创建和修改的审核流程

## 技术债务

### 需要优化的实现
1. **数据模型扩展**
```python
# 建议扩展Certificate模型
class Certificate(Base):
    __tablename__ = 'certificates'
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    issuer = Column(String(200), nullable=True)
    serial = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)  # 需要添加
    certificate_type = Column(String(50), nullable=True)  # 需要添加
    issue_date = Column(Date, nullable=True)  # 需要添加
    expire_date = Column(Date, nullable=True)  # 需要添加
    file_url = Column(String(500), nullable=True)  # 需要添加
    status = Column(String(20), default='active')  # 需要添加
    created_at = Column(DateTime, default=func.now())  # 需要添加
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # 需要添加
```

2. **Service层实现**
```python
# service.py 建议实现
class CertificateService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_certificate(self, cert_data: CertificateCreate) -> Certificate:
        # 验证业务规则
        await self._validate_certificate_data(cert_data)
        
        # 检查序列号唯一性
        if await self._check_serial_exists(cert_data.serial):
            raise ValueError("证书序列号已存在")
        
        # 创建证书
        certificate = Certificate(**cert_data.dict())
        self.db.add(certificate)
        self.db.commit()
        self.db.refresh(certificate)
        return certificate
    
    async def _validate_certificate_data(self, cert_data: CertificateCreate):
        # 业务规则验证
        pass
    
    async def _check_serial_exists(self, serial: str) -> bool:
        # 检查序列号是否存在
        return self.db.query(Certificate).filter(Certificate.serial == serial).first() is not None
```

3. **完善Schema实现**
```python
# schemas.py 完整实现
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date

class CertificateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="证书名称")
    issuer: Optional[str] = Field(None, max_length=200, description="发证机构")
    serial: str = Field(..., min_length=1, max_length=200, description="证书序列号")
    description: Optional[str] = Field(None, max_length=1000, description="证书描述")
    certificate_type: Optional[str] = Field(None, max_length=50, description="证书类型")
    issue_date: Optional[date] = Field(None, description="发证日期")
    expire_date: Optional[date] = Field(None, description="过期日期")
    
    @validator('expire_date')
    def expire_date_must_be_future(cls, v, values):
        if v and 'issue_date' in values and values['issue_date']:
            if v <= values['issue_date']:
                raise ValueError('过期日期必须晚于发证日期')
        return v

class CertificateRead(BaseModel):
    id: int
    name: str
    issuer: Optional[str]
    serial: str
    description: Optional[str]
    certificate_type: Optional[str]
    issue_date: Optional[date]
    expire_date: Optional[date]
    status: str
    
    class Config:
        from_attributes = True
```

## 性能优化建议

### 数据库优化
1. **索引优化**
```sql
-- 证书序列号唯一索引（已存在）
CREATE UNIQUE INDEX idx_certificates_serial ON certificates(serial);

-- 发证机构索引（用于搜索）
CREATE INDEX idx_certificates_issuer ON certificates(issuer);

-- 证书名称索引（用于搜索）
CREATE INDEX idx_certificates_name ON certificates(name);

-- 证书类型索引
CREATE INDEX idx_certificates_type ON certificates(certificate_type);

-- 状态索引
CREATE INDEX idx_certificates_status ON certificates(status);

-- 复合索引：类型+状态
CREATE INDEX idx_certificates_type_status ON certificates(certificate_type, status);
```

2. **查询优化**
```python
# 分页查询优化
def list_certificates_optimized(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # 限制最大查询数量，避免大量数据查询
    limit = min(limit, 100)
    
    # 使用索引优化的查询
    certs = db.query(Certificate)\
        .filter(Certificate.status == 'active')\
        .order_by(Certificate.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return certs
```

### 缓存策略
```python
# Redis缓存实现（未来功能）
from app.core.redis_client import redis_client

async def get_certificate_cached(cert_id: int, db: Session):
    # 尝试从缓存获取
    cache_key = f"certificate:{cert_id}"
    cached_cert = await redis_client.get(cache_key)
    
    if cached_cert:
        return json.loads(cached_cert)
    
    # 从数据库获取并缓存
    cert = db.query(Certificate).get(cert_id)
    if cert:
        await redis_client.setex(cache_key, 3600, json.dumps(cert.dict()))
    
    return cert
```

## 测试实施

### 单元测试实现
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db
from app.shared.models import Base

# 测试数据库设置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

def test_create_certificate(client):
    """测试创建证书"""
    response = client.post(
        "/api/v1/quality-control/certificates",
        json={
            "name": "测试证书",
            "issuer": "测试机构",
            "serial": "TEST-001"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "测试证书"
    assert data["serial"] == "TEST-001"

def test_get_certificates(client):
    """测试获取证书列表"""
    # 先创建一个证书
    client.post(
        "/api/v1/quality-control/certificates",
        json={
            "name": "测试证书",
            "issuer": "测试机构", 
            "serial": "TEST-001"
        }
    )
    
    # 获取列表
    response = client.get("/api/v1/quality-control/certificates")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "测试证书"

def test_duplicate_serial_error(client):
    """测试重复序列号错误"""
    # 创建第一个证书
    client.post(
        "/api/v1/quality-control/certificates",
        json={
            "name": "证书1",
            "serial": "DUPLICATE-001"
        }
    )
    
    # 尝试创建重复序列号的证书
    response = client.post(
        "/api/v1/quality-control/certificates",
        json={
            "name": "证书2",
            "serial": "DUPLICATE-001"
        }
    )
    assert response.status_code == 400
    assert "序列号已存在" in response.json()["detail"]
```

### 集成测试实现
```python
def test_certificate_crud_workflow(client):
    """测试完整的CRUD工作流程"""
    # 1. 创建证书
    create_response = client.post(
        "/api/v1/quality-control/certificates",
        json={
            "name": "集成测试证书",
            "issuer": "测试机构",
            "serial": "INTEGRATION-001"
        }
    )
    assert create_response.status_code == 201
    cert_id = create_response.json()["id"]
    
    # 2. 获取证书详情
    get_response = client.get(f"/api/v1/quality-control/certificates/{cert_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "集成测试证书"
    
    # 3. 删除证书
    delete_response = client.delete(f"/api/v1/quality-control/certificates/{cert_id}")
    assert delete_response.status_code == 204
    
    # 4. 验证证书已删除
    get_deleted_response = client.get(f"/api/v1/quality-control/certificates/{cert_id}")
    assert get_deleted_response.status_code == 404
```

## 部署配置

### 环境变量配置
```bash
# 质量控制模块配置
QUALITY_CONTROL_ENABLED=true

# 证书文件存储配置（未来功能）
CERTIFICATE_STORAGE_TYPE=local  # local/oss/s3
CERTIFICATE_STORAGE_PATH=/data/certificates/
CERTIFICATE_MAX_FILE_SIZE=10485760  # 10MB

# 缓存配置
CERTIFICATE_CACHE_TTL=3600  # 1小时
```

### 数据库初始化
```sql
-- 创建证书表（如果不存在）
CREATE TABLE IF NOT EXISTS certificates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    issuer VARCHAR(200),
    serial VARCHAR(200) UNIQUE NOT NULL,
    KEY idx_certificates_serial (serial),
    KEY idx_certificates_issuer (issuer),
    KEY idx_certificates_name (name)
);
```

## 监控和日志

### 监控指标
```python
from prometheus_client import Counter, Histogram

# 定义监控指标
certificate_operations = Counter('certificate_operations_total', 'Total certificate operations', ['operation', 'status'])
certificate_response_time = Histogram('certificate_response_time_seconds', 'Certificate API response time')

# 在路由中使用
@router.post("/certificates")
def create_certificate(payload: CertificateCreate, db: Session = Depends(get_db)):
    start_time = time.time()
    try:
        # 业务逻辑
        result = create_certificate_logic(payload, db)
        certificate_operations.labels(operation='create', status='success').inc()
        return result
    except Exception as e:
        certificate_operations.labels(operation='create', status='error').inc()
        raise
    finally:
        certificate_response_time.observe(time.time() - start_time)
```

### 日志记录
```python
import logging

logger = logging.getLogger(__name__)

@router.post("/certificates")
def create_certificate(payload: CertificateCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating certificate with serial: {payload.serial}")
    
    try:
        # 业务逻辑
        result = create_certificate_logic(payload, db)
        logger.info(f"Certificate created successfully: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create certificate: {e}")
        raise
```

## 相关文档
- [质量控制模块概览](overview.md)
- [质量控制模块API规范](api-spec.md)
- [质量控制模块技术设计](design.md)
- [API标准规范](../../standards/api-standards.md)
- [测试规范](../../standards/testing-standards.md)