# metrics.py
import pandas as pd, matplotlib.pyplot as plt

df = pd.read_csv("merged_indices_gold_mon_fri_2024-01-01_to_2025-10-20.csv", parse_dates=["Date"])
df.set_index("Date", inplace=True)

def with_metrics(s: pd.Series, lookback=750):
    out = pd.DataFrame({"ratio": s})
    out["ma50"]  = out["ratio"].rolling(50).mean()
    out["ma200"] = out["ratio"].rolling(200).mean()
    roll = out["ratio"].rolling(lookback, min_periods=252)
    out["z"] = (out["ratio"] - roll.mean()) / roll.std()
    return out

dj = with_metrics(df["DJI_per_oz_gold"])
ix = with_metrics(df["IXIC_per_oz_gold"])

def panel(ax, m, title):
    ax.plot(m.index, m["ratio"], label="ratio")
    ax.plot(m.index, m["ma50"],  label="MA50")
    ax.plot(m.index, m["ma200"], label="MA200")
    for z in (1,2):
        ax.fill_between(m.index,  z, -z, where=(m["z"].notna()),
                        alpha=0.08, step="pre", label=None)
    ax.set_title(title); ax.grid(True); ax.legend()

fig, axs = plt.subplots(2, 1, figsize=(12,8), sharex=True)
panel(axs[0], dj, "Dow/Gold")
panel(axs[1], ix, "Nasdaq/Gold")
plt.tight_layout(); plt.savefig("metrics_dashboard.png", dpi=144)
