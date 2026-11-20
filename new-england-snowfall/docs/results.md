# Results: Was there less snow in New England?

## Overall answer: NO

The supplied NOAA GHCN-Daily analysis shows a small increase in average November–April snowfall between the two study periods. The 1941–2000 average was **7.12 inches per season**, compared with **7.28 inches** in 2001–2020. That is an increase of approximately **0.15 inches, or 2.2%**.

The analysis includes **98 eligible weather stations** and 4,608 station-season observations in the baseline period and 1,715 in the modern period.

## Station-by-station comparison

Of the 98 stations, **63 (64.3%) increased**, **34 (34.7%) decreased**, and **1** showed no change in the rounded station comparison. This shows that the regional result does not describe every location: snowfall trends varied by station.

### Five largest increases

| Station | 1941–2000 mean | 2001–2020 mean | Change |
|---|---:|---:|---:|
| BELFAST | 4.86 in | 7.36 in | **+2.51 in** |
| VAN BUREN 2 | 8.45 in | 9.94 in | **+1.49 in** |
| LOWELL | 5.09 in | 6.56 in | **+1.47 in** |
| RUTLAND | 6.20 in | 7.58 in | **+1.38 in** |
| MIDDLEBORO | 3.30 in | 4.64 in | **+1.34 in** |

### Five largest decreases

| Station | 1941–2000 mean | 2001–2020 mean | Change |
|---|---:|---:|---:|
| ENOSBURG FALLS | 9.82 in | 6.62 in | **-3.20 in** |
| NORFOLK 2 SW | 9.38 in | 7.42 in | **-1.96 in** |
| WOODLAND | 7.09 in | 5.61 in | **-1.49 in** |
| HANOVER | 6.88 in | 5.39 in | **-1.49 in** |
| SANFORD 2 NNW | 6.58 in | 5.13 in | **-1.45 in** |

## Annual variation

The annual CSV covers 80 seasons (1941–2020). The highest annual average in the supplied file was **11.07 inches in 1996** (91 reporting stations); the lowest was **3.07 inches in 1980** (86 reporting stations). Annual averages vary substantially, and the number of stations contributing to each year is not constant.

## Method and limitations

Snow seasons run from November through April and are labelled by the year containing April. A station-season is included when at least 80% of its November–April days have valid observations. Stations in the balanced panel need at least 30 valid seasons in 1941–2000 and at least 10 in 2001–2020. The supplied summary reports 4,608 baseline and 1,715 modern station-season observations.

The regional comparison is based on the selected station panel, not an area-weighted estimate of every location in New England. The station counts and individual station changes show meaningful local variation. The 2.2% difference is descriptive; these summary results alone do not establish statistical significance or prove that every part of New England became snowier.

## Data files and figures

- [`annual.csv`](annual.csv): annual mean snowfall and number of contributing stations.
- [`station-means.csv`](station-means.csv): station-level means and changes.
- [`snowfall-trend.png`](snowfall-trend.png): annual snowfall trend.
- [`station-comparison.png`](station-comparison.png): station-by-station period comparison.
- [`summary.json`](summary.json): overall result and station summary statistics.

Source: [NOAA NCEI GHCN-Daily](https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/), daily `SNOW` element.
