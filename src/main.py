import traceback
from datetime import datetime
import pytz
from itertools import islice

from src.config import PAIR_POOL
from src.data_fetch import fetch_multi_tf
from src.feature_engineering import to_dataframe, add_technical, add_smc, detect_regime
from src.model_inference import ensemble_predict
from src.news_sentiment import get_high_impact_events, llm_sentiment
from src.scoring_engine import build_score
from src.risk_filter import is_session_active, spread_ok, cooldown_ok, mark_sent
from src.telegram_sender import format_signal, send_telegram
from src.logger import log_signal

JAKARTA = pytz.timezone("Asia/Jakarta")

def pick_pairs(pool, n=4):
    minute_slot = datetime.now(JAKARTA).minute // 5
    start = (minute_slot * n) % len(pool)
    return list(islice((pool * 2), start, start + n))

def compute_levels(df_m5, direction):
    last = df_m5.iloc[-1]
    atr = float(last["atr"])
    entry = float(last["close"])
    sl_dist = max(5e-4, min(1.5e-3, 1.2 * atr))
    if direction == "BUY":
        sl = entry - sl_dist
        tp1 = entry + sl_dist * 1.0
        tp2 = entry + sl_dist * 2.0
        tp3 = entry + sl_dist * 3.5 
    else:
        sl = entry + sl_dist
1        tp1 = entry - sl_dist *.0
        tp2 = entry - sl_dist * 2.0
        tp3 = entry - sl_dist * 3.5
    pip = 0.0001
    return {
        "entry": round(entry, 5), "sl": round(sl, 5),
        "tp1": round(tp1, 5), "tp2": round(tp2, 5), "tp3": round(tp3, 5),
        "sl_pips": round(abs(entry - sl) / pip, 1),
        "tp1_pips": round(abs(tp1 - entry) / pip, 1),
        "tp2_pips": round(abs(tp2 - entry) / pip, 1),
        "tp3_pips": round(abs(tp3 - entry) / pip, 1),
    }

def run():
    if not is_session_active():
        print("[SKIP] Di luar sesi aktif.")
        return

    pairs = pick_pairs(PAIR_POOL, n=4)
    print(f"[RUN] {datetime.now(JAKARTA):%Y-%m-%d %H:%M WIB} | Pairs: {pairs}")

    try:
        events = get_high_impact_events()
        next_event = events[0]["title"] if events else "Tidak ada"
        news_score = llm_sentiment(str(events)) if events else 0.0
    except Exception as e:
        print(f"[WARN] News fetch gagal: {e}")
        next_event, news_score = "N/A", 0.0

    for pair in pairs:
        try:
            if not cooldown_ok(pair):
                continue

            raw = fetch_multi_tf(pair)
            df_m5 = add_smc(add_technical(to_dataframe(raw["5min"])))
            df_h1 = add_technical(to_dataframe(raw["1h"]))
            if df_m5.empty or df_h1.empty:
                continue

            probs = ensemble_predict(df_m5)
            regime = detect_regime(df_m5)
            last5, last1h = df_m5.iloc[-1], df_h1.iloc[-1]
            
            trend_flags = {"ema_bull": last1h["ema50"] > last1h["ema200"], "ema_bear": last1h["ema50"] < last1h["ema200"]}
            smc_flags = {
                "bullish_ob": bool(last5["smc_bullish_ob"]), "bearish_ob": bool(last5["smc_bearish_ob"]),
                "bos_bull": bool(last5["smc_bos_bull"]), "bos_bear": bool(last5["smc_bos_bear"]),
                "rsi": float(last5["rsi"]),
            }

            score = build_score(probs, regime, news_score, smc_flags, trend_flags)
            if score is None or score["confidence"] < 65:
                continue

            spread_pips = 0.3 if not events else 1.5
            if not spread_ok(spread_pips):
                continue

            levels = compute_levels(df_m5, score["direction"])

            s = {
                "pair": pair, "direction": score["direction"], "confidence": score["confidence"],
                "tf": "M5", "time_wib": datetime.now(JAKARTA).strftime("%Y-%m-%d %H:%M"),
                "mode": "SCALPING (Zero Spread)", "risk_pct": 0.5,
                "reasons": score["reasons"], "smc_bullish_ob": smc_flags["bullish_ob"],
                "smc_bos_bull": smc_flags["bos_bull"], "news_label": f"skor {news_score:+.2f}",
                "next_news": next_event, "p_bull": int(probs["bull"] * 100),
                "p_bear": int(probs["bear"] * 100), "p_side": int(probs["side"] * 100),
                "regime": regime, "risk_level": "Medium" if score["confidence"] < 80 else "Low",
                "note": "Eksekusi cepat, spread < 1 pip.", **levels,
            }

            send_telegram(format_signal(s))
            log_signal(s)
            mark_sent(pair)
            print(f"[SENT] {pair} {score['direction']}")

        except Exception as e:
            print(f"[ERR] {pair}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    run()
