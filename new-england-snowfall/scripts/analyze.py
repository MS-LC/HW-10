#!/usr/bin/env python3
"""Compare November-April snowfall in New England using NOAA's GHCN-Daily CSVs.

Downloads only station CSVs for New England stations listed as having SNOW data.
Raw data are kept in the ignored data/ directory, never in the Git repository.
"""
from __future__ import annotations
import csv
import json
import math
import urllib.request
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "docs"
BASE = "https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily"
STATES = {"CT", "ME", "MA", "NH", "RI", "VT"}


def download(url: str, destination: Path) -> None:
    """Download a URL once, caching it in the ignored data directory."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size:
        return
    print(f"Downloading {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "NewEnglandSnowfallStudy/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as output:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            output.write(block)


def new_england_stations() -> dict[str, str]:
    """Return station IDs and names for U.S. stations in the six New England states."""
    path = DATA / "ghcnd-stations.txt"
    download(f"{BASE}/doc/ghcnd-stations.txt", path)
    stations: dict[str, str] = {}
    for line in path.read_text(errors="replace").splitlines():
        station_id = line[0:11].strip()
        state = line[38:40].strip()
        if station_id.startswith("US") and state in STATES:
            stations[station_id] = line[41:71].strip()
    return stations


def snow_station_ids() -> set[str]:
    """Read NOAA's inventory and retain stations with a SNOW record in study years."""
    path = DATA / "ghcnd-inventory.txt"
    download(f"{BASE}/doc/ghcnd-inventory.txt", path)
    ids = set()
    for line in path.read_text(errors="replace").splitlines():
        if len(line) < 45 or line[31:35] != "SNOW":
            continue
        try:
            first, last = int(line[36:40]), int(line[41:45])
        except ValueError:
            continue
        if first <= 2020 and last >= 1940:
            ids.add(line[0:11].strip())
    return ids


def load_station_csv(station_id: str) -> dict[tuple[int, int, int], float]:
    """Return valid daily snowfall as inches, keyed by (year, month, day).

    NOAA's GHCN-Daily SNOW values are in millimetres. Blank quality flags are
    retained; nonblank quality flags and NOAA's -9999 missing code are dropped.
    """
    path = DATA / "stations" / f"{station_id}.csv"
    download(f"{BASE}/access/{station_id}.csv", path)
    observations: dict[tuple[int, int, int], float] = {}
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        for row in reader:
            if row.get("ELEMENT") != "SNOW":
                continue
            date = row.get("DATE", "")
            if len(date) != 8 or not date.isdigit():
                continue
            year, month, day = int(date[:4]), int(date[4:6]), int(date[6:8])
            if not (1940 <= year <= 2020):
                continue
            try:
                raw = int(row.get("DATA_VALUE", ""))
            except (TypeError, ValueError):
                continue
            if raw == -9999 or (row.get("Q_FLAG") or "").strip():
                continue
            # GHCN-Daily SNOW is in mm (not tenths of mm).
            observations[(year, month, day)] = raw / 25.4
    return observations


def season_dates(end_year: int) -> list[tuple[int, int, int]]:
    """List all dates from November of the previous year through April."""
    import calendar
    dates = []
    for year, month in ((end_year - 1, 11), (end_year - 1, 12), (end_year, 1),
                        (end_year, 2), (end_year, 3), (end_year, 4)):
        dates.extend((year, month, day) for day in range(1, calendar.monthrange(year, month)[1] + 1))
    return dates


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def main() -> None:
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    stations = new_england_stations()
    eligible_ids = sorted(set(stations) & snow_station_ids())
    station_seasons: dict[str, dict[int, float]] = {}

    for index, station_id in enumerate(eligible_ids, 1):
        try:
            daily = load_station_csv(station_id)
        except Exception as error:
            print(f"Skipping {station_id}: {error}")
            continue
        seasons: dict[int, float] = {}
        for end_year in range(1941, 2021):
            dates = season_dates(end_year)
            valid = [daily[d] for d in dates if d in daily]
            if len(valid) >= math.ceil(0.80 * len(dates)):
                seasons[end_year] = sum(valid)
        if seasons:
            station_seasons[station_id] = seasons
        print(f"[{index}/{len(eligible_ids)}] {station_id}: {len(seasons)} usable seasons")

    panel = []
    for station_id, seasons in station_seasons.items():
        old_n = sum(1941 <= year <= 2000 for year in seasons)
        new_n = sum(2001 <= year <= 2020 for year in seasons)
        if old_n >= 30 and new_n >= 10:
            panel.append(station_id)
    if not panel:
        raise RuntimeError("No stations met the coverage rule; no result was generated.")

    # Each station receives equal weight in each period, avoiding extra weight
    # for stations that happen to have more complete years than other stations.
    station_rows = []
    for station_id in panel:
        seasons = station_seasons[station_id]
        old_values = [seasons[y] for y in range(1941, 2001) if y in seasons]
        new_values = [seasons[y] for y in range(2001, 2021) if y in seasons]
        old_station_mean, new_station_mean = mean(old_values), mean(new_values)
        station_rows.append({
            "station_id": station_id, "station_name": stations[station_id],
            "baseline_mean_inches": old_station_mean,
            "modern_mean_inches": new_station_mean,
            "change_inches": new_station_mean - old_station_mean,
            "baseline_seasons": len(old_values), "modern_seasons": len(new_values),
        })

    old_mean = mean([row["baseline_mean_inches"] for row in station_rows])
    new_mean = mean([row["modern_mean_inches"] for row in station_rows])
    difference = new_mean - old_mean
    percent = 100 * difference / old_mean if old_mean else None
    answer = "YES" if difference < 0 else "NO"

    annual = []
    for year in range(1941, 2021):
        values = [station_seasons[sid][year] for sid in panel if year in station_seasons[sid]]
        annual.append({"season": year, "mean_inches": round(mean(values), 2) if values else None,
                       "stations": len(values)})

    summary = {
        "answer": answer,
        "baseline": "1941–2000 seasons (November 1940–April 2000)",
        "modern": "2001–2020 seasons (November 2000–April 2020)",
        "baseline_mean_inches": round(old_mean, 2),
        "modern_mean_inches": round(new_mean, 2),
        "change_inches": round(difference, 2),
        "change_percent": round(percent, 1) if percent is not None else None,
        "eligible_stations": len(panel),
        "station_ids": panel,
        "annual": annual,
        "coverage_rule": "At least 80% of November–April days observed per station-season; stations need >=30 valid baseline seasons and >=10 valid modern seasons.",
        "averaging_rule": "Equal-weight average of eligible station-period means; annual values are equal-weight means of available eligible stations.",
        "units": "inches of snowfall per November–April season",
        "data_source": "NOAA NCEI GHCN-Daily, SNOW element, station CSV files",
        "source_url": "https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))

    with (OUT / "annual.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["season", "mean_inches", "stations"])
        writer.writeheader(); writer.writerows(annual)
    with (OUT / "station-means.csv").open("w", newline="") as output:
        fields = ["station_id", "station_name", "baseline_mean_inches", "modern_mean_inches",
                  "change_inches", "baseline_seasons", "modern_seasons"]
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in station_rows:
            writer.writerow({k: round(v, 2) if isinstance(v, float) else v for k, v in row.items()})

    # Annual regional snowfall time series.
    years = [row["season"] for row in annual if row["mean_inches"] is not None]
    values = [row["mean_inches"] for row in annual if row["mean_inches"] is not None]
    plt.figure(figsize=(11, 5.5))
    plt.plot(years, values, marker="o", markersize=2.5, linewidth=1.2)
    plt.axvspan(1941, 2000, alpha=.10, label="Earlier period")
    plt.axvspan(2001, 2020, alpha=.10, label="Recent period")
    plt.axhline(old_mean, linestyle="--", linewidth=1.2, label=f"1941–2000 mean: {old_mean:.1f} in")
    plt.axhline(new_mean, linestyle="--", linewidth=1.2, label=f"2001–2020 mean: {new_mean:.1f} in")
    plt.xlabel("Snow season ending year"); plt.ylabel("Mean station snowfall (inches)")
    plt.title("New England November–April snowfall by season")
    plt.legend(); plt.tight_layout(); plt.savefig(OUT / "snowfall-trend.png", dpi=180); plt.close()

    # Paired period means for every eligible station.
    station_rows.sort(key=lambda row: row["change_inches"])
    labels = [f'{r["station_name"]} ({r["station_id"]})' for r in station_rows]
    y = list(range(len(station_rows)))
    plt.figure(figsize=(11, max(6, .34 * len(station_rows))))
    plt.barh([v - .18 for v in y], [r["baseline_mean_inches"] for r in station_rows],
             height=.34, label="1941–2000")
    plt.barh([v + .18 for v in y], [r["modern_mean_inches"] for r in station_rows],
             height=.34, label="2001–2020")
    plt.yticks(y, labels, fontsize=7)
    plt.xlabel("Average November–April snowfall (inches)")
    plt.title("Station-by-station snowfall comparison")
    plt.legend(); plt.tight_layout(); plt.savefig(OUT / "station-comparison.png", dpi=180); plt.close()

    print(json.dumps({k: v for k, v in summary.items() if k not in {"annual", "station_ids"}}, indent=2))


if __name__ == "__main__":
    main()
