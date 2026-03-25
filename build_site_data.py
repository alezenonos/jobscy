"""
Build a compact JSON for the website by merging CSV stats with AI exposure scores.

Reads occupations_cy.csv (Cyprus ISCO-08 data) and scores.json (AI exposure
ratings) and writes site/data.json for the treemap visualisation.

Usage:
    uv run python build_site_data.py
    uv run python build_site_data.py --csv occupations_cy.csv
"""

import argparse
import csv
import json
import os


def merge_cyprus(rows, scores, outlook=None):
    """Merge Cyprus-format CSV rows with scores and outlook data."""
    outlook = outlook or {}
    data = []
    for row in rows:
        slug = row["slug"]
        score = scores.get(slug, {})
        outl = outlook.get(slug, {})

        # Employment in thousands → absolute number for treemap sizing
        emp_k = row.get("employment_thousands", "")
        jobs = round(float(emp_k) * 1000) if emp_k else None

        data.append(
            {
                "title": row["title"],
                "slug": slug,
                "category": row["category"],
                "isco_code": row.get("isco_code", ""),
                "pay": int(row["median_pay_annual_eur"]) if row.get("median_pay_annual_eur") else None,
                "pay_hourly": float(row["median_pay_hourly_eur"]) if row.get("median_pay_hourly_eur") else None,
                "jobs": jobs,
                "education": row.get("entry_education", ""),
                "outlook": outl.get("outlook"),
                "outlook_rationale": outl.get("outlook_rationale", outl.get("rationale", "")),
                "exposure": score.get("exposure"),
                "exposure_rationale": score.get("rationale"),
                "year_employment": row.get("year_employment", ""),
                "year_earnings": row.get("year_earnings", ""),
            }
        )
    return data


def main():
    parser = argparse.ArgumentParser(description="Build site data JSON from CSV + scores")
    parser.add_argument("--csv", default=None, help="Input CSV file (default: occupations_cy.csv)")
    parser.add_argument("--scores", default="scores.json", help="Scores JSON file")
    parser.add_argument("--outlook", default="outlook_scores.json", help="Outlook scores JSON file")
    parser.add_argument("--output", default="site/data.json", help="Output JSON file")
    args = parser.parse_args()

    csv_path = args.csv or "occupations_cy.csv"

    # Load AI exposure scores
    scores = {}
    if os.path.exists(args.scores):
        with open(args.scores) as f:
            scores_list = json.load(f)
        scores = {s["slug"]: s for s in scores_list}

    # Load outlook scores
    outlook = {}
    if os.path.exists(args.outlook):
        with open(args.outlook) as f:
            outlook_list = json.load(f)
        outlook = {s["slug"]: s for s in outlook_list}

    # Load CSV stats
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    data = merge_cyprus(rows, scores, outlook)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(data, f)

    print(f"Wrote {len(data)} occupations to {args.output}")
    total_jobs = sum(d["jobs"] for d in data if d["jobs"])
    print(f"Total jobs represented: {total_jobs:,}")


if __name__ == "__main__":
    main()
