#!/usr/bin/env python3
"""Download GHCN-Daily station files and compare New England snowfall.

The script downloads only station files for the six New England states; it
never stores the full GHCN archive in the repository. Snowfall seasons are
November-April and are labelled by the year in which April occurs.
"""
from __future__ import annotations
import csv, json, math, os, re, urllib.request
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"              # ignored by git
OUT = ROOT / "docs"
BASE_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily"
STATES = {"CT", "ME", "MA", "NH", "RI", "VT"}


def fetch(url: str, dest: Path) -> None:
    """Download URL to dest unless a local copy already exists."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        print(f"Downloading {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "NewEnglandSnowfallStudy/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response, dest.open("wb") as f:
            f.write(response.read())


def stations() -> list[tuple[str, str, float, float]]:
    """Return station ID, name, latitude and longitude for New England."""
    path = DATA / "ghcnd-stations.txt"
    fetch(f"{BASE_URL}/ghcnd-stations.txt", path)
    result = []
    for line in path.read_text(errors="replace").splitlines():
        sid = line[0:11].strip()
        state = line[38:40].strip()
        if state in STATES and sid.startswith("US"):
            try:
                lat, lon = float(line[12:20]), float(line[21:30])
            except ValueError:
                continue
            result.append((sid, line[41:71].strip(), lat, lon))
    return result


def parse_dly(path: Path, sid: str) -> dict[str, dict[int, float]]:
    """Parse SNOW records; return date->value (inches) by calendar date."""
    values: dict[str, dict[int, float]] = defaultdict(dict)
    for line in path.read_text(errors="replace").splitlines():
        if len(line) < 269 or line[0:11] != sid or line[17:21] != "SNOW":
            continue
        year, month = int(line[11:15]), int(line[15:17])
        if not (1939 <= year <= 2020):
            continue
        for day in range(1, 32):
            pos = 21 + (day - 1) * 8
            chunk = line[pos:pos+8]
            if len(chunk) < 8 or not chunk[:5].strip():
                continue
            try:
                raw = int(chunk[:5])
            except ValueError:
                continue
            # GHCN-Daily SNOW is reported in mm; -9999 denotes missing.
            # Reject observations carrying a nonblank quality flag.
            if raw == -9999 or chunk[6] != " ":
                continue
            # Reject impossible calendar dates (e.g. February 30).
            import calendar
            if day > calendar.monthrange(year, month)[1]:
                continue
            # GHCN-Daily values are tenths of millimetres.
            values[f"{year:04d}-{month:02d}"][day] = raw / 10 / 25.4
    return values


def main() -> None:
    DATA.mkdir(exist_ok=True)
    meta = stations()
    station_seasons: dict[str, dict[int, float]] = {}
    station_names = {}
    for i, (sid, name, lat, lon) in enumerate(meta, 1):
        local = DATA / f"{sid}.dly"
        try:
            fetch(f"{BASE_URL}/all/{sid}.dly", local)
            daily = parse_dly(local, sid)
        except Exception as exc:
            print(f"Skipping {sid}: {exc}")
            continue
        station_names[sid] = name
        # Seasons 1940-41 through 2019-20; label by spring year.
        seasons = {}
        for end_year in range(1941, 2021):
            dates = []
            for y, m in ((end_year - 1, 11), (end_year - 1, 12),
                         (end_year, 1), (end_year, 2), (end_year, 3), (end_year, 4)):
                import calendar
                n = calendar.monthrange(y, m)[1]
                for d in range(1, n + 1):
                    dates.append((f"{y:04d}-{m:02d}", d))
            observed = [daily[k][d] for k, d in dates if d in daily.get(k, {})]
            # At least 80% of all season-days must have valid SNOW data.
            if len(observed) >= math.ceil(0.80 * len(dates)):
                seasons[end_year] = sum(observed)
        if seasons:
            station_seasons[sid] = seasons
        print(f"[{i}/{len(meta)}] {sid}: {len(seasons)} usable seasons")

    # Balanced station panel: require >=30 baseline and >=10 modern seasons.
    eligible = []
    for sid, seasons in station_seasons.items():
        n_old = sum(1941 <= y <= 2000 for y in seasons)
        n_new = sum(2001 <= y <= 2020 for y in seasons)
        if n_old >= 30 and n_new >= 10:
            eligible.append(sid)
    if not eligible:
        raise RuntimeError("No stations met the balanced-panel coverage rule. Review coverage threshold.")

    annual = []
    for year in range(1941, 2021):
        vals = [station_seasons[s][year] for s in eligible if year in station_seasons[s]]
        annual.append({"season": year, "mean_inches": sum(vals)/len(vals) if vals else None,
                       "stations": len(vals)})
    old = [station_seasons[s][y] for s in eligible for y in range(1941, 2001) if y in station_seasons[s]]
    new = [station_seasons[s][y] for s in eligible for y in range(2001, 2021) if y in station_seasons[s]]
    old_mean, new_mean = sum(old)/len(old), sum(new)/len(new)
    change = new_mean - old_mean
    pct = 100 * change / old_mean if old_mean else None
    answer = "YES" if change < 0 else "NO"

    summary = {
        "answer": answer, "baseline": "1941–2000 seasons", "modern": "2001–2020 seasons",
        "baseline_mean_inches": round(old_mean, 2), "modern_mean_inches": round(new_mean, 2),
        "change_inches": round(change, 2), "change_percent": round(pct, 1) if pct is not None else None,
        "eligible_stations": len(eligible), "station_ids": eligible,
        "annual": annual, "baseline_station_season_n": len(old), "modern_station_season_n": len(new),
        "coverage_rule": "At least 80% of November–April days observed per station-season; balanced stations need >=30 baseline and >=10 modern seasons.",
        "units": "inches of snowfall per November–April season",
        "data_source": "NOAA NCEI GHCN-Daily, SNOW element"
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    with (OUT / "annual.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["season", "mean_inches", "stations"])
        w.writeheader(); w.writerows(annual)

    years = [r["season"] for r in annual if r["mean_inches"] is not None]
    vals = [r["mean_inches"] for r in annual if r["mean_inches"] is not None]
    plt.figure(figsize=(10, 5))
    plt.plot(years, vals, linewidth=1.2, marker="o", markersize=2.5)
    plt.axvspan(1941, 2000, alpha=.10, label="Earlier period")
    plt.axvspan(2001, 2020, alpha=.10, label="Recent period")
    plt.axhline(old_mean, linestyle="--", linewidth=1, label=f"Earlier mean: {old_mean:.1f} in")
    plt.axhline(new_mean, linestyle="--", linewidth=1, label=f"Recent mean: {new_mean:.1f} in")
    plt.xlabel("Snow season ending year"); plt.ylabel("Mean station snowfall (inches)")
    plt.title("New England November–April snowfall")
    plt.legend(); plt.tight_layout(); plt.savefig(OUT / "snowfall-trend.png", dpi=180); plt.close()

    with (OUT / "station-means.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["station_id", "station_name", "1941-2000_mean_in", "2001-2020_mean_in", "change_in"])
        for sid in eligible:
            a = [station_seasons[sid][y] for y in range(1941, 2001) if y in station_seasons[sid]]
            b = [station_seasons[sid][y] for y in range(2001, 2021) if y in station_seasons[sid]]
            ma, mb = sum(a)/len(a), sum(b)/len(b)
            w.writerow([sid, station_names.get(sid, ""), round(ma, 2), round(mb, 2), round(mb-ma, 2)])
    print(json.dumps({k:v for k,v in summary.items() if k not in {"annual", "station_ids"}}, indent=2))

if __name__ == "__main__":
    main()
