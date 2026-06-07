from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base
from util.incident_enum_util import IncidentPriority, IncidentState

if TYPE_CHECKING:
    from model.user import User
    from model.device import Device

class Incident(Base):
    __tablename__ = "incident"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False) 

    state: Mapped[IncidentState] = mapped_column(Enum(IncidentState), default=IncidentState.NEW, nullable=False)
    priority: Mapped[IncidentPriority] = mapped_column(Enum(IncidentPriority), default=IncidentPriority.MODERATE, nullable=False) 
    
    caller_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="RESTRICT"), nullable=False) 
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    description: Mapped[Optional[str]] = mapped_column(String(500))
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("device.id", ondelete="SET NULL"))

    caller: Mapped["User"] = relationship()
    device: Mapped[Optional["Device"]] = relationship()

    def __repr__(self):
        desc_part = f", description={self.description!r}" if self.description else ""
        device_part = f", device={self.device_id!r}" if self.device_id else ""
        
        return f"Incident(number={self.number!r}, title={self.title!r}, state={self.state.value!r}, priority={self.priority.value!r}, caller={self.caller_id!r}{desc_part}{device_part}, update_at={self.updated_at})"