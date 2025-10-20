# Historic Stock Price in Gold

**Description:** Recent historic **NASDAQ** and **DJIA** prices, shown both in **USD** and in **ounces of gold** (index / gold).
Everything is reproducible with three small Python scripts and the resulting CSVs & charts.

> **Disclaimer:** For **educational** use only. This repo does **not** provide investment advice and does **not** predict future prices.

---

## Quick start

```bash
# 1) Create/activate a virtual env (recommended)
python3 -m venv .venv
source .venv/bin/activate

# 2) Install deps
pip install -U pandas matplotlib yfinance

# 3) Fetch DJIA + NASDAQ (Mon/Fri closes only)
python3 historic_stock_data.py

# 4) Fetch gold (COMEX continuous futures)
python3 historic_gold_price.py

# 5) Merge + build charts (USD vs oz-of-gold)
#    The file in this repo is named:
python3 nasdaq_djia_gold_price.py
# (If you kept the earlier filename, it's the same script content as build_charts.py)
```

The output files (CSV + PNG) will be regenerated in-place.

---

## Repo contents

```
chart_djia_usd_vs_gold.png                 # DJIA: USD (left axis) vs per-oz-of-gold (right)
chart_nasdaq_usd_vs_gold.png               # NASDAQ: USD (left axis) vs per-oz-of-gold (right)
gold_raw_GCF_2024-01-01_2025-10-20.csv     # Daily gold prices (GC=F), tidy "Date,Open,High,Low,Close,Adj Close,Volume"
historic_gold_price.py                     # Script #2: fetch gold, tidy to CSV
historic_stock_data.py                     # Script #1: fetch DJIA (^DJI) + NASDAQ (^IXIC), Mon/Fri closes only
index_closes_mon_fri_2024-01-01_to_2025-10-20.csv  # Mon/Fri closes for ^DJI and ^IXIC
merged_indices_gold_mon_fri_2024-01-01_to_2025-10-20.csv  # Merge + computed ratios
nasdaq_djia_gold_price.py                  # Script #3: merge, compute ratios, render Matplotlib charts
```

---

## How it works

### Script #1 — `historic_stock_data.py`

- Pulls **DJIA** (`^DJI`) and **NASDAQ Composite** (`^IXIC`) from Yahoo via `yfinance`.
- Keeps **actual trading days that are Monday/Friday** to reduce noise.
- Writes `index_closes_mon_fri_YYYY-MM-DD_to_YYYY-MM-DD.csv` with columns:

  - `Date`, `DJI_Close` → renamed to `^DJI` in merge step, `IXIC_Close` → `^IXIC` (depending on your version)
  - If you need all days: remove the `filter_mon_fri` call.

### Script #2 — `historic_gold_price.py`

- Pulls **gold** from Yahoo as **COMEX continuous futures** `GC=F` (falls back to `MGC=F`).
- Writes `gold_raw_GCF_YYYY-MM-DD_YYYY-MM-DD.csv` with standard OHLCV columns.
- Uses **Adj Close** when available.

### Script #3 — `nasdaq_djia_gold_price.py` (merge + charts)

- Reads the two CSVs above, left-joins on `Date`, **forward-fills** gold if an index date is missing a print.
- Computes ratios:

  - `DJI_per_oz_gold` = `^DJI` / `Gold_Close`
  - `IXIC_per_oz_gold` = `^IXIC` / `Gold_Close`

- Produces:

  - `merged_indices_gold_mon_fri_...csv`
  - `chart_djia_usd_vs_gold.png`
  - `chart_nasdaq_usd_vs_gold.png`

**Chart style:** Dual y-axes for readability (USD on left, ounces of gold on right).
Per your tweak, the left-axis line in the plotting function uses **yellow**:

```py
ax_left.plot(dates, y_left, label=y_left_label, color='y')  # yellow
```

---

## Example output (embed-ready)

If you're referencing these from a blog, you can use GitHub raw paths:

```markdown
![DJIA: USD vs per-oz-of-gold](https://raw.githubusercontent.com/basperheim/historic-stock-price-in-gold/master/chart_djia_usd_vs_gold.png)

![NASDAQ: USD vs per-oz-of-gold](https://raw.githubusercontent.com/basperheim/historic-stock-price-in-gold/master/chart_nasdaq_usd_vs_gold.png)
```

_(Change `master` to your default branch if different.)_

---

## Data notes & caveats

- **Free data:** `yfinance` wraps publicly accessible Yahoo endpoints. Availability can vary by symbol/region; indices work well, and `GC=F` is generally stable.
- **Spot gold:** `XAUUSD=X` is flaky on Yahoo in some locales. Use `GC=F` for reliability; for spot via API, consider Alpha Vantage `FX_DAILY XAU/USD` (free key, rate limits).
- **Trading days:** If Monday or Friday was a **market holiday**, that date simply doesn't appear (no interpolation).
- **Time zones:** All dates are normalized to midnight (naive) before merging.
- **Scaling:** USD values (e.g., DJIA ~40—46k) dwarfs gold-denominated values (~10—20), so we use **dual y-axes**.

---

## Repro tips

- Python ≥ 3.10 recommended (works on 3.13).
- If Yahoo throttles you, re-run; the scripts already use polite settings (single-threaded, small pauses + retry/backoff).
- VPN not required; if you use one, keep endpoints consistent across runs.
- To fetch a different window, edit `START`/`END` in the scripts.

---

## Extending

- Add 50/200-day MAs and a rolling z-score to **Dow/Gold** and **Nasdaq/Gold**.
- Overlay **real yields (TIPS)** or **DXY** for macro context.
- Export a combined dashboard PNG.

Open a PR or file an issue with ideas—happy to keep it practical and reproducible.

---

## License & attribution

- Code: MIT (or your preference—update this line if you choose a different license).
- Data: From Yahoo via `yfinance`; subject to their terms.
- Long-history perspective: see _"200 Years of the Dow/Gold Ratio"_ by David Chapman:
  [https://mikesmoneytalks.ca/200-years-of-the-dowgold-ratio/](https://mikesmoneytalks.ca/200-years-of-the-dowgold-ratio/)

---
