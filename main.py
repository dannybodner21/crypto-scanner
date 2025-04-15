from fastapi import FastAPI
import requests
from supabase import create_client, Client
import os
from datetime import datetime

app = FastAPI()

# Supabase credentials from Render env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/update")
def update_metrics():
    res = requests.get("https://api.coingecko.com/api/v3/coins/markets", params={
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 150,
        "page": 1,
        "price_change_percentage": "1h,24h"
    })
    data = res.json()

    rows = []
    now = datetime.utcnow().isoformat()

    for coin in data:
        rows.append({
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "price": coin["current_price"],
            "change_5m": None,  # Not in CoinGecko
            "change_1h": coin.get("price_change_percentage_1h_in_currency"),
            "change_24h": coin.get("price_change_percentage_24h_in_currency"),
            "volume": coin["total_volume"],
            "avg_volume": None,  # Could compute later
            "rsi": None,
            "macd": None,
            "scanner_flags": None,
            "timestamp": now
        })

    supabase.table("scanned_metrics").insert(rows).execute()
    return {"inserted": len(rows)}
