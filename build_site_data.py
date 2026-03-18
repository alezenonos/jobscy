"""
Build a compact JSON for the website by merging CSV stats with AI exposure scores.

Supports both legacy BLS format (occupations.csv) and Cyprus format
(occupations_cy.csv). Auto-detects format based on CSV column names.

Reads scores.json (AI exposure ratings) and writes site/data.json
for the treemap visualization.

Usage:
    uv run python build_site_data.py                              # auto-detect
    uv run python build_site_data.py --csv occupations_cy.csv     # explicit Cyprus
    uv run python build_site_data.py --csv occupations.csv        # explicit BLS
"""

import argparse
import csv
import json
import os


def detect_format(fieldnames):
    """Detect whether a CSV is in Cyprus or BLS format based on column names."""
    if "isco_code" in fieldnames:
        return "cyprus"
    if "soc_code" in fieldnames:
        return "bls"
    return "unknown"


def merge_bls(rows, scores):
    """Merge BLS-format CSV rows with scores."""
    data = []
    for row in rows:
        slug = row["slug"]
        score = scores.get(slug, {})
        data.append(
            {
                "title": row["title"],
                "slug": slug,
                "category": row["category"],
                "pay": int(row["median_pay_annual"]) if row["median_pay_annual"] else None,
                "jobs": int(row["num_jobs_2024"]) if row["num_jobs_2024"] else None,
                "outlook": int(row["outlook_pct"]) if row.get("outlook_pct") else None,
                "outlook_desc": row.get("outlook_desc", ""),
                "education": row.get("entry_education", ""),
                "exposure": score.get("exposure"),
                "exposure_rationale": score.get("rationale"),
                "url": row.get("url", ""),
            }
        )
    return data


def merge_cyprus(rows, scores):
    """Merge Cyprus-format CSV rows with scores."""
    data = []
    for row in rows:
        slug = row["slug"]
        score = scores.get(slug, {})

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
                "exposure": score.get("exposure"),
                "exposure_rationale": score.get("rationale"),
                "year_employment": row.get("year_employment", ""),
                "year_earnings": row.get("year_earnings", ""),
            }
        )
    return data


def main():
    parser = argparse.ArgumentParser(description="Build site data JSON from CSV + scores")
    parser.add_argument("--csv", default=None, help="Input CSV file (auto-detects format)")
    parser.add_argument("--scores", default="scores.json", help="Scores JSON file")
    parser.add_argument("--output", default="site/data.json", help="Output JSON file")
    args = parser.parse_args()

    # Auto-detect CSV file if not specified
    csv_path = args.csv
    if csv_path is None:
        if os.path.exists("occupations_cy.csv"):
            csv_path = "occupations_cy.csv"
        elif os.path.exists("occupations.csv"):
            csv_path = "occupations.csv"
        else:
            print("Error: no occupations CSV found. Run make_cy_csv.py or make_csv.py first.")
            return

    # Load AI exposure scores
    scores = {}
    if os.path.exists(args.scores):
        with open(args.scores) as f:
            scores_list = json.load(f)
        scores = {s["slug"]: s for s in scores_list}

    # Load CSV stats
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Detect format and merge
    fmt = detect_format(fieldnames)
    if fmt == "cyprus":
        data = merge_cyprus(rows, scores)
        print("Detected Cyprus format (ISCO-08, EUR)")
    elif fmt == "bls":
        data = merge_bls(rows, scores)
        print("Detected BLS format (SOC, USD)")
    else:
        print("Warning: unknown CSV format, attempting Cyprus merge")
        data = merge_cyprus(rows, scores)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(data, f)

    print(f"Wrote {len(data)} occupations to {args.output}")
    total_jobs = sum(d["jobs"] for d in data if d["jobs"])
    print(f"Total jobs represented: {total_jobs:,}")


if __name__ == "__main__":
    main()
