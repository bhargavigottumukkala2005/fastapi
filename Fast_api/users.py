from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import UserCreateSchema, UserResponseSchema
from model import User
from database import get_db
from hashing import hash_password

router = APIRouter()

@router.post("/", response_model=UserResponseSchema, tags=["Users"])
def create_user(request: UserCreateSchema, db: Session = Depends(get_db)):
    try:
        hashed_password = hash_password(request.password)
        new_user = User(name=request.name, email=request.email, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[UserResponseSchema], tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=UserResponseSchema, tags=["Users"])
def show_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{id}", response_model=UserResponseSchema, tags=["Users"])
def update_user(id: int, request: UserCreateSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = request.name
    user.email = request.email
    user.password = hash_password(request.password)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{id}", response_model=UserResponseSchema, tags=["Users"])
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user
