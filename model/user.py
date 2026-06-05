from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base

if TYPE_CHECKING:
    from model.device import Device

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True) #INTEGER PK NOT NULL AUTO
    name: Mapped[str] = mapped_column(String(50), nullable=False) #VARCHAR NOT NULL
    email: Mapped[str] = mapped_column(String(30), nullable=False) #VARCHAR NOT NULL
    departament: Mapped[Optional[str]] = mapped_column(String(30)) #VARCHAR NULL

    devices: Mapped[List["Device"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r}, departament={self.departament!r})"