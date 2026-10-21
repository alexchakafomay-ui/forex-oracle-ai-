import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from src.config import GROQ_API_KEY

# Menggunakan ecocal sebagai pengganti forexfactory
try:
    from ecocal import Calendar
    HAS_ECOCAL = True
except ImportError:
    HAS_ECOCAL = False

def get_high_impact_events(currencies=("USD", "EUR", "GBP", "JPY")):
    if not HAS_ECOCAL:
        return []
    
    today = datetime.now(timezone.utc).date()
    tomorrow = today + timedelta(days=1)
    
    try:
        ec = Calendar(
            startHorizon=str(today),
            endHorizon=str(tomorrow),
            withDetails=True,
            preBuildCalendar=True
        )
        df = ec.getDataFrame()
        
        # Filter berdasarkan mata uang dan dampak 'High'
        df = df[df['currency'].isin(currencies)]
        df = df[df['impact'].str.lower() == 'high']
        
        # Filter untuk 2 jam ke depan
        now = pd.Timestamp.now(tz="UTC")
        df['datetime_utc'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str)).dt.tz_localize('UTC')
        future = df[(df["datetime_utc"] > now) & (df["datetime_utc"] < now + pd.Timedelta(hours=2))]
        
        return future[["datetime_utc", "currency", "event"]].rename(columns={"event": "title"}).to_dict("records")
    except Exception as e:
        print(f"[WARN] Gagal mengambil kalender ecocal: {e}")
        return []

def llm_sentiment(headlines: str) -> float:
    if not GROQ_API_KEY or not headlines:
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
