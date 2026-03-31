from unittest.mock import Base

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
import enum
from .database import Base

class SignalStatus(str, enum.Enum):
    OPEN = "OPEN"
    TARGET_HIT = "TARGET_HIT"
    STOPLOSS_HIT = "STOPLOSS_HIT"
    EXPIRED = "EXPIRED"


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)          # e.g., BTCUSDT
    direction = Column(String)                   # BUY / SELL
    entry_price = Column(Float)
    stop_loss = Column(Float)
    target_price = Column(Float)
    entry_time = Column(DateTime(timezone=True))
    expiry_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(SignalStatus), default=SignalStatus.OPEN)
    realized_roi = Column(Float, nullable=True)