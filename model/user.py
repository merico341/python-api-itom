from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from model.base import Base

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True) #INTEGER PK NOT NULL AUTO
    name: Mapped[str] = mapped_column(String(50), nullable=False) #VARCHAR NOT NULL
    email: Mapped[str] = mapped_column(String(30), nullable=False) #VARCHAR NOT NULL
    departament: Mapped[Optional[str]] = mapped_column(String(30)) #VARCHAR NULL

    def __repr__(self):
        # O '!r' chama o repr() da variável, colocando aspas nas strings automaticamente
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r}, departament={self.departament!r})"