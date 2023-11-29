from decimal import Decimal
from typing import List
from pydantic import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class UserSchema(BaseModel):
    username: Decimal
    password: str


class User(Base):
    __tablename__ = 'users'
    schema = UserSchema    
    
    username: Mapped[str] = mapped_column(String(128), unique=True)
    password: Mapped[str] = mapped_column(String(256))
    refresh_tokens: Mapped[List["RefreshTokens"]] = relationship(back_populates="user", lazy='select')