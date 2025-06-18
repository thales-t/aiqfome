from pydantic import AnyUrl, BaseModel, EmailStr, Field
from typing import Optional, List

# --- Schemas para Produtos (dados da API externa) ---
class ProductReview(BaseModel):
    rate: float
    count: int

class Product(BaseModel):
    id: int
    title: str
    price: float
    description: str
    category: str
    image: AnyUrl
    review: Optional[ProductReview] = Field(alias='rating')

    class Config:
        populate_by_name = True 

# --- Schemas para Favoritos ---
class FavoriteProductCreate(BaseModel):
    product_id: int

# --- Schemas para Clientes ---
class ClientBase(BaseModel):
    name: str
    email: EmailStr

class ClientCreate(ClientBase):
    password: str = Field(min_length=6)

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class Client(ClientBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Schemas para Autenticação ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# --- Schemas para Hello ---
class Message(BaseModel):
    message: str
