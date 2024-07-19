from pydantic import BaseModel

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

    class Config:
        from_attributes = True


