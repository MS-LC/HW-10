# Was there less snow in New England?

**GitHub Pages report:** `https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPOSITORY/` (replace these placeholders after creating the repository and enabling Pages).

This project tests the claim that New England received less snow in the first two decades of the 21st century than in the last six decades of the 20th century. It uses NOAA NCEI GHCN-Daily daily snowfall (`SNOW`) observations from Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, and Vermont.

## Reproduce the analysis

Requirements: Python 3.10+, `matplotlib`.

```bash
python -m pip install matplotlib
python scripts/analyze.py
```

The script downloads NOAA station metadata, the station inventory, and only the relevant New England station CSVs into `data/` (excluded from Git). It uses the exact NOAA data-access directory supplied for this project, applies the coverage and balanced-station rules, and generates:

- `docs/summary.json` — computed headline answer and period statistics
- `docs/annual.csv` — year-by-year regional station mean
- `docs/station-means.csv` — station-level period comparison
- `docs/snowfall-trend.png` — annual series and period means
- `docs/station-comparison.png` — paired period averages for every eligible station

Open `docs/index.html` locally after running the script, or publish the `docs/` directory with GitHub Pages.


## Results from the completed analysis

The supplied analysis of 98 eligible stations returned **NO**: average November–April snowfall was **7.12 inches** in 1941–2000 and **7.28 inches** in 2001–2020, an increase of approximately **0.15 inches (2.2%)**. There were 4,608 station-season observations in the baseline period and 1,715 in the modern period.

The station-level results are mixed: **63 stations increased**, **34 decreased**, and **one was unchanged**. The largest increase was at Belfast (+2.51 inches per season); the largest decrease was at Enosburg Falls (−3.20 inches). See [`docs/results.md`](docs/results.md), the [published report page](docs/index.html), and the full [`station-means.csv`](docs/station-means.csv) and [`annual.csv`](docs/annual.csv) tables. The annual series ranges from 3.07 inches in 1980 to 11.07 inches in 1996 in the supplied CSV.

These are descriptive station averages, not an area-weighted estimate or a test of statistical significance. Individual locations show different patterns.

## Method

Snow seasons run November through April and are labelled by the year containing April. The comparison is 1941–2000 versus 2001–2020. A station-season requires valid daily snowfall on at least 80% of season days. To reduce station-composition bias, stations must have at least 30 usable seasons in the earlier period and 10 in the later period; the same station panel is used in both period means.

Daily GHCN-Daily station CSV records are filtered to the `SNOW` element. Missing values (`-9999`) and records with nonblank quality flags are excluded; NOAA snowfall values in millimetres are converted to inches. Each eligible station is weighted equally when calculating the two period averages. The analysis is not area-weighted and is sensitive to station coverage and measurement practices; see the report's limitations section.

## Publish with GitHub Pages

1. Create a GitHub repository and push this directory to its default branch.
2. Run the analysis locally (`python scripts/analyze.py`) before publishing so the generated summary and graph exist in `docs/`.
3. In **Settings → Pages**, set the build and deployment source to **GitHub Actions**. The included workflow runs the NOAA download and analysis, then deploys the generated report.
4. Replace the placeholder URL at the top of this README with the actual Pages URL.

The repository deliberately excludes downloaded station data and Python/build caches. Do not commit the `data/` directory or the full GHCN archive.

## Source

NOAA National Centers for Environmental Information, [Global Historical Climatology Network-Daily data directory](https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/) and [GHCN-Daily documentation](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily). The analysis downloads station metadata from `/doc/` and station CSVs from `/access/` under the supplied data directory.
