from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import logging

from schemas import BlogSchema, BlogResponseSchema, UserCreateSchema, UserResponseSchema
from model import Blog, User
from database import get_db
from hashing import hash_password, verify_password

app = FastAPI()

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logging.error(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.get("/blogs", response_model=list[BlogResponseSchema])
def get_blogs(db: Session = Depends(get_db)):
    try:
        blogs = db.query(Blog).all()
        return blogs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/blogs", response_model=BlogResponseSchema)
def create_blog(request: BlogSchema, db: Session = Depends(get_db)):
    try:
        new_blog = Blog(title=request.title, body=request.body)
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        return new_blog
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/blogs/{blog_id}", response_model=BlogResponseSchema)
def update_blog(blog_id: int, blog: BlogSchema, db: Session = Depends(get_db)):
    db_blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    db_blog.title = blog.title
    db_blog.body = blog.body
    db.commit()
    db.refresh(db_blog)
    return db_blog

@app.delete("/blogs/{blog_id}", response_model=BlogResponseSchema)
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    db_blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(db_blog)
    db.commit()
    return db_blog

@app.post("/users", response_model=UserResponseSchema)
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

@app.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"message": "Login successful"}






