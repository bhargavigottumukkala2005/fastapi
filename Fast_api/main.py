from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

DATABASE_URL = "postgresql://postgres:12345@localhost/test"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    body = Column(String, index=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

class BlogSchema(BaseModel):
    title: str
    body: str

    class Config:
        from_attributes = True

class BlogResponseSchema(BaseModel):
    id: int
    title: str
    body: str

    class Config:
        from_attributes = True

class UserCreateSchema(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        from_attributes = True

class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: str
    password: str

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
        new_user = User(name=request.name, email=request.email, password=request.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
