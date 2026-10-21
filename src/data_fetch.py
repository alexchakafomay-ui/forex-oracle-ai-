import requests, time, json, os
from src.config import TWELVE_DATA_API_KEY, TIMEFRAMES

CACHE_DIR = "/tmp/fx_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_path(symbol, interval):
    safe = symbol.replace("/", "")
    return f"{CACHE_DIR}/{safe}_{interval}.json"

def _is_fresh(path, max_age_sec):
    if not os.path.exists(path):
        return False
    return (time.time() - os.path.getmtime(path)) < max_age_sec

def fetch_ohlc(symbol, interval, outputsize=200, max_age_sec=300):
    path = _cache_path(symbol, interval)
    if _is_fresh(path, max_age_sec):
        with open(path) as f:
            return json.load(f)

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": TWELVE_DATA_API_KEY,
        "format": "JSON",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "values" not in data:
            raise ValueError(f"API error: {data}")
        with open(path, "w") as f:
            json.dump(data["values"], f)
        return data["values"]
    except Exception as e:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        raise RuntimeError(f"Gagal fetch {symbol} {interval}: {e}")

def fetch_multi_tf(symbol):
    ages = {"1min": 300, "5min": 300, "15min": 900, "1h": 3600, "4h": 14400, "1day": 86400}
    result = {}
    for tf in TIMEFRAMES:
        result[tf] = fetch_ohlc(symbol, tf, max_age_sec=ages[tf])
        time.sleep(0.2)
    return result
