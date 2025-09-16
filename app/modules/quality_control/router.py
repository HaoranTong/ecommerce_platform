"""
质量控制模块 API 路由

此模块定义了质量控制相关的API端点，包括：
- 证书管理接口
- 质量检验接口
- 合规性检查接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from .models import Certificate
from .schemas import CertificateRead, CertificateCreate

router = APIRouter()


# ============ 证书管理接口 ============

@router.post("/quality-control/certificates", response_model=CertificateRead, status_code=status.HTTP_201_CREATED)
def create_certificate(payload: CertificateCreate, db: Session = Depends(get_db)):
    """创建新证书"""
    existing = db.query(Certificate).filter(Certificate.serial == payload.serial).first()
    if existing:
        raise HTTPException(status_code=400, detail="证书序列号已存在")
    
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


@router.get("/quality-control/certificates", response_model=List[CertificateRead])
def list_certificates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取证书列表"""
    certs = db.query(Certificate).offset(skip).limit(limit).all()
    return certs


@router.get("/quality-control/certificates/{cert_id}", response_model=CertificateRead)
def get_certificate(cert_id: int, db: Session = Depends(get_db)):
    """获取指定证书信息"""
    cert = db.query(Certificate).get(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="证书不存在")
    return cert


@router.delete("/quality-control/certificates/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certificate(cert_id: int, db: Session = Depends(get_db)):
    """删除证书"""
    cert = db.query(Certificate).get(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="证书不存在")
    db.delete(cert)
    db.commit()
    return None
