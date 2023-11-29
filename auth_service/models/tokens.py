from sqlalchemy import ForeignKey, String
from models.base import Base
from sqlalchemy.orm import Mapped, relationship, mapped_column

from models.user import User


class RefreshTokens(Base):
    __tablename__ = 'user_refresh_tokens'
    
    user_id: Mapped[int] = mapped_column(ForeignKey(User.get_primary_key_path()))
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
    token: Mapped[str] = mapped_column(String(256), unique=True)