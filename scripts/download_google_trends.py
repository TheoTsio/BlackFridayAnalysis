"""Download Google Trends search interest for "Black Friday" in Greece.

NOTE: Google Trends measures SEARCHES, not sales. It is the one non-official source
in this project and must be labelled as such.

Google Trends values are relative (0-100) and rescaled within each query:
  - monthly 2010-2025 (one query)   -> years ARE comparable with each other
  - daily, 1 Oct - 31 Dec per year  -> each year scaled to its own peak = 100,
                                       so only the SHAPE / peak day is comparable
Google samples the data, so re-downloading can give slightly different numbers.
That's why we save the files and note the download date.

Outputs (data/raw/):
  google_trends_GR_monthly_2010_2025.csv
  google_trends_GR_daily_oct_dec_2016_2025.csv
Run: python scripts/download_google_trends.py   (needs: pip install pytrends)
"""
from datetime import date
from pathlib import Path
import time

import pandas as pd
from pytrends.request import TrendReq

TERMS = ["Black Friday", "Μαύρη Παρασκευή"]   # English and Greek spelling
GEO = "GR"
OUT = Path(__file__).resolve().parent.parent / "data" / "raw"


def query(pt, timeframe):
    for attempt in range(5):
        try:
            pt.build_payload(TERMS, geo=GEO, timeframe=timeframe)
            d = pt.interest_over_time()
            return d.drop(columns="isPartial", errors="ignore")
        except Exception as e:  # Google rate-limits (429): wait and retry
            print("  retry after error:", e)
            time.sleep(20 * (attempt + 1))
    raise RuntimeError(f"Google Trends failed for {timeframe}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pt = TrendReq(hl="en-US", tz=0)
    today = date.today().isoformat()

    monthly = query(pt, "2010-01-01 2025-12-31")
    monthly["downloaded"] = today
    monthly.to_csv(OUT / "google_trends_GR_monthly_2010_2025.csv", index_label="date")
    print("monthly:", len(monthly), "rows")

    frames = []
    for year in range(2016, 2026):
        d = query(pt, f"{year}-10-01 {year}-12-31")
        d["year"] = year
        frames.append(d)
        print("daily", year, "ok")
        time.sleep(5)
    daily = pd.concat(frames)
    daily["downloaded"] = today
    daily.to_csv(OUT / "google_trends_GR_daily_oct_dec_2016_2025.csv", index_label="date")
    print("daily:", len(daily), "rows")


if __name__ == "__main__":
    main()
