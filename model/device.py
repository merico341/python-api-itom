from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base

if TYPE_CHECKING:
    from model.user import User

class Device(Base):
    __tablename__ = "device"
    
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)  #INTEGER PK NOT NULL AUTO
    name: Mapped[str] = mapped_column(String(30), nullable=False) #VARCHAR NOT NULL 
    type: Mapped[str] = mapped_column(String(30), nullable=False) #VARCHAR NOT NULL 

    ip: Mapped[Optional[str]] = mapped_column(String(16)) #VARCHAR
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id", ondelete="SET NULL")) #FK 

    user: Mapped[Optional["User"]] = relationship(back_populates="devices") #Python relationship

    def __repr__(self): 
        return f"Device(id={self.id}, name={self.name!r}, type={self.type!r}, ip={self.ip!r}, user_id={self.user_id})"