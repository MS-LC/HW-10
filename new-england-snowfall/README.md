# Was there less snow in New England?

**GitHub Pages report:** `https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPOSITORY/` (replace these placeholders after creating the repository and enabling Pages).

This project tests the claim that New England received less snow in the first two decades of the 21st century than in the last six decades of the 20th century. It uses NOAA NCEI GHCN-Daily daily snowfall (`SNOW`) observations from Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, and Vermont.

## Reproduce the analysis

Requirements: Python 3.10+, `matplotlib`.

```bash
python -m pip install matplotlib
python scripts/analyze.py
```

The script downloads station inventory and individual `.dly` files into `data/` (excluded from Git), applies the documented coverage and balanced-station rules, and generates:

- `docs/summary.json` — computed headline answer and period statistics
- `docs/annual.csv` — year-by-year regional station mean
- `docs/station-means.csv` — station-level period comparison
- `docs/snowfall-trend.png` — annual series and period means

Open `docs/index.html` locally after running the script, or publish the `docs/` directory with GitHub Pages.

## Method

Snow seasons run November through April and are labelled by the year containing April. The comparison is 1941–2000 versus 2001–2020. A station-season requires valid daily snowfall on at least 80% of season days. To reduce station-composition bias, stations must have at least 30 usable seasons in the earlier period and 10 in the later period; the same station panel is used in both period means.

Daily GHCN-Daily snowfall values are parsed from the fixed-width `.dly` files, missing values and nonblank quality flags are excluded, and tenths of millimetres are converted to inches. The analysis is not area-weighted and is sensitive to station coverage and measurement practices; see the report's limitations section.

## Publish with GitHub Pages

1. Create a GitHub repository and push this directory to its default branch.
2. Run the analysis locally (`python scripts/analyze.py`) before publishing so the generated summary and graph exist in `docs/`.
3. In **Settings → Pages**, choose **Deploy from a branch**, select the default branch and `/docs`.
4. Replace the placeholder URL at the top of this README with the actual Pages URL.

The repository deliberately excludes downloaded station data and Python/build caches. Do not commit the `data/` directory or the full GHCN archive.

## Source

NOAA National Centers for Environmental Information, [Global Historical Climatology Network-Daily](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily). Station files are distributed at `https://www.ncei.noaa.gov/pub/data/ghcn/daily/`.
