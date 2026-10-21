from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    role: str = "USER"

class UserOut(UserBase):
    id: int
    role: str
    status: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int

class ProductOut(ProductBase):
    id: int
    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    product_id: int
    quantity: int

class OrderOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total: float
    status: str
    created_at: datetime
    product: ProductOut
    
    class Config:
        orm_mode = True
