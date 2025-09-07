from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_session
import app.models as models
from app.api import schemas

router = APIRouter()


@router.post("/products", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_session)):
    existing = db.query(models.Product).filter(models.Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="sku already exists")
    product = models.Product(name=payload.name, sku=payload.sku, description=payload.description)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products", response_model=List[schemas.ProductRead])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
def get_product(product_id: int, db: Session = Depends(get_session)):
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_session)):
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    db.delete(product)
    db.commit()
    return None
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
