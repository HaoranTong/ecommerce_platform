from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_session
import app.models as models

router = APIRouter()


@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: dict, db: Session = Depends(get_session)):
    # minimal scaffold
    product = models.Product(name=payload.get('name'), sku=payload.get('sku'), description=payload.get('description'))
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"id": product.id, "name": product.name, "sku": product.sku}


@router.get("/products", response_model=List[dict])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    prods = db.query(models.Product).offset(skip).limit(limit).all()
    return [ {"id": p.id, "name": p.name, "sku": p.sku} for p in prods ]
