"""
质量控制模块集成测试 - 完整测试套件
测试质量控制模块与数据库的真实交互
包含Certificate模型的完整CRUD操作和业务流程测试
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
from app.core.database import get_db
from app.modules.quality_control.models import Certificate
from app.modules.user_auth.models import User


@pytest.fixture
def client():
    """FastAPI 测试客户端"""
    return TestClient(app)


@pytest.fixture
def test_user(integration_test_db: Session):
    """创建测试用户"""
    unique_suffix = str(uuid.uuid4())[:8]
    user = User(
        username=f"qc_test_user_{unique_suffix}",
        email=f"qc_{unique_suffix}@test.com",
        password_hash="hashed_test_password",
        real_name=f"质控测试用户_{unique_suffix}",
        phone=f"133{unique_suffix[:8]}"
    )
    integration_test_db.add(user)
    integration_test_db.commit()
    integration_test_db.refresh(user)
    return user


class TestCertificateIntegration:
    """证书集成测试"""
    
    @pytest.mark.integration
    def test_create_certificate(self, integration_test_db: Session):
        """测试创建证书"""
        # 创建证书
        unique_suffix = str(uuid.uuid4())[:8]
        current_time = datetime.now()
        
        certificate = Certificate(
            serial=f"CERT-{current_time.strftime('%Y%m%d')}-{unique_suffix}",
            name=f"ISO质量认证_{unique_suffix}",
            issuer="国际标准化组织",
            description="产品质量管理体系认证证书",
            issued_at=current_time,
            expires_at=current_time + timedelta(days=365),
            is_active=True
        )
        
        integration_test_db.add(certificate)
        integration_test_db.commit()
        integration_test_db.refresh(certificate)
        
        # 验证证书创建
        assert certificate.id is not None
        assert certificate.serial.startswith("CERT-")
        assert certificate.name.startswith("ISO质量认证_")
        assert certificate.issuer == "国际标准化组织"
        assert certificate.is_active == True
        assert certificate.expires_at > certificate.issued_at
        
    @pytest.mark.integration
    def test_certificate_validity_check(self, integration_test_db: Session):
        """测试证书有效性检查"""
        unique_suffix = str(uuid.uuid4())[:8]
        current_time = datetime.now()
        
        # 创建有效证书
        valid_certificate = Certificate(
            serial=f"VALID-CERT-{unique_suffix}",
            name=f"有效证书_{unique_suffix}",
            issuer="认证机构",
            issued_at=current_time - timedelta(days=30),
            expires_at=current_time + timedelta(days=30),
            is_active=True
        )
        
        # 创建过期证书
        expired_certificate = Certificate(
            serial=f"EXPIRED-CERT-{unique_suffix}",
            name=f"过期证书_{unique_suffix}",
            issuer="认证机构",
            issued_at=current_time - timedelta(days=60),
            expires_at=current_time - timedelta(days=1),
            is_active=True
        )
        
        # 创建停用证书
        inactive_certificate = Certificate(
            serial=f"INACTIVE-CERT-{unique_suffix}",
            name=f"停用证书_{unique_suffix}",
            issuer="认证机构",
            issued_at=current_time - timedelta(days=30),
            expires_at=current_time + timedelta(days=30),
            is_active=False
        )
        
        integration_test_db.add_all([valid_certificate, expired_certificate, inactive_certificate])
        integration_test_db.commit()
        
        # 验证有效证书
        def is_certificate_valid(cert: Certificate) -> bool:
            now = datetime.now()
            return cert.is_active and cert.issued_at <= now <= cert.expires_at
        
        assert is_certificate_valid(valid_certificate) == True
        assert is_certificate_valid(expired_certificate) == False
        assert is_certificate_valid(inactive_certificate) == False
        
    @pytest.mark.integration
    def test_certificate_search_and_filter(self, integration_test_db: Session):
        """测试证书搜索和过滤"""
        unique_suffix = str(uuid.uuid4())[:8]
        current_time = datetime.now()
        
        # 创建多个证书用于测试
        certificates_data = [
            {
                "serial": f"ISO9001-{unique_suffix}-001",
                "name": f"ISO9001质量管理_{unique_suffix}",
                "issuer": "ISO组织",
                "expires_at": current_time + timedelta(days=100)
            },
            {
                "serial": f"ISO14001-{unique_suffix}-002", 
                "name": f"ISO14001环境管理_{unique_suffix}",
                "issuer": "ISO组织",
                "expires_at": current_time + timedelta(days=200)
            },
            {
                "serial": f"OHSAS18001-{unique_suffix}-003",
                "name": f"OHSAS18001安全管理_{unique_suffix}",
                "issuer": "OHSAS组织",
                "expires_at": current_time + timedelta(days=50)
            }
        ]
        
        created_certificates = []
        for cert_data in certificates_data:
            cert = Certificate(
                serial=cert_data["serial"],
                name=cert_data["name"],
                issuer=cert_data["issuer"],
                issued_at=current_time,
                expires_at=cert_data["expires_at"],
                is_active=True
            )
            integration_test_db.add(cert)
            created_certificates.append(cert)
        
        integration_test_db.commit()
        
        # 测试按发证机构搜索
        iso_certificates = integration_test_db.query(Certificate).filter(
            Certificate.issuer == "ISO组织",
            Certificate.serial.contains(unique_suffix)
        ).all()
        
        assert len(iso_certificates) == 2
        for cert in iso_certificates:
            assert cert.issuer == "ISO组织"
        
        # 测试按证书类型搜索（ISO9001）
        iso9001_certificates = integration_test_db.query(Certificate).filter(
            Certificate.serial.contains("ISO9001"),
            Certificate.serial.contains(unique_suffix)
        ).all()
        
        assert len(iso9001_certificates) == 1
        assert "ISO9001质量管理" in iso9001_certificates[0].name
        
        # 测试按有效期搜索（未来150天内过期）
        expiring_soon = integration_test_db.query(Certificate).filter(
            Certificate.expires_at <= current_time + timedelta(days=150),
            Certificate.expires_at > current_time,
            Certificate.serial.contains(unique_suffix)
        ).all()
        
        assert len(expiring_soon) >= 2  # ISO9001(100天) 和 OHSAS18001(50天)
        
    @pytest.mark.integration
    def test_certificate_lifecycle_management(self, integration_test_db: Session):
        """测试证书生命周期管理"""
        unique_suffix = str(uuid.uuid4())[:8]
        current_time = datetime.now()
        
        # 1. 创建证书
        certificate = Certificate(
            serial=f"LIFECYCLE-{unique_suffix}",
            name=f"生命周期测试证书_{unique_suffix}",
            issuer="测试机构",
            issued_at=current_time,
            expires_at=current_time + timedelta(days=365),
            is_active=True
        )
        
        integration_test_db.add(certificate)
        integration_test_db.commit()
        integration_test_db.refresh(certificate)
        
        # 验证证书创建成功
        assert certificate.id is not None
        original_id = certificate.id
        
        # 2. 更新证书信息
        certificate.description = "更新后的证书描述"
        certificate.issuer = "更新后的认证机构"
        integration_test_db.commit()
        integration_test_db.refresh(certificate)
        
        # 验证证书更新
        updated_cert = integration_test_db.query(Certificate).filter(
            Certificate.id == original_id
        ).first()
        
        assert updated_cert.description == "更新后的证书描述"
        assert updated_cert.issuer == "更新后的认证机构"
        
        # 3. 停用证书
        certificate.is_active = False
        integration_test_db.commit()
        integration_test_db.refresh(certificate)
        
        # 验证证书停用
        assert certificate.is_active == False
        
        # 4. 重新激活证书
        certificate.is_active = True
        integration_test_db.commit()
        integration_test_db.refresh(certificate)
        
        # 验证证书重新激活
        assert certificate.is_active == True
        
        # 5. 延期证书
        new_expires_at = certificate.expires_at + timedelta(days=365)
        certificate.expires_at = new_expires_at
        integration_test_db.commit()
        integration_test_db.refresh(certificate)
        
        # 验证证书延期
        assert certificate.expires_at == new_expires_at
        
    @pytest.mark.integration
    def test_certificate_expiry_monitoring(self, integration_test_db: Session):
        """测试证书过期监控"""
        unique_suffix = str(uuid.uuid4())[:8]
        current_time = datetime.now()
        
        # 创建不同过期时间的证书
        test_certificates = [
            # 即将过期（7天后）
            {
                "serial": f"EXPIRING-SOON-{unique_suffix}",
                "name": "即将过期证书",
                "days_until_expiry": 7
            },
            # 需要关注（25天后）
            {
                "serial": f"EXPIRING-MONTH-{unique_suffix}",
                "name": "月内过期证书", 
                "days_until_expiry": 25
            },
            # 还有较长时间（90天后）
            {
                "serial": f"VALID-LONG-{unique_suffix}",
                "name": "长期有效证书",
                "days_until_expiry": 90
            }
        ]
        
        created_certificates = []
        for cert_data in test_certificates:
            cert = Certificate(
                serial=cert_data["serial"],
                name=cert_data["name"],
                issuer="监控测试机构",
                issued_at=current_time,
                expires_at=current_time + timedelta(days=cert_data["days_until_expiry"]),
                is_active=True
            )
            integration_test_db.add(cert)
            created_certificates.append(cert)
        
        integration_test_db.commit()
        
        # 查询即将过期的证书（30天内）
        warning_threshold = current_time + timedelta(days=30)
        expiring_certificates = integration_test_db.query(Certificate).filter(
            Certificate.expires_at <= warning_threshold,
            Certificate.expires_at > current_time,
            Certificate.is_active == True,
            Certificate.serial.contains(unique_suffix)
        ).all()
        
        # 验证查询结果
        assert len(expiring_certificates) == 2  # 7天和25天的证书
        
        for cert in expiring_certificates:
            days_left = (cert.expires_at - current_time).days
            assert days_left <= 30
            assert cert.is_active == True
        
        # 查询紧急过期证书（10天内）
        urgent_threshold = current_time + timedelta(days=10) 
        urgent_certificates = integration_test_db.query(Certificate).filter(
            Certificate.expires_at <= urgent_threshold,
            Certificate.expires_at > current_time,
            Certificate.is_active == True,
            Certificate.serial.contains(unique_suffix)
        ).all()
        
        # 验证紧急过期查询
        assert len(urgent_certificates) == 1  # 只有7天的证书
        assert "EXPIRING-SOON" in urgent_certificates[0].serial


class TestCertificateBusinessLogic:
    """证书业务逻辑测试"""
    
    @pytest.mark.integration 
    def test_certificate_renewal_process(self, integration_test_db: Session):
        """测试证书续期流程"""
        unique_suffix = str(uuid.uuid4())[:8]
        current_time = datetime.now()
        
        # 创建即将过期的证书
        original_certificate = Certificate(
            serial=f"RENEWAL-{unique_suffix}",
            name=f"待续期证书_{unique_suffix}",
            issuer="续期测试机构",
            issued_at=current_time - timedelta(days=330),
            expires_at=current_time + timedelta(days=35),  # 35天后过期
            is_active=True
        )
        
        integration_test_db.add(original_certificate)
        integration_test_db.commit()
        integration_test_db.refresh(original_certificate)
        
        # 模拟续期流程
        def renew_certificate(cert: Certificate, renewal_period_days: int = 365):
            """续期证书"""
            cert.expires_at = cert.expires_at + timedelta(days=renewal_period_days)
            return cert
        
        # 执行续期
        renewed_certificate = renew_certificate(original_certificate, 365)
        integration_test_db.commit()
        integration_test_db.refresh(renewed_certificate)
        
        # 验证续期结果
        expected_expiry = current_time + timedelta(days=35) + timedelta(days=365)
        assert renewed_certificate.expires_at.date() == expected_expiry.date()
        assert renewed_certificate.is_active == True
        
        # 验证续期后证书仍然有效
        def is_certificate_valid(cert: Certificate) -> bool:
            now = datetime.now()
            return cert.is_active and cert.issued_at <= now <= cert.expires_at
        
        assert is_certificate_valid(renewed_certificate) == True
        
    @pytest.mark.integration
    def test_certificate_batch_operations(self, integration_test_db: Session):
        """测试证书批量操作"""
        unique_suffix = str(uuid.uuid4())[:8]
        current_time = datetime.now()
        
        # 创建一批证书
        batch_certificates = []
        for i in range(5):
            cert = Certificate(
                serial=f"BATCH-{unique_suffix}-{i:03d}",
                name=f"批量操作证书_{unique_suffix}_{i}",
                issuer="批量测试机构",
                issued_at=current_time,
                expires_at=current_time + timedelta(days=30 + i * 10),
                is_active=True
            )
            batch_certificates.append(cert)
        
        # 批量添加证书
        integration_test_db.add_all(batch_certificates)
        integration_test_db.commit()
        
        # 验证批量创建
        created_certificates = integration_test_db.query(Certificate).filter(
            Certificate.serial.contains(f"BATCH-{unique_suffix}")
        ).all()
        
        assert len(created_certificates) == 5
        
        # 批量更新操作：更新发证机构
        integration_test_db.query(Certificate).filter(
            Certificate.serial.contains(f"BATCH-{unique_suffix}")
        ).update({Certificate.issuer: "更新后的批量测试机构"})
        integration_test_db.commit()
        
        # 验证批量更新
        updated_certificates = integration_test_db.query(Certificate).filter(
            Certificate.serial.contains(f"BATCH-{unique_suffix}")
        ).all()
        
        for cert in updated_certificates:
            assert cert.issuer == "更新后的批量测试机构"
        
        # 批量停用操作
        integration_test_db.query(Certificate).filter(
            Certificate.serial.contains(f"BATCH-{unique_suffix}")
        ).update({Certificate.is_active: False})
        integration_test_db.commit()
        
        # 验证批量停用
        deactivated_certificates = integration_test_db.query(Certificate).filter(
            Certificate.serial.contains(f"BATCH-{unique_suffix}")
        ).all()
        
        for cert in deactivated_certificates:
            assert cert.is_active == False