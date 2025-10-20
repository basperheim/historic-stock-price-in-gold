#!/usr/bin/env python3
"""
Fetch raw gold price history and write to CSV (no merging, no transforms).
Primary: 'GC=F' (COMEX Gold continuous futures)
Fallback: 'MGC=F' (Micro Gold futures)

Requires:
  pip install yfinance pandas
"""

import time, random
import pandas as pd
import yfinance as yf

# ---- CONFIG ----
START = "2024-01-01"
END   = "2025-10-20"
SYMBOLS_TRY = ["GC=F", "MGC=F"]  # try in order
OUT_TEMPLATE = "gold_raw_{sym}_{start}_{end}.csv"

def download_yf(ticker: str, start: str, end: str, max_retries: int = 4) -> pd.DataFrame:
    delay = 2.0
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(
                ticker,
                start=start,
                end=end,
                interval="1d",
                auto_adjust=False,   # keep raw OHLC + Adj Close as-is
                progress=False,
                threads=False
            )
            if df is None or df.empty:
                raise RuntimeError(f"No data returned for {ticker}")
            if getattr(df.index, "tz", None) is not None:
                df = df.tz_convert(None)
            return df
        except Exception as e:
            last_err = e
            if attempt == max_retries:
                raise
            time.sleep(delay + random.uniform(0, 0.75))
            delay *= 1.6
    raise last_err

def main():
    used = None
    df = None
    for sym in SYMBOLS_TRY:
        try:
            df = download_yf(sym, START, END)
            used = sym
            break
        except Exception as e:
            print(f"[WARN] Failed for {sym}: {e}")
    if df is None or used is None:
        raise SystemExit("Could not fetch gold data from any symbol in SYMBOLS_TRY.")

    # Tidy index -> Date column
    out = df.copy()
    out.index = pd.to_datetime(out.index).normalize()
    out = out.reset_index().rename(columns={"index": "Date"})
    out["Date"] = out["Date"].dt.strftime("%Y-%m-%d")

    # Ensure standard column order if present
    cols = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    out = out[[c for c in cols if c in out.columns]]

    out_path = OUT_TEMPLATE.format(sym=used.replace("=", ""), start=START, end=END)
    out.to_csv(out_path, index=False)
    print(f"Gold source used: {used}")
    print(f"Wrote {len(out):,} rows -> {out_path}")

if __name__ == "__main__":
    main()
