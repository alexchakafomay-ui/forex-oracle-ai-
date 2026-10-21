import csv, os
from datetime import datetime

LOG_PATH = "logs/signals.csv"
FIELDS = ["timestamp", "pair", "direction", "confidence", "entry", "sl", "tp1",
          "result", "pips", "rr", "regime"]

def log_signal(s):
    os.makedirs("logs", exist_ok=True)
    new = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: s.get(k, "") for k in FIELDS})
