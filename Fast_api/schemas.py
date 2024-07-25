from pydantic import BaseModel

class LoginSchema(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class BlogSchema(BaseModel):
    title: str
    body: str
    user_id: int

    class Config:
        from_attributes = True

class BlogResponseSchema(BaseModel):
    id: int
    title: str
    body: str
    user_id: int

    class Config:
        from_attributes = True

class BlogResponseWithUserSchema(BaseModel):
    id: int
    title: str
    body: str
    user: UserResponseSchema

    class Config:
        from_attributes = True

class UserCreateSchema(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        from_attributes = True
