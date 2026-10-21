def build_score(probs, regime, news_score, smc_flags, trend_flags):
    votes = {"buy": 0, "sell": 0}
    reasons = []

    if probs["bull"] > probs["bear"] and probs["bull"] > 0.55:
        votes["buy"] += 1
        reasons.append("Model ensemble bullish")
    elif probs["bear"] > probs["bull"] and probs["bear"] > 0.55:
        votes["sell"] += 1
        reasons.append("Model ensemble bearish")

    if trend_flags["ema_bull"]:
        votes["buy"] += 1
        reasons.append("EMA50 > EMA200")
    if trend_flags["ema_bear"]:
        votes["sell"] += 1
        reasons.append("EMA50 < EMA200")

    if smc_flags["bullish_ob"] or smc_flags["bos_bull"]:
        votes["buy"] += 1
        reasons.append("SMC bullish (OB/BOS)")
    if smc_flags["bearish_ob"] or smc_flags["bos_bear"]:
        votes["sell"] += 1
        reasons.append("SMC bearish (OB/BOS)")

    if smc_flags["rsi"] < 35:
        votes["buy"] += 1
        reasons.append("RSI oversold")
    if smc_flags["rsi"] > 65:
        votes["sell"] += 1
        reasons.append("RSI overbought")

    if news_score > 0.3:
        votes["buy"] += 1
        reasons.append("Sentimen berita bullish")
    elif news_score < -0.3:
        votes["sell"] += 1
        reasons.append("Sentimen berita bearish")

    total_votes = votes["buy"] + votes["sell"]
    if total_votes < 3:
        return None

    direction = "BUY" if votes["buy"] > votes["sell"] else "SELL"
    confidence = int((max(votes.values()) / total_votes) * 100)
    
    if total_votes >= 3 and min(votes.values()) > 0:
        confidence = int(confidence * 0.85)

    return {
        "direction": direction,
        "confidence": confidence,
        "votes": votes,
        "reasons": reasons,
        "regime": regime,
    }
