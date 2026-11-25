# Black Friday in the official numbers

Does Black Friday show up in Greek retail sales? This repository holds the data and the notebook behind the Big Blue Data Academy blog post *"Black Friday in the official numbers"* (November 2026).

It compares two things for Greece, from 2010 to 2025:

- **Official monthly retail sales** from Eurostat: does November rise compared with October, and did that change after Black Friday arrived?
- **Google searches** for "Black Friday" and for 20 Greek shops: when did Greeks start looking for Black Friday, and on which days?

It also compares Greece with the other EU countries.

## Main findings

| | Greece | EU-27 |
|---|---|---|
| Sales volume, November vs October, average 2010–2015 | −2.2% | −2.7% |
| Sales volume, November vs October, average 2016–2025 (excl. 2020) | −0.6% | +1.2% |
| Sales volume, November vs October, average 2021–2025 | −0.7% | +2.1% |

- **Searches for "Black Friday" in Greece jumped in 2016.** They went from almost nothing (4 out of 100 in November 2015) to 63 in November 2016, peaked in 2019, and have been steady at about 55–60 since 2021.
- **Searches peak on Black Friday itself**, in every year from 2016 to 2025.
- **Greek November sales did not clearly follow.** The change since 2016 (+1.6 points) is within normal year-to-year variation (Welch t-test, p = 0.28).
- **The EU changed more than Greece.** November moved from below October to clearly above it. Greece ranks 19th of 26 EU countries by its November jump (2021–2025).
- **In Greece, November is an average month.** Greek sales peak in July–August (tourism) and December. Across the EU, November is already about 4% above an average month.

**Limits.** The sales data is monthly and covers all retail, so it shows whether November as a whole rises. It cannot isolate Black Friday weekend, and it cannot show whether Black Friday moves purchases from other weeks. Google Trends measures searches, not sales.

## Data sources

| Source | What | Official? |
|---|---|---|
| [Eurostat `sts_trtu_m`](https://ec.europa.eu/eurostat/databrowser/view/sts_trtu_m/default/table) | Monthly turnover and volume of sales in retail trade, all EU countries, 2010–2025 | Yes |
| [Google Trends](https://trends.google.com/) | Search interest for "Black Friday" and 20 shop names in Greece | No, labelled as searches |

The Eurostat figures come from each country's statistics office. The Greek figures come from ELSTAT.

### Eurostat: which series and why

| Field | Code used | Meaning |
|---|---|---|
| Activity (`nace_r2`) | `G47` | Retail trade, except motor vehicles and motorcycles |
| Indicator (`indic_bt`) | `VOL_SLS` | **Volume of sales**: turnover with price changes removed. Main series. |
| | `NETTUR` | Net turnover in euros, including inflation. Used only to cross-check ELSTAT. |
| Unit | `I21` | Index, average month of 2021 = 100 |
| Adjustment (`s_adj`) | `CA` | **Calendar adjusted, not seasonally adjusted.** Main series. |
| | `NSA` | Unadjusted |
| | `SCA` | Seasonally and calendar adjusted. **Not used for November vs October**, because seasonal adjustment removes exactly the November effect we are looking for. |

Greece is `EL` in Eurostat, not `GR`.

**Flags** in the data: `p` = provisional (may be revised), `b` = break in series (Slovenia, January 2021), `i` = see Eurostat metadata. The Greek calendar-adjusted volume series has no flags.

**Check against ELSTAT:** Greek retail turnover, November vs October 2024, is +2.4% in both this data and ELSTAT's release.

### Google Trends: how to read it

- Values are relative (0–100), not search counts. Google rescales every query and samples the data, so a new download gives slightly different numbers. The files in `data/raw/` are the ones used for the post, and each records its download date.
- **"Black Friday", monthly 2010–2025:** one query, so years compare directly. The Greek term "Μαύρη Παρασκευή" has almost no searches.
- **Shops, daily October–December:** one query per shop per year. To compare shops and years, each day is shown as *times an average October day* for that shop.
- **Sum of all shops:** needs every shop on one scale. A monthly query with Skroutz in every group acts as the common anchor.
- **Search terms:** each shop uses the spelling Greeks search most, e.g. `κωτσοβολος` in Greek letters, `eshop` for e-shop.gr. Some terms also catch other meanings: "Apple" includes product news, and "Public" is also an English word.

## Repository structure

```
├── data/raw/                     downloaded data (CSV), not edited by hand
├── figures/                      charts saved by the notebook (PNG, 200 dpi)
│   └── shops/                    one chart per shop
├── notebooks/
│   └── black_friday.ipynb        the analysis
├── scripts/
│   ├── download_eurostat.py               Eurostat retail trade
│   ├── download_google_trends.py          "Black Friday" searches
│   └── download_google_trends_shops.py    searches for 20 shops
└── requirements.txt
```

### What the notebook contains

| Part | Sections | Content |
|---|---|---|
| 1. Data | 1–6 | Load the Eurostat data, check coverage and flags, cross-check ELSTAT |
| 2. Black Friday each year | 7–9 | Search peaks vs Black Friday dates, shop searches, searches vs November sales |
| 3. Greece vs the EU | 10–14 | November jump per year, before/after 2016, EU ranking, month-by-month profile |

## How to reproduce

Requires Python 3.9 or later.

```bash
pip install -r requirements.txt

# 1. Download the data (optional: the CSVs used for the post are already in data/raw/)
python scripts/download_eurostat.py
python scripts/download_google_trends.py
python scripts/download_google_trends_shops.py   # ~20+ minutes, Google rate-limits requests

# 2. Run the notebook (from the notebooks/ folder, it reads ../data/raw/)
cd notebooks
jupyter nbconvert --to notebook --execute --inplace black_friday.ipynb
```

Running the notebook writes all charts to `figures/`.

Note that re-running the downloads gives you newer data than the post. Eurostat revises recent months, and Google Trends resamples. Keep the original CSVs if you want to reproduce the published numbers exactly.

## Source line for charts

> Source: Eurostat, retail trade volume index (sts_trtu_m), calendar adjusted, 2021 = 100; data extracted 25 Nov 2026. Search data: Google Trends (searches, not sales).
