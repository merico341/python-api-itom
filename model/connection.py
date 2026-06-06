from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base

if TYPE_CHECKING:
    from model.device import Device

class Connection(Base):
    __tablename__ = "connection"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True) #INTEGER PK NOT NULL AUTO
    type: Mapped[str] = mapped_column(String(50), nullable=False) #VARCHAR NOT NULL
    source_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"), nullable=False) #VARCHAR FK NOT NULL
    destination_id: Mapped[int] = mapped_column(ForeignKey("device.id", ondelete="CASCADE"), nullable=False) #VARCHAR FK NOT NULL 
    
    source: Mapped["Device"] = relationship("Device", foreign_keys=[source_id], back_populates="connections_as_source") #Python relationship
    destination: Mapped["Device"] = relationship("Device", foreign_keys=[destination_id], back_populates="connections_as_destination") #Python relationship

    def __repr__(self):
        return f"Connection(id={self.id}, type={self.type!r}, source_id={self.source_id}, destination_id={self.destination_id})"