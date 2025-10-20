#!/usr/bin/env python3
"""
Build DJIA/NASDAQ vs Gold charts:
- Input 1: index CSV with columns: Date,^DJI,^IXIC
- Input 2: gold CSV from yfinance (GC=F or MGC=F), columns: Date,Open,High,Low,Close,Adj Close,Volume
          (It may contain a second header-like row with ',GC=F,...' — this script drops it.)
- Output: merged CSV + two PNG charts (dual y-axes for readability)

Requirements:
  pip install pandas matplotlib
"""

from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt

# ---------- CONFIG ----------
INDEX_CSV = "index_closes_mon_fri_2024-01-01_to_2025-10-20.csv"
GOLD_CSV  = "gold_raw_GCF_2024-01-01_2025-10-20.csv"  # change if your file name differs

OUT_MERGED_CSV = "merged_indices_gold_mon_fri_2024-01-01_to_2025-10-20.csv"
OUT_DJIA_PNG   = "chart_djia_usd_vs_gold.png"
OUT_NASDAQ_PNG = "chart_nasdaq_usd_vs_gold.png"

DJI_COL  = "^DJI"
IXIC_COL = "^IXIC"


# ---------- HELPERS ----------
def require_columns(df: pd.DataFrame, required: list[str], name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"{name} missing columns: {missing}. Present: {list(df.columns)}")

def load_index_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    require_columns(df, ["Date", DJI_COL, IXIC_COL], "Index CSV")
    # Normalize date and enforce numeric
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["Date"]).sort_values("Date")
    df[DJI_COL]  = pd.to_numeric(df[DJI_COL], errors="coerce")
    df[IXIC_COL] = pd.to_numeric(df[IXIC_COL], errors="coerce")
    return df

def load_gold_csv(path: str | Path) -> pd.DataFrame:
    g = pd.read_csv(path)
    if "Date" not in g.columns:
        raise SystemExit(f"Gold CSV has no 'Date' column. Columns: {list(g.columns)}")
    # Drop the extra symbol row(s) like ",GC=F,GC=F,..."
    g = g[g["Date"].notna() & (g["Date"].astype(str).str.strip() != "")]
    g["Date"] = pd.to_datetime(g["Date"], errors="coerce").dt.normalize()
    g = g.dropna(subset=["Date"]).sort_values("Date")

    price_col = "Adj Close" if "Adj Close" in g.columns else "Close"
    if price_col not in g.columns:
        raise SystemExit(f"Gold CSV missing 'Adj Close'/'Close'. Columns: {list(g.columns)}")

    g["Gold_Close"] = pd.to_numeric(g[price_col], errors="coerce")
    g = g[["Date", "Gold_Close"]]
    return g

def plot_dual_axis(dates, y_left, y_right, title, y_left_label, y_right_label, out_png):
    fig, ax_left = plt.subplots(figsize=(12, 6))
    ax_right = ax_left.twinx()  # secondary y-axis

    ax_left.plot(dates, y_left, label=y_left_label, color='y') # Yellow color for gold
    ax_right.plot(dates, y_right, label=y_right_label)

    ax_left.set_title(title)
    ax_left.set_xlabel("Date")
    ax_left.set_ylabel(y_left_label)
    ax_right.set_ylabel(y_right_label)

    ax_left.grid(True)

    # Single combined legend
    lines_left, labels_left = ax_left.get_legend_handles_labels()
    lines_right, labels_right = ax_right.get_legend_handles_labels()
    ax_left.legend(lines_left + lines_right, labels_left + labels_right, loc="upper left")

    fig.tight_layout()
    fig.savefig(out_png, dpi=144)
    plt.close(fig)


# ---------- MAIN ----------
def main():
    idx = load_index_csv(INDEX_CSV)
    gold = load_gold_csv(GOLD_CSV)

    # Left-join so we keep your Mon/Fri dates from the index file
    merged = idx.merge(gold, on="Date", how="left").sort_values("Date")

    # Fill missing gold prints (e.g., equity holiday / timing mismatch)
    merged["Gold_Close"] = merged["Gold_Close"].ffill()

    # If still missing, abort with a clear message
    if merged["Gold_Close"].isna().any():
        n_missing = int(merged["Gold_Close"].isna().sum())
        raise SystemExit(
            f"Gold_Close still has {n_missing} NaNs after forward-fill. "
            f"Verify GOLD_CSV range and filename."
        )

    # Compute index levels in ounces of gold
    merged["DJI_per_oz_gold"]  = merged[DJI_COL]  / merged["Gold_Close"]
    merged["IXIC_per_oz_gold"] = merged[IXIC_COL] / merged["Gold_Close"]

    # Write merged CSV
    cols = ["Date", DJI_COL, IXIC_COL, "Gold_Close", "DJI_per_oz_gold", "IXIC_per_oz_gold"]
    merged[cols].to_csv(OUT_MERGED_CSV, index=False)

    # Charts (dual y-axes → clearest for different units)
    plot_dual_axis(
        merged["Date"],
        merged[DJI_COL],
        merged["DJI_per_oz_gold"],
        title="DJIA: USD (left) vs Per-Ounce-of-Gold (right)",
        y_left_label="DJIA (USD)",
        y_right_label="DJIA (oz of gold)",
        out_png=OUT_DJIA_PNG
    )

    plot_dual_axis(
        merged["Date"],
        merged[IXIC_COL],
        merged["IXIC_per_oz_gold"],
        title="NASDAQ Composite: USD (left) vs Per-Ounce-of-Gold (right)",
        y_left_label="NASDAQ (USD)",
        y_right_label="NASDAQ (oz of gold)",
        out_png=OUT_NASDAQ_PNG
    )

    print(f"Wrote merged CSV → {OUT_MERGED_CSV}")
    print(f"Wrote chart → {OUT_DJIA_PNG}")
    print(f"Wrote chart → {OUT_NASDAQ_PNG}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
