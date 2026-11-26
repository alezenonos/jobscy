"""
Helpers for the scheduled data refresh (.github/workflows/refresh-data.yml).

    uv run python refresh_data.py wage-index            # update data/cache/wage_index.json from Eurostat
    uv run python refresh_data.py report --old old.json # Markdown summary of what changed in site/data.json

The refresh workflow fetches Eurostat employment, earnings, employment history
and the wage index, rebuilds site/data.json and opens a pull request with the
report below. It never calls the LLM: when the historical growth behind an
outlook score changes, the report lists those occupations so the outlook can be
re-scored by hand with score_outlook.py.
"""

import argparse
import json
import os
import sys

from eurostat import fetch_json_stat
from forecasts import CACHE_DIR

WAGE_INDEX_FILE = "wage_index.json"
# Filters are passed by name to the JSON-stat API, so they don't depend on the
# dataset's dimension order (a positional SDMX key got 400 Bad Request).
WAGE_INDEX_KEY = {"unit": "I20", "lcstruct": "D11", "nace_r2": "B-S"}


def parse_wage_index(data):
    """Turn a Eurostat JSON-stat response into {year: index}, skipping missing values.

    Every filter except time selects a single value, so an observation's flat
    position is its position on the time dimension.
    """
    years = data.get("dimension", {}).get("time", {}).get("category", {}).get("index", {})
    values = data.get("value", {})
    if isinstance(values, list):
        values = dict(enumerate(values))
    index = {}
    for year, pos in years.items():
        value = values.get(str(pos), values.get(pos))
        if value is None:
            continue
        try:
            index[str(year)] = round(float(value), 1)
        except (TypeError, ValueError):
            continue
    return dict(sorted(index.items()))


def update_wage_index(cache_dir=CACHE_DIR, geo="CY", fetch=fetch_json_stat):
    """Fetch the labour cost index and merge it into the cached file. Returns the new index."""
    params = {"freq": "A", **WAGE_INDEX_KEY, "geo": geo}
    fetched = parse_wage_index(fetch("lc_lci_r2_a", params=params))
    if not fetched:
        raise RuntimeError("Eurostat returned no wage index values")
    path = os.path.join(cache_dir, WAGE_INDEX_FILE)
    current = {}
    if os.path.exists(path):
        with open(path) as f:
            current = json.load(f)
    index = {**current.get("index", {}), **fetched}
    out = {"dataset": "lc_lci_r2_a", **WAGE_INDEX_KEY, "geo": geo, "index": dict(sorted(index.items()))}
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    return out["index"]


def _fmt_jobs(n):
    return "—" if n is None else f"{n / 1000:.1f}k"


def build_report(old, new):
    """Return a Markdown summary of the differences between two site/data.json lists."""
    old_by = {d["slug"]: d for d in old}
    lines = []

    def years(data, key):
        return sorted({str(d.get(key)) for d in data if d.get(key)})

    for label, key in (("Employment (LFS)", "year_employment"), ("Pay survey (SES)", "pay_survey_year")):
        before, after = years(old, key), years(new, key)
        if before != after:
            lines.append(f"- **{label}:** {', '.join(before) or '—'} → {', '.join(after)}")
    before, after = years(old, "pay_year"), years(new, "pay_year")
    if before != after:
        lines.append(f"- **Pay estimate year:** {', '.join(before) or '—'} → {', '.join(after)}")

    total_old = sum(d.get("jobs") or 0 for d in old)
    total_new = sum(d.get("jobs") or 0 for d in new)
    if total_old != total_new:
        lines.append(f"- **Total jobs:** {total_old:,} → {total_new:,}")

    changed = []
    for d in new:
        o = old_by.get(d["slug"], {})
        if o.get("jobs") != d.get("jobs") or o.get("pay") != d.get("pay"):
            changed.append(
                f"| {d['title']} | {_fmt_jobs(o.get('jobs'))} → {_fmt_jobs(d.get('jobs'))} "
                f"| €{o.get('pay') or 0:,} → €{d.get('pay') or 0:,} |"
            )
    if changed:
        lines += [
            "",
            f"**{len(changed)} occupations changed:**",
            "",
            "| Occupation | Jobs | Average pay |",
            "|---|---|---|",
        ]
        lines += changed

    if not lines:
        return "No changes to the published data."
    return "\n".join(lines)


def stale_outlook(new_cagr, outlook_scores, occupations):
    """Occupations whose cached outlook used a different historical CAGR than cagr.json now has."""
    out = []
    for occ in occupations:
        cagr = (new_cagr.get(occ.get("isco_code")) or {}).get("cagr")
        cached = outlook_scores.get(occ["slug"], {})
        if cagr is not None and cached.get("historical_cagr") != cagr:
            out.append(occ["title"])
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("wage-index", help="Update data/cache/wage_index.json from Eurostat")
    w.add_argument("--cache-dir", default=CACHE_DIR)
    r = sub.add_parser("report", help="Summarise changes in site/data.json")
    r.add_argument("--old", required=True, help="site/data.json before the refresh")
    r.add_argument("--new", default="site/data.json")
    r.add_argument("--outlook", default="outlook_scores.json")
    r.add_argument("--cagr", default="cagr.json")
    r.add_argument("--occupations", default="occupations_cy.json")
    args = parser.parse_args(argv)

    if args.cmd == "wage-index":
        try:
            index = update_wage_index(args.cache_dir, fetch=fetch_json_stat)
        except Exception as e:  # noqa: BLE001 - keep the cached index so the rest of the refresh still runs
            print(f"::warning::Wage index not updated, keeping the cached values: {e}")
            return 0
        latest = max(index)
        print(f"Wage index: {len(index)} years, latest {latest} = {index[latest]}")
        return 0

    with open(args.old) as f:
        old = json.load(f)
    with open(args.new) as f:
        new = json.load(f)
    with open(args.outlook) as f:
        outlook = {s["slug"]: s for s in json.load(f)}
    report = build_report(old, new)
    if os.path.exists(args.cagr) and os.path.exists(args.occupations):
        with open(args.cagr) as f:
            cagr = json.load(f)
        with open(args.occupations) as f:
            occupations = json.load(f)
        stale = stale_outlook(cagr, outlook, occupations)
        if stale:
            report = ("" if report.startswith("No changes") else report + "\n\n") + (
                f"**Growth outlook needs re-scoring for {len(stale)} occupations** (historical growth in "
                "`cagr.json` changed). Run `uv run python score_outlook.py` with `OPENROUTER_API_KEY` set, then "
                "`uv run python build_site_data.py`, and push to this branch:\n\n" + "\n".join(f"- {t}" for t in stale)
            )
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
