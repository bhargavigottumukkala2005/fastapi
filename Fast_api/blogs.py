from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import BlogSchema, BlogResponseSchema, BlogResponseWithUserSchema
from model import Blog
from database import get_db

router = APIRouter()

@router.get("/", response_model=list[BlogResponseSchema])
def get_blogs(db: Session = Depends(get_db)):
    try:
        blogs = db.query(Blog).all()
        return blogs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=BlogResponseSchema)
def create_blog(request: BlogSchema, db: Session = Depends(get_db)):
    try:
        new_blog = Blog(title=request.title, body=request.body, user_id=request.user_id)
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        return new_blog
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=BlogResponseWithUserSchema)
def get_blog_by_id(id: int, db: Session = Depends(get_db)):
    try:
        blog = db.query(Blog).filter(Blog.id == id).first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        return blog
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=BlogResponseSchema)
def update_blog(id: int, blog: BlogSchema, db: Session = Depends(get_db)):
    db_blog = db.query(Blog).filter(Blog.id == id).first()
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    db_blog.title = blog.title
    db_blog.body = blog.body
    db_blog.user_id = blog.user_id
    db.commit()
    db.refresh(db_blog)
    return db_blog

@router.delete("/{id}", response_model=BlogResponseSchema)
def delete_blog(id: int, db: Session = Depends(get_db)):
    db_blog = db.query(Blog).filter(Blog.id == id).first()
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(db_blog)
    db.commit()
    return db_blog
