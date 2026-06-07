from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin

from model.base import Base

if TYPE_CHECKING:
    from model.device import Device

class User(Base, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True) #INTEGER PK NOT NULL AUTO
    name: Mapped[str] = mapped_column(String(100), nullable=False) #VARCHAR NOT NULL
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True) #VARCHAR NOT NULL UNIQUE
    password: Mapped[str] = mapped_column(String(255), nullable=False) #VARCHAR NOT NULL
    role: Mapped[str] = mapped_column(String(20), default="USER", nullable=False) #VARCHAR NOT NULL

    devices: Mapped[List["Device"]] = relationship(back_populates="user") # Python Relationship

    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r}, role={self.role!r}, password={self.password!r})"