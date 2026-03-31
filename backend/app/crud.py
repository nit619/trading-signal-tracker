from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
from .binance import get_live_price

def get_signal(db: Session, signal_id: int):
    return db.query(models.Signal).filter(models.Signal.id == signal_id).first()


def get_signals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Signal).offset(skip).limit(limit).all()


def create_signal(db: Session, signal: schemas.SignalCreate):
    db_signal = models.Signal(**signal.dict())
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal


def delete_signal(db: Session, signal_id: int):
    obj = get_signal(db, signal_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj


def _calculate_roi(signal: models.Signal, current_price: float) -> float:
    if signal.direction == "BUY":
        return (current_price - signal.entry_price) / signal.entry_price * 100
    else:  # SELL
        return (signal.entry_price - current_price) / signal.entry_price * 100


def update_signal_status(db: Session, signal_id: int):
    """
    Re‑evaluate a signal against the live Binance price and expiry.
    Called by the optional /refresh endpoint and also when we fetch
    signals for the dashboard.
    """
    signal = get_signal(db, signal_id)
    if not signal or signal.status in (
        models.SignalStatus.TARGET_HIT,
        models.SignalStatus.STOPLOSS_HIT,
        models.SignalStatus.EXPIRED,
    ):
        # Terminal states never change again (Req 12)
        return signal

    now = datetime.utcnow()
    # 1️⃣ Expiry check (Req 7)
    if now > signal.expiry_time.replace(tzinfo=None):
        signal.status = models.SignalStatus.EXPIRED
        signal.realized_roi = _calculate_roi(signal, signal.entry_price)
        db.commit()
        db.refresh(signal)
        return signal

    # 2️⃣ Live price from Binance (Req 5)
    price = get_live_price(signal.symbol)

    # 3️⃣ Status logic (Req 6)
    if signal.direction == "BUY":
        if price >= signal.target_price:
            signal.status = models.SignalStatus.TARGET_HIT
        elif price <= signal.stop_loss:
            signal.status = models.SignalStatus.STOPLOSS_HIT
    else:  # SELL
        if price <= signal.target_price:
            signal.status = models.SignalStatus.TARGET_HIT
        elif price >= signal.stop_loss:
            signal.status = models.SignalStatus.STOPLOSS_HIT

    # 4️⃣ Store ROI when we hit a terminal state (Req 8)
    if signal.status in (
        models.SignalStatus.TARGET_HIT,
        models.SignalStatus.STOPLOSS_HIT,
        models.SignalStatus.EXPIRED,
    ):
        signal.realized_roi = _calculate_roi(signal, price)

    db.commit()
    db.refresh(signal)
    return signal