import requests
from fastapi import HTTPException

BINANCE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"

def get_live_price(symbol: str) -> float:
    """
    Calls Binance public ticker/price endpoint (no API key needed).
    Raises HTTPException 502 if the request fails or symbol is invalid.
    """
    try:
        resp = requests.get(
            BINANCE_PRICE_URL,
            params={"symbol": symbol.upper()},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        return float(data["price"])
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch price for {symbol}: {exc}",
        ) from exc