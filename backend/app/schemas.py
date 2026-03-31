from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from .models import SignalStatus

class SignalBase(BaseModel):
    symbol: str = Field(..., example="BTCUSDT")
    direction: str = Field(..., pattern="^(BUY|SELL)$")
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    target_price: float = Field(..., gt=0)
    entry_time: datetime
    expiry_time: datetime

    # ---- Validation rules (Req 3.2) ----
    @validator("stop_loss")
    def sl_check(cls, v, values):
        if values.get("direction") == "BUY":
            if not (v < values.get("entry_price", 0)):
                raise ValueError("For BUY, stop loss must be < entry price")
        else:  # SELL
            if not (v > values.get("entry_price", 0)):
                raise ValueError("For SELL, stop loss must be > entry price")
        return v

    @validator("target_price")
    def tp_check(cls, v, values):
        if values.get("direction") == "BUY":
            if not (v > values.get("entry_price", 0)):
                raise ValueError("For BUY, target price must be > entry price")
        else:
            if not (v < values.get("entry_price", 0)):
                raise ValueError("For SELL, target price must be < entry price")
        return v

    @validator("expiry_time")
    def expiry_after_entry(cls, v, values):
        if v <= values.get("entry_time"):
            raise ValueError("Expiry time must be after entry time")
        return v


class SignalCreate(SignalBase):
    pass


class SignalOut(SignalBase):
    id: int
    created_at: datetime
    status: SignalStatus
    realized_roi: Optional[float] = None
    # Filled by the endpoint for the frontend
    current_price: Optional[float] = None
    time_left_seconds: Optional[int] = None