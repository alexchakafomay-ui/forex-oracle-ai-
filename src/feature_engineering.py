import pandas as pd
import pandas_ta as ta
import numpy as np
import pyvsmc as smc

def to_dataframe(values):
    df = pd.DataFrame(values)
    df["datetime"] = pd.to_datetime(df["datetime"])
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    return df.sort_values("datetime").reset_index(drop=True)

def add_technical(df):
    df["ema50"]  = ta.ema(df["close"], length=50)
    df["ema200"] = ta.ema(df["close"], length=200)
    df["rsi"]    = ta.rsi(df["close"], length=14)
    df["atr"]    = ta.atr(df["high"], df["low"], df["close"], length=14)
    df["adx"]    = ta.adx(df["high"], df["low"], df["close"], length=14)["ADX_14"]
    bb = ta.bbands(df["close"], length=20)
    df["bb_lower"] = bb["BBL_20_2.0"]
    df["bb_upper"] = bb["BBU_20_2.0"]
    return df

def add_smc(df):
    high = df["high"].values
    low  = df["low"].values
    close = df["close"].values
    open_ = df["open"].values

    fvg   = smc.detect_fvg(high, low, close=close, compute_mitigation=True)
    swings = smc.detect_swings(high, low, window_size=2)
    struct = smc.detect_structure(high, low, close, window_size=2, break_mode="close")
    obs    = smc.detect_order_blocks(open_, high, low, close, lookback=5,
                                     zone_mode="body", compute_mitigation=True)

    df["smc_bullish_ob"] = obs.bullish_ob.astype(int)
    df["smc_bearish_ob"] = obs.bearish_ob.astype(int)
    df["smc_bos_bull"]   = struct.bos_bullish.astype(int)
    df["smc_bos_bear"]   = struct.bos_bearish.astype(int)
    df["smc_fvg_bull"]   = fvg.bullish.astype(int)
    df["smc_fvg_bear"]   = fvg.bearish.astype(int)
    return df

def detect_regime(df):
    last = df.iloc[-1]
    if last["adx"] > 25:
        return "trending"
    if last["atr"] > df["atr"].rolling(50).mean().iloc[-1] * 1.5:
        return "volatile"
    return "ranging"
