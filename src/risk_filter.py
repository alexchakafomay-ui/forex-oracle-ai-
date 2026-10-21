from datetime import datetime, timedelta, timezone
import pytz

JAKARTA = pytz.timezone("Asia/Jakarta")
COOLDOWN = {}
COOLDOWN_MIN = 30

def is_session_active():
    now = datetime.now(JAKARTA)
    if now.weekday() >= 5:
        return False
    return 13 <= now.hour <= 23

def spread_ok(spread_pips):
    return spread_pips < 1.0

def cooldown_ok(pair):
    last = COOLDOWN.get(pair)
    if last is None:
        return True
    return (datetime.now(timezone.utc) - last) > timedelta(minutes=COOLDOWN_MIN)

def mark_sent(pair):
    COOLDOWN[pair] = datetime.now(timezone.utc)
