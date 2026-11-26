"""
Build cagr.json: historical employment growth (CAGR) per ISCO-08 code for Cyprus.

Uses the Eurostat LFSA_EGAI2D multi-year series. The output grounds the
LLM growth-outlook scoring in score_outlook.py (which reads cagr.json by default).

Usage:
    uv run python make_cagr.py                                   # fetch from Eurostat
    uv run python make_cagr.py --save-cache data/cache           # fetch and cache the series
    uv run python make_cagr.py --cached data/cache               # use the cached series
    uv run python make_cagr.py --years 10 --output cagr.json
"""

import argparse
import json
import os

from eurostat import compute_cagr_from_series, fetch_employment_multi_year

HISTORY_CACHE = "employment_history.json"


def build_cagr(history, min_years=3):
    """Compute CAGR per ISCO code from {code: {year: employment_thousands}}.

    Codes with fewer than ``min_years`` observations are skipped, because a
    growth rate from two noisy LFS points is not meaningful.

    Returns:
        Dict mapping isco_code -> {"cagr", "start_year", "end_year", "n_obs"}.
    """
    result = {}
    for code, series in sorted(history.items()):
        if len(series) < min_years:
            continue
        cagr, start_year, end_year = compute_cagr_from_series(series)
        if cagr is None:
            continue
        result[code] = {
            "cagr": round(cagr, 2),
            "start_year": start_year,
            "end_year": end_year,
            "n_obs": len(series),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description="Build historical employment CAGR per ISCO-08 code")
    parser.add_argument("--output", default="cagr.json")
    parser.add_argument("--geo", default="CY")
    parser.add_argument("--years", type=int, default=10, help="Number of most recent years to fetch")
    parser.add_argument("--min-years", type=int, default=3, help="Minimum observations per code")
    parser.add_argument("--cached", help=f"Directory containing {HISTORY_CACHE}")
    parser.add_argument("--save-cache", help=f"Save the fetched series to this directory as {HISTORY_CACHE}")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.cached:
        with open(os.path.join(args.cached, HISTORY_CACHE)) as f:
            history = json.load(f)
        print(f"Loaded employment history from {args.cached}")
    else:
        print(f"Fetching {args.years} years of employment for {args.geo} from Eurostat...")
        history = fetch_employment_multi_year(geo=args.geo, last_n=args.years, verbose=args.verbose)

    if args.save_cache:
        os.makedirs(args.save_cache, exist_ok=True)
        with open(os.path.join(args.save_cache, HISTORY_CACHE), "w") as f:
            json.dump(history, f, indent=2, sort_keys=True)
        print(f"Saved employment history to {args.save_cache}/{HISTORY_CACHE}")

    cagr = build_cagr(history, min_years=args.min_years)
    with open(args.output, "w") as f:
        json.dump(cagr, f, indent=2)
    print(f"Wrote CAGR for {len(cagr)} ISCO codes to {args.output}")


if __name__ == "__main__":
    main()
