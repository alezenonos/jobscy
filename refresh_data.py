"""
Helpers for the scheduled data refresh (.github/workflows/refresh-data.yml).

    uv run python refresh_data.py wage-index            # update data/cache/wage_index.json from Eurostat
    uv run python refresh_data.py eu-compare            # update data/cache/eu_compare.json (EU27 jobs, EU/Greece pay)
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


EU_COMPARE_FILE = "eu_compare.json"
EU_GEO = "EU27_2020"
PAY_GEOS = ("CY", EU_GEO, "EL")
EU_EMPLOYMENT_KEY = {"unit": "THS_PER", "sex": "T", "age": "Y_GE15"}
EU_EARNINGS_KEY = {"sex": "T", "indic_se": "ERN", "age": "TOTAL", "sizeclas": "GE10"}
# Each SES wave has its own annual-earnings table (earn_ses22_28 for 2022).
EU_EARNINGS_DATASET = "earn_ses22_28"


def flatten_json_stat(data):
    """Turn a Eurostat JSON-stat response into a list of {dimension: code, ..., "value": v}."""
    dims = data.get("id", [])
    sizes = data.get("size", [])
    cats = []
    for d in dims:
        index = data["dimension"][d]["category"]["index"]
        if isinstance(index, list):
            cats.append(index)
        else:
            codes = [None] * len(index)
            for code, pos in index.items():
                codes[pos] = code
            cats.append(codes)
    values = data.get("value", {})
    if isinstance(values, list):
        values = {i: v for i, v in enumerate(values) if v is not None}
    rows = []
    for pos, value in values.items():
        n = int(pos)
        row = {}
        for i in range(len(dims) - 1, -1, -1):
            row[dims[i]] = cats[i][n % sizes[i]]
            n //= sizes[i]
        row["value"] = value
        rows.append(row)
    return rows


def _keep_isco(code):
    # Keep single groups (OC1, OC21) and the total; drop ranges such as OC1-5.
    return code == "TOTAL" or (code.startswith("OC") and "-" not in code)


def fetch_eu_compare(fetch=fetch_json_stat):
    """Fetch EU27 employment by 2-digit group and CY/EU27/Greece pay by major group."""
    emp_rows = flatten_json_stat(
        fetch("lfsa_egai2d", params={"freq": "A", **EU_EMPLOYMENT_KEY, "geo": EU_GEO, "lastTimePeriod": 1})
    )
    if not emp_rows:
        raise RuntimeError("Eurostat returned no EU employment values")
    emp_year = max(r["time"] for r in emp_rows)
    thousands = {
        r["isco08"]: round(float(r["value"]), 1) for r in emp_rows if r["time"] == emp_year and _keep_isco(r["isco08"])
    }

    earnings = {}
    pay_year = None
    for unit in ("EUR", "PPS"):
        rows = flatten_json_stat(
            fetch(EU_EARNINGS_DATASET, params={"freq": "A", **EU_EARNINGS_KEY, "unit": unit, "geo": list(PAY_GEOS)})
        )
        if not rows:
            raise RuntimeError(f"Eurostat returned no {unit} earnings values")
        pay_year = max(r["time"] for r in rows)
        by_geo = {}
        for r in rows:
            if r["time"] == pay_year and _keep_isco(r["isco08"]):
                by_geo.setdefault(r["geo"], {})[r["isco08"]] = float(r["value"])
        earnings[unit] = {g: dict(sorted(by_geo.get(g, {}).items())) for g in PAY_GEOS}

    return {
        "employment": {
            "dataset": "lfsa_egai2d",
            "geo": EU_GEO,
            "year": emp_year,
            **EU_EMPLOYMENT_KEY,
            "thousands": dict(sorted(thousands.items())),
        },
        "earnings": {
            "dataset": EU_EARNINGS_DATASET,
            "year": pay_year,
            "indic_se": "ERN",
            "sizeclas": "GE10",
            **earnings,
        },
    }


def update_eu_compare(cache_dir=CACHE_DIR, fetch=fetch_json_stat):
    """Fetch the EU comparison data and write it to the cache. Returns the new data."""
    out = fetch_eu_compare(fetch)
    with open(os.path.join(cache_dir, EU_COMPARE_FILE), "w") as f:
        json.dump(out, f, indent=2)
    return out


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
    e = sub.add_parser("eu-compare", help="Update data/cache/eu_compare.json from Eurostat")
    e.add_argument("--cache-dir", default=CACHE_DIR)
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

    if args.cmd == "eu-compare":
        try:
            out = update_eu_compare(args.cache_dir, fetch=fetch_json_stat)
        except Exception as e:  # noqa: BLE001 - keep the cached file so the rest of the refresh still runs
            print(f"::warning::EU comparison not updated, keeping the cached values: {e}")
            return 0
        print(f"EU comparison: jobs {out['employment']['year']}, pay {out['earnings']['year']}")
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
