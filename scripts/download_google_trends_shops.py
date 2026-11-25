"""Download daily Google Trends searches for Greek e-shops, Oct-Dec 2016-2025.

NOTE: Google Trends measures SEARCHES, not sales (non-official source, label it).

Terms (Google Trends allows max 5 per query; all 5 share one 0-100 scale per query):
  eshop        e-shop.gr  ("e-shop" with a hyphen is barely searched)
  κωτσοβολος   Kotsovolos (searched more in Greek than "kotsovolos")
  Skroutz      price comparison / marketplace
  Public       electronics & books chain
  Apple        brand (also catches iPhone news, not only shopping)

One query per year (1 Oct - 31 Dec) gives DAILY values. Values are scaled within
each year's query, so compare shapes and ratios within a year, not raw levels
across years. Google samples data: re-downloading gives slightly different numbers.

Output: data/raw/google_trends_GR_shops_daily_oct_dec_2016_2025.csv
Run:    python scripts/download_google_trends_shops.py   (needs: pip install pytrends)
"""
from datetime import date
from pathlib import Path
import time

import pandas as pd
from pytrends.request import TrendReq

TERMS = ["eshop", "κωτσοβολος", "Skroutz", "Public", "Apple"]
GEO = "GR"
OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "google_trends_GR_shops_daily_oct_dec_2016_2025.csv"


def query(pt, timeframe):
    for attempt in range(5):
        try:
            pt.build_payload(TERMS, geo=GEO, timeframe=timeframe)
            return pt.interest_over_time().drop(columns="isPartial", errors="ignore")
        except Exception as e:  # rate limit (429): wait and retry
            print("  retry after error:", e)
            time.sleep(20 * (attempt + 1))
    raise RuntimeError(f"Google Trends failed for {timeframe}")


def main():
    pt = TrendReq(hl="en-US", tz=0)
    frames = []
    for year in range(2016, 2026):
        d = query(pt, f"{year}-10-01 {year}-12-31")
        d["year"] = year
        frames.append(d)
        print(year, "ok")
        time.sleep(5)
    out = pd.concat(frames)
    # long format: one row per day and shop
    out = out.reset_index().melt(id_vars=["date", "year"], var_name="term", value_name="searches")
    out["downloaded"] = date.today().isoformat()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"Saved {len(out):,} rows to {OUT}")


if __name__ == "__main__":
    main()
