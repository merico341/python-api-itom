from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base
from util.log_enum_util import LogStatus, LogOperation

if TYPE_CHECKING:
    from model.user import User
    from model.device import Device

class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    date_hour: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    operation: Mapped[LogOperation] = mapped_column(Enum(LogOperation), nullable=False) 
    status: Mapped[LogStatus] = mapped_column(Enum(LogStatus), nullable=False)    
    
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("device.id", ondelete="SET NULL"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    description: Mapped[Optional[str]] = mapped_column(String(200))
    
    device: Mapped[Optional["Device"]] = relationship()
    user: Mapped[Optional["User"]] = relationship()

    def __repr__(self):
        desc_part = f", description={self.description!r}" if self.description else ""
        
        op_val = self.operation.value if hasattr(self.operation, 'value') else self.operation
        st_val = self.status.value if hasattr(self.status, 'value') else self.status

        if self.device_id is None:
            return f"Log(id={self.id}, user_id={self.user_id}, operation={op_val!r}, status={st_val!r}, date_hour={self.date_hour}{desc_part})"
        else:
            return f"Log(id={self.id}, device_id={self.device_id}, operation={op_val!r}, status={st_val!r}, date_hour={self.date_hour}{desc_part})"