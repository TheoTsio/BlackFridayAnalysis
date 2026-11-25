"""Download Eurostat monthly retail trade (sts_trtu_m) for all countries, 2010-2025.

Source: Eurostat, dataset sts_trtu_m
  "Turnover and volume of sales in wholesale and retail trade - monthly data"
API:    https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sts_trtu_m

Filters:
  nace_r2  = G47      Retail trade, except motor vehicles and motorcycles
  indic_bt = VOL_SLS  Volume of sales (deflated)   <- main series
             NETTUR   Net turnover (nominal)       <- only for sanity checks vs ELSTAT
  unit     = I21      Index, 2021=100
  s_adj    = NSA      Unadjusted
             CA       Calendar adjusted, NOT seasonally adjusted  <- use for Nov/Oct ratios
             SCA      Seasonally and calendar adjusted            <- do NOT use for Nov/Oct
  geo      = all (Greece is "EL", not "GR")

Output: data/raw/sts_trtu_m_G47_2010_2025.csv (tidy/long, one row per observation)
Run:    python scripts/download_eurostat.py
"""
from pathlib import Path
import itertools
import json
import urllib.request

import pandas as pd

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sts_trtu_m"
PARAMS = [
    ("lang", "EN"),
    ("nace_r2", "G47"),
    ("unit", "I21"),
    ("indic_bt", "VOL_SLS"),
    ("indic_bt", "NETTUR"),
    ("s_adj", "NSA"),
    ("s_adj", "CA"),
    ("s_adj", "SCA"),
    ("sinceTimePeriod", "2010-01"),
    ("untilTimePeriod", "2025-12"),
]
OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "sts_trtu_m_G47_2010_2025.csv"


def jsonstat_to_df(d: dict) -> pd.DataFrame:
    """Flatten a JSON-stat 2.0 response into a long DataFrame."""
    dims = d["id"]
    sizes = d["size"]
    # position -> code for each dimension
    codes = []
    for dim in dims:
        idx = d["dimension"][dim]["category"]["index"]
        codes.append(sorted(idx, key=idx.get))
    values = d["value"]  # dict {flat_index_str: value} (sparse)
    status = d.get("status", {})
    rows = []
    for flat, combo in enumerate(itertools.product(*codes)):
        key = str(flat)
        if key in values:
            rows.append((*combo, values[key], status.get(key, "")))
    assert len(rows) == len(values), "flattening mismatch"
    df = pd.DataFrame(rows, columns=[*dims, "value", "flag"])
    geo_labels = d["dimension"]["geo"]["category"]["label"]
    df["geo_name"] = df["geo"].map(geo_labels)
    return df


def main() -> None:
    url = BASE + "?" + "&".join(f"{k}={v}" for k, v in PARAMS)
    print("GET", url)
    with urllib.request.urlopen(url, timeout=300) as r:
        d = json.load(r)
    print("Dataset:", d["label"], "| updated:", d["updated"])

    df = jsonstat_to_df(d)
    df["date"] = pd.to_datetime(df["time"], format="%Y-%m")
    df = df[["geo", "geo_name", "indic_bt", "s_adj", "unit", "nace_r2",
             "time", "date", "value", "flag"]]
    df = df.sort_values(["geo", "indic_bt", "s_adj", "date"]).reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df):,} rows to {OUT}")


if __name__ == "__main__":
    main()
