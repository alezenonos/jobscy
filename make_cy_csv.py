"""
Build occupations_cy.csv from Eurostat data for Cyprus.

Merges the ISCO-08 master occupation list (occupations_cy.json) with
employment and earnings data from Eurostat. Supports both live API
fetching and cached JSON files.

Output fields are in EUR and follow EU statistical classifications.

Usage:
    uv run python make_cy_csv.py                          # fetch from Eurostat API
    uv run python make_cy_csv.py --cached data/eurostat/  # use cached JSON files
    uv run python make_cy_csv.py --output occupations_cy.csv
"""

import argparse
import csv
import json
import os

from eurostat import (
    fetch_annual_earnings_by_occupation,
    fetch_earnings_by_occupation,
    fetch_employment_by_occupation,
)

FIELDNAMES = [
    "title",
    "category",
    "slug",
    "isco_code",
    "mean_pay_annual_eur",
    "mean_pay_hourly_eur",
    "median_pay_annual_eur",
    "p10_pay_annual_eur",
    "p90_pay_annual_eur",
    "entry_education",
    "employment_thousands",
    "employment_estimated",
    "year_employment",
    "year_earnings",
]


def load_occupations(path="occupations_cy.json"):
    """Load the Cyprus master occupation list."""
    with open(path) as f:
        return json.load(f)


def fetch_eurostat_data(geo="CY", client=None, verbose=False):
    """Fetch employment and earnings data from Eurostat API.

    Returns:
        Tuple of (employment_data, earnings_data).
    """
    employment = fetch_employment_by_occupation(geo=geo, client=client)
    earnings = fetch_earnings_by_occupation(geo=geo, client=client, verbose=verbose)
    annual = fetch_annual_earnings_by_occupation(geo=geo, client=client, verbose=verbose)
    for row in earnings:
        if row["isco_code"] in annual:
            row["annual_earnings_eur"] = annual[row["isco_code"]]
    return employment, earnings


def load_cached_data(cache_dir):
    """Load previously saved Eurostat data from JSON files.

    Args:
        cache_dir: Directory containing employment.json and earnings.json.

    Returns:
        Tuple of (employment_data, earnings_data).
    """
    emp_path = os.path.join(cache_dir, "employment.json")
    earn_path = os.path.join(cache_dir, "earnings.json")

    with open(emp_path) as f:
        employment = json.load(f)
    with open(earn_path) as f:
        earnings = json.load(f)

    return employment, earnings


def save_cached_data(employment, earnings, cache_dir):
    """Save fetched Eurostat data to JSON files for future use."""
    os.makedirs(cache_dir, exist_ok=True)

    with open(os.path.join(cache_dir, "employment.json"), "w") as f:
        json.dump(employment, f, indent=2)
    with open(os.path.join(cache_dir, "earnings.json"), "w") as f:
        json.dump(earnings, f, indent=2)


def _residual_employment(code, parent, emp_by_code, occupations):
    """Estimate a suppressed 2-digit employment value from its 1-digit parent.

    Returns ``parent total - sum of the known siblings`` (floored at 0), split
    evenly if several siblings are missing. Returns {} when the parent total is
    unavailable.
    """
    parent_row = emp_by_code.get(parent)
    if not parent_row or parent_row.get("employment_thousands") in (None, ""):
        return {}
    siblings = [o["isco_code"] for o in occupations if o.get("isco_parent", o["isco_code"][:3]) == parent]
    known = sum(emp_by_code[c]["employment_thousands"] for c in siblings if c in emp_by_code)
    missing = [c for c in siblings if c not in emp_by_code] or [code]
    residual = max(0.0, parent_row["employment_thousands"] - known) / len(missing)
    return {"employment_thousands": round(residual, 1), "year": parent_row.get("year", "")}


HOURS_PER_YEAR = 2080  # fallback when SES annual earnings are unavailable


def _annual_pay(earn):
    """Annual mean, median, P10 and P90 pay for one ISCO 1-digit group.

    The mean is SES mean annual earnings (includes 13th salary and bonuses)
    when available, else hourly mean x 2080. The median and deciles are only
    published as hourly figures, so they are annualised with the same
    annual/hourly ratio as the mean for that group.
    """
    hourly = earn.get("hourly_earnings_eur")
    if not hourly:
        return {}
    annual = earn.get("annual_earnings_eur") or hourly * HOURS_PER_YEAR
    factor = annual / hourly
    out = {"mean": round(annual)}
    for key, src in (("median", "median_hourly_eur"), ("p10", "p10_hourly_eur"), ("p90", "p90_hourly_eur")):
        if earn.get(src):
            out[key] = round(earn[src] * factor)
    return out


def build_csv_rows(occupations, employment, earnings):
    """Build CSV rows by merging occupation list with Eurostat data.

    Each 2-digit ISCO occupation is matched to its parent 1-digit group
    for earnings data (since Eurostat SES only provides 1-digit earnings),
    and to its own 2-digit entry for employment data.

    Args:
        occupations: List from occupations_cy.json.
        employment: Output of fetch_employment_by_occupation().
        earnings: Output of fetch_earnings_by_occupation().

    Returns:
        List of dicts matching FIELDNAMES.
    """
    # Index employment by ISCO code
    emp_by_code = {}
    for row in employment:
        emp_by_code[row["isco_code"]] = row

    # Index earnings by ISCO 1-digit code
    earn_by_code = {}
    for row in earnings:
        earn_by_code[row["isco_code"]] = row

    # Education mapping for ISCO major groups (typical for Cyprus/EU)
    # Based on ISCED 2011 typical requirements per ISCO group
    isco_education = {
        "OC1": "Bachelor's degree or higher",
        "OC2": "Bachelor's degree or higher",
        "OC3": "Short-cycle tertiary / Associate",
        "OC4": "Upper secondary / Vocational",
        "OC5": "Upper secondary / Vocational",
        "OC6": "Upper secondary / Vocational",
        "OC7": "Upper secondary / Vocational",
        "OC8": "Lower secondary or below",
        "OC9": "Lower secondary or below",
        "OC0": "Varies (military)",
    }

    rows = []
    for occ in occupations:
        code = occ["isco_code"]
        parent = occ.get("isco_parent", code[:3])

        # Employment: exact 2-digit match. When Eurostat suppresses the
        # 2-digit value, estimate it as the residual of the 1-digit total
        # (never the whole parent total, which would double-count siblings).
        emp = emp_by_code.get(code)
        estimated = False
        if emp is None:
            emp = _residual_employment(code, parent, emp_by_code, occupations)
            estimated = bool(emp)

        # Earnings: always from 1-digit (SES limitation)
        earn = earn_by_code.get(parent, {})

        pay = _annual_pay(earn)
        rows.append(
            {
                "title": occ["title"],
                "category": occ["category"],
                "slug": occ["slug"],
                "isco_code": code,
                "mean_pay_annual_eur": pay.get("mean", ""),
                "mean_pay_hourly_eur": f"{earn['hourly_earnings_eur']:.2f}" if earn.get("hourly_earnings_eur") else "",
                "median_pay_annual_eur": pay.get("median", ""),
                "p10_pay_annual_eur": pay.get("p10", ""),
                "p90_pay_annual_eur": pay.get("p90", ""),
                "entry_education": isco_education.get(parent, ""),
                "employment_thousands": emp.get("employment_thousands", ""),
                "employment_estimated": "yes" if estimated else "",
                "year_employment": emp.get("year", ""),
                "year_earnings": earn.get("year", ""),
            }
        )

    return rows


def main():
    parser = argparse.ArgumentParser(description="Build Cyprus occupations CSV from Eurostat data")
    parser.add_argument("--output", default="occupations_cy.csv", help="Output CSV file")
    parser.add_argument("--occupations", default="occupations_cy.json", help="Master occupation list")
    parser.add_argument("--cached", help="Directory with cached employment.json and earnings.json")
    parser.add_argument("--save-cache", help="Save fetched data to this directory for future use")
    parser.add_argument("--geo", default="CY", help="Country code (default: CY)")
    parser.add_argument("--verbose", action="store_true", help="Print API URLs and debug info")
    args = parser.parse_args()

    # Load master occupation list
    occupations = load_occupations(args.occupations)

    # Get Eurostat data
    if args.cached:
        print(f"Loading cached data from {args.cached}")
        employment, earnings = load_cached_data(args.cached)
    else:
        print(f"Fetching data from Eurostat for {args.geo}...")
        employment, earnings = fetch_eurostat_data(geo=args.geo, verbose=args.verbose)

    if not earnings:
        print("WARNING: No earnings data returned from Eurostat.")
        print("  Run 'uv run python diagnose_eurostat.py' to investigate.")

    if args.save_cache:
        save_cached_data(employment, earnings, args.save_cache)
        print(f"Cached data saved to {args.save_cache}/")

    # Build CSV rows
    rows = build_csv_rows(occupations, employment, earnings)

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.output}")

    # Summary
    with_emp = sum(1 for r in rows if r["employment_thousands"])
    estimated = [r["isco_code"] for r in rows if r["employment_estimated"]]
    if estimated:
        print(f"  Employment estimated from 1-digit residual: {', '.join(estimated)}")
    with_pay = sum(1 for r in rows if r["mean_pay_annual_eur"])
    print(f"  With employment data: {with_emp}/{len(rows)}")
    print(f"  With earnings data: {with_pay}/{len(rows)}")

    if rows:
        # Show one sample per ISCO major group to verify distinct earnings
        print("\nSample rows (one per major group):")
        seen_parents = set()
        for r in rows:
            parent = r["isco_code"][:3]
            if parent in seen_parents:
                continue
            seen_parents.add(parent)
            pay = f"€{r['mean_pay_annual_eur']}" if r["mean_pay_annual_eur"] else "—"
            emp = f"{r['employment_thousands']}K" if r["employment_thousands"] else "—"
            print(f"  {r['isco_code']} {r['title']}: {pay}/yr, {emp} employed")


if __name__ == "__main__":
    main()
