#!/usr/bin/env python3
import time, random
import pandas as pd
import yfinance as yf

START = "2024-01-01"
END   = "2025-10-20"
TICKERS = {"^DJI": "DJI_Close", "^IXIC": "IXIC_Close"}
OUT = f"index_closes_mon_fri_{START}_to_{END}.csv"

def download_range(ticker: str, start: str, end: str, max_retries: int = 4) -> pd.DataFrame:
    delay = 2.0
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(
                ticker,
                start=start,
                end=end,
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False  # single-threaded to be gentle
            )
            if df is None or df.empty:
                raise RuntimeError(f"No data returned for {ticker}")
            # Ensure tz-naive index
            if getattr(df.index, "tz", None) is not None:
                df = df.tz_convert(None)
            return df
        except Exception as e:
            last_err = e
            if attempt == max_retries:
                raise
            time.sleep(delay + random.uniform(0, 0.75))
            delay *= 1.6
    raise last_err  # pragma: no cover

def pick_close(df: pd.DataFrame) -> pd.Series:
    s = df["Adj Close"] if "Adj Close" in df.columns else df["Close"]
    # Set the series name explicitly (avoid Series.rename with a string)
    s = s.copy()
    s.name = "Close"
    return s

def filter_mon_fri(s: pd.Series) -> pd.Series:
    s = s.copy()
    s.index = pd.to_datetime(s.index)
    wd = s.index.weekday  # 0=Mon..6=Sun
    return s[(wd == 0) | (wd == 4)]

def main():
    series = []
    for i, (sym, out_col) in enumerate(TICKERS.items()):
        if i > 0:
            time.sleep(2.5)  # small pause between the two requests
        df = download_range(sym, START, END)
        close = filter_mon_fri(pick_close(df))
        close.name = out_col
        series.append(close)

    out = pd.concat(series, axis=1).sort_index()
    out = out.reset_index().rename(columns={"index": "Date"})
    out["Date"] = pd.to_datetime(out["Date"]).dt.strftime("%Y-%m-%d")
    out.to_csv(OUT, index=False)
    print(f"Wrote {len(out):,} rows → {OUT}")

if __name__ == "__main__":
    main()
