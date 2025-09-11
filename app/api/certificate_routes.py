from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_session
import app.models as models
from app.api import schemas

router = APIRouter()


@router.post("/api/certificates", response_model=schemas.CertificateRead, status_code=status.HTTP_201_CREATED)
def create_certificate(payload: schemas.CertificateCreate, db: Session = Depends(get_session)):
    existing = db.query(models.Certificate).filter(models.Certificate.serial == payload.serial).first()
    if existing:
        raise HTTPException(status_code=400, detail="serial already exists")
    cert = models.Certificate(name=payload.name, issuer=payload.issuer, serial=payload.serial, description=payload.description)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@router.get("/api/certificates", response_model=List[schemas.CertificateRead])
def list_certificates(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    certs = db.query(models.Certificate).offset(skip).limit(limit).all()
    return certs


@router.get("/api/certificates/{cert_id}", response_model=schemas.CertificateRead)
def get_certificate(cert_id: int, db: Session = Depends(get_session)):
    cert = db.query(models.Certificate).get(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="certificate not found")
    return cert


@router.delete("/api/certificates/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certificate(cert_id: int, db: Session = Depends(get_session)):
    cert = db.query(models.Certificate).get(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="certificate not found")
    db.delete(cert)
    db.commit()
    return None
