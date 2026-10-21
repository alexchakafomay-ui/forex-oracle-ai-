import forexfactory as ff
import requests
import os
import pandas as pd
from src.config import GROQ_API_KEY

def get_high_impact_events(currencies=("USD", "EUR", "GBP", "JPY")):
    df = ff.read(currencies=list(currencies), impacts=["high"])
    now = pd.Timestamp.now(tz="UTC")
    future = df[(df["datetime_utc"] > now) & (df["datetime_utc"] < now + pd.Timedelta(hours=2))]
    return future[["datetime_utc", "currency", "title"]].to_dict("records")

def llm_sentiment(headlines: str) -> float:
    if not GROQ_API_KEY:
        return 0.0
    prompt = f"Berita forex berikut. Beri skor sentimen -1.0 sampai +1.0 untuk USD. Jawab hanya angka.\n{headlines}"
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 10,
            },
            timeout=10,
        )
        return float(r.json()["choices"][0]["message"]["content"].strip())
    except Exception:
        return 0.0
