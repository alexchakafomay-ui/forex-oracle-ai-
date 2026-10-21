import numpy as np

def rule_based_probability(df):
    last = df.iloc[-1]
    score_bull = 0.0
    score_bear = 0.0
    total = 0.0

    if last["ema50"] > last["ema200"]:
        score_bull += 1.0
    else:
        score_bear += 1.0
    total += 1.0

    if last["rsi"] < 40:
        score_bull += 1.0
    elif last["rsi"] > 60:
        score_bear += 1.0
    total += 1.0

    if last["smc_bullish_ob"] == 1 or last["smc_bos_bull"] == 1:
        score_bull += 1.5
    if last["smc_bearish_ob"] == 1 or last["smc_bos_bear"] == 1:
        score_bear += 1.5
    total += 1.5

    if last["adx"] > 25:
        total += 0.5

    p_bull = score_bull / (score_bull + score_bear + 1e-9)
    p_bear = score_bear / (score_bull + score_bear + 1e-9)
    p_side = max(0.0, 1.0 - abs(p_bull - p_bear) - 0.1)
    s = p_bull + p_bear + p_side
    return {"bull": p_bull/s, "bear": p_bear/s, "side": p_side/s}

def ensemble_predict(df):
    probs = rule_based_probability(df)
    probs["confidence"] = int(max(probs["bull"], probs["bear"]) * 100)
    return probs
