from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    favorites = relationship("FavoriteProduct", back_populates="owner", cascade="all, delete-orphan")


class FavoriteProduct(Base):
    __tablename__ = "favorite_products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    owner = relationship("Client", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("client_id", "product_id", name="unic_client_product"),
    )