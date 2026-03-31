from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import crud, models, schemas, database
from ..binance import get_live_price

router = APIRouter(prefix="/api/signals", tags=["signals"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.SignalOut, status_code=status.HTTP_201_CREATED)
def create_signal(
    signal: schemas.SignalCreate, db: Session = Depends(get_db)
):
    """Create a new signal – validation is done by the Pydantic model."""
    return crud.create_signal(db=db, signal=signal)


@router.get("/", response_model=List[schemas.SignalOut])
def read_signals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Return all signals, enriched with live price and time‑left."""
    signals = crud.get_signals(db, skip=skip, limit=limit)
    out: List[schemas.SignalOut] = []
    for s in signals:
        price = get_live_price(s.symbol)
        time_left = int((s.expiry_time - datetime.utcnow()).total_seconds())
        out.append(
            schemas.SignalOut(
                **s.__dict__,
                current_price=price,
                time_left_seconds=max(time_left, 0),
            )
        )
    return out


@router.get("/{signal_id}", response_model=schemas.SignalOut)
def read_signal(signal_id: int, db: Session = Depends(get_db)):
    """Return a single signal, enriched."""
    signal = crud.get_signal(db, signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    price = get_live_price(signal.symbol)
    time_left = int((signal.expiry_time - datetime.utcnow()).total_seconds())
    return schemas.SignalOut(
        **signal.__dict__,
        current_price=price,
        time_left_seconds=max(time_left, 0),
    )


@router.delete("/{signal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_signal(signal_id: int, db: Session = Depends(get_db)):
    """Delete a signal – returns 204 on success, 404 if not found."""
    obj = crud.delete_signal(db, signal_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Signal not found")
    return None


# Optional endpoint – handy for manual testing or forcing a refresh
@router.post("/{signal_id}/refresh", response_model=schemas.SignalOut)
def refresh_signal(signal_id: int, db: Session = Depends(get_db)):
    updated = crud.update_signal_status(db, signal_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Signal not found")
    price = get_live_price(updated.symbol)
    time_left = int((updated.expiry_time - datetime.utcnow()).total_seconds())
    return schemas.SignalOut(
        **updated.__dict__,
        current_price=price,
        time_left_seconds=max(time_left, 0),
    )