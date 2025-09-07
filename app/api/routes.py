from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_session
import app.models as models
from app.api import schemas

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_session)):
    # check uniqueness
    existing = db.query(models.User).filter((models.User.username == payload.username) | (models.User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="username or email already exists")
    user = models.User(username=payload.username, email=payload.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=List[schemas.UserRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: Session = Depends(get_session)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_session)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    db.delete(user)
    db.commit()
    return None

