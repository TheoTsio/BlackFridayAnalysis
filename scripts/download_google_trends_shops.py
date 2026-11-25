"""Download Google Trends searches for Greek shops around Black Friday, 2016-2025.

NOTE: Google Trends measures SEARCHES, not sales (non-official source, label it).

Two downloads:
1. DAILY, one query per shop per year (1 Oct - 31 Dec). Each query is scaled to
   that shop-year's own peak = 100, so small shops are not rounded to zero.
   -> used for each shop's own chart ("x an average October day").
2. MONTHLY 2016-2025, shops in groups of 4 + one ANCHOR term (Skroutz) that is in
   every group. Rescaling each group by the anchor puts all shops on ONE scale.
   -> gives each shop's relative size, needed to SUM searches across shops.

Edit SHOPS to add or remove shops (label: search term). Search terms use the
spelling Greeks search most (checked in Google Trends, 2025).
Google samples data: re-downloading gives slightly different numbers.

Outputs (data/raw/):
  google_trends_GR_shops_daily_oct_dec_2016_2025.csv   long: date, year, shop, term, searches
  google_trends_GR_shops_monthly_anchored_2016_2025.csv long: date, shop, term, level
Run: python scripts/download_google_trends_shops.py   (needs: pip install pytrends; takes ~15 min)
"""
from datetime import date
from pathlib import Path
import time

import pandas as pd
from pytrends.request import TrendReq

# label -> (search term, category)
SHOPS = {
    # electronics
    "Public":        ("Public", "Electronics"),
    "Kotsovolos":    ("κωτσοβολος", "Electronics"),
    "Plaisio":       ("plaisio", "Electronics"),
    "e-shop.gr":     ("eshop", "Electronics"),
    "Media Markt":   ("media markt", "Electronics"),
    "Germanos":      ("γερμανος", "Electronics"),
    "Electronet":    ("electronet", "Electronics"),
    "Apple":         ("Apple", "Electronics"),
    # marketplaces & price comparison
    "Skroutz":       ("Skroutz", "Marketplace"),
    "BestPrice":     ("bestprice", "Marketplace"),
    "Temu":          ("temu", "Marketplace"),
    "Shein":         ("shein", "Marketplace"),
    "AliExpress":    ("aliexpress", "Marketplace"),
    # fashion, beauty, home, sport, toys
    "Zara":          ("zara", "Fashion"),
    "H&M":           ("h&m", "Fashion"),
    "Hondos Center": ("hondos", "Beauty"),
    "Sephora":       ("sephora", "Beauty"),
    "IKEA":          ("ikea", "Home"),
    "Jumbo":         ("jumbo", "Home & toys"),
    "Intersport":    ("intersport", "Sport"),
}
ANCHOR = "Skroutz"
GEO = "GR"
YEARS = range(2016, 2026)
OUT = Path(__file__).resolve().parent.parent / "data" / "raw"


def query(pt, terms, timeframe):
    for attempt in range(6):
        try:
            pt.build_payload(terms, geo=GEO, timeframe=timeframe)
            return pt.interest_over_time().drop(columns="isPartial", errors="ignore")
        except Exception as e:  # rate limit (429): wait and retry
            wait = 30 * (attempt + 1)
            print(f"  retry in {wait}s after error: {e}")
            time.sleep(wait)
    raise RuntimeError(f"Google Trends failed for {terms} {timeframe}")


def daily(pt):
    rows = []
    for label, (term, cat) in SHOPS.items():
        for year in YEARS:
            d = query(pt, [term], f"{year}-10-01 {year}-12-31")
            if d.empty:  # no searches at all (e.g. shop not in Greece yet)
                continue
            rows.append(pd.DataFrame({"date": d.index, "year": year, "shop": label, "category": cat,
                                      "term": term, "searches": d[term].to_numpy()}))
            time.sleep(3)
        print("daily:", label, "ok")
    return pd.concat(rows, ignore_index=True)


def monthly_anchored(pt):
    anchor_term = SHOPS[ANCHOR][0]
    others = [s for s in SHOPS if s != ANCHOR]
    groups = [others[i:i + 4] for i in range(0, len(others), 4)]
    frames, ref = [], None
    for g in groups:
        terms = [anchor_term] + [SHOPS[s][0] for s in g]
        d = query(pt, terms, "2016-01-01 2025-12-31")
        if ref is None:
            ref = d[anchor_term]
        # rescale the group so its anchor matches the first group's anchor
        factor = ref.sum() / d[anchor_term].sum()
        for s in g:
            frames.append(pd.DataFrame({"date": d.index, "shop": s, "term": SHOPS[s][0],
                                        "level": d[SHOPS[s][0]].to_numpy() * factor}))
        time.sleep(3)
    frames.append(pd.DataFrame({"date": ref.index, "shop": ANCHOR, "term": anchor_term, "level": ref.to_numpy()}))
    out = pd.concat(frames, ignore_index=True)
    print("monthly anchored ok")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pt = TrendReq(hl="en-US", tz=0)
    today = date.today().isoformat()

    m = monthly_anchored(pt)
    m["downloaded"] = today
    m.to_csv(OUT / "google_trends_GR_shops_monthly_anchored_2016_2025.csv", index=False)

    d = daily(pt)
    d["downloaded"] = today
    d.to_csv(OUT / "google_trends_GR_shops_daily_oct_dec_2016_2025.csv", index=False)
    print(f"Saved {len(d):,} daily rows and {len(m):,} monthly rows")


if __name__ == "__main__":
    main()
