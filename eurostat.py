"""
Fetch Cyprus labour market data from the Eurostat REST API.

Provides functions to retrieve employment counts by ISCO-08 occupation
and earnings data, filtered to Cyprus (geo=CY).

Eurostat SDMX 2.1 API docs:
    https://wikis.ec.europa.eu/display/EUROSTATHELP/Transition+to+the+new+dissemination+chain

Key datasets:
    LFSA_EGAI2D  — Employment by ISCO-08 2-digit occupation
    earn_ses_hourly — Mean gross hourly earnings by ISCO-08 1-digit

Note: Eurostat SDMX 2.1 ignores dimension filters passed as query parameters.
Filtering must use path-based keys: /data/{dataset}/{dim1}.{dim2}...{dimN}

Usage:
    uv run python eurostat.py                     # fetch and print Cyprus data
    uv run python eurostat.py --dataset LFSA_EGAI2D --output employment.csv
"""

import argparse
import csv
import io
import json

import httpx

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data"
JSON_STAT_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# ISCO-08 major groups (1-digit) used across Eurostat datasets
ISCO08_MAJOR_GROUPS = {
    "OC0": "Armed forces occupations",
    "OC1": "Managers",
    "OC2": "Professionals",
    "OC3": "Technicians and associate professionals",
    "OC4": "Clerical support workers",
    "OC5": "Service and sales workers",
    "OC6": "Skilled agricultural, forestry and fishery workers",
    "OC7": "Craft and related trades workers",
    "OC8": "Plant and machine operators and assemblers",
    "OC9": "Elementary occupations",
}

# ISCO-08 2-digit sub-major groups used in LFSA_EGAI2D
ISCO08_2DIGIT = {
    "OC11": "Chief executives, senior officials and legislators",
    "OC12": "Administrative and commercial managers",
    "OC13": "Production and specialised services managers",
    "OC14": "Hospitality, retail and other services managers",
    "OC21": "Science and engineering professionals",
    "OC22": "Health professionals",
    "OC23": "Teaching professionals",
    "OC24": "Business and administration professionals",
    "OC25": "Information and communications technology professionals",
    "OC26": "Legal, social and cultural professionals",
    "OC31": "Science and engineering associate professionals",
    "OC32": "Health associate professionals",
    "OC33": "Business and administration associate professionals",
    "OC34": "Legal, social, cultural and related associate professionals",
    "OC35": "Information and communications technicians",
    "OC41": "General and keyboard clerks",
    "OC42": "Customer services clerks",
    "OC43": "Numerical and material recording clerks",
    "OC44": "Other clerical support workers",
    "OC51": "Personal service workers",
    "OC52": "Sales workers",
    "OC53": "Personal care workers",
    "OC54": "Protective services workers",
    "OC61": "Market-oriented skilled agricultural workers",
    "OC62": "Market-oriented skilled forestry, fishery and hunting workers",
    "OC71": "Building and related trades workers, excluding electricians",
    "OC72": "Metal, machinery and related trades workers",
    "OC73": "Handicraft and printing workers",
    "OC74": "Electrical and electronic trades workers",
    "OC75": "Food processing, wood working, garment and other craft and related trades workers",
    "OC81": "Stationary plant and machine operators",
    "OC82": "Assemblers",
    "OC83": "Drivers and mobile plant operators",
    "OC91": "Cleaners and helpers",
    "OC92": "Agricultural, forestry and fishery labourers",
    "OC93": "Labourers in mining, construction, manufacturing and transport",
    "OC94": "Food preparation assistants",
    "OC95": "Street and related sales and service workers",
    "OC96": "Refuse workers and other elementary workers",
}


def fetch_sdmx_csv(dataset, key="", params=None, client=None, verbose=False):
    """Fetch data from Eurostat SDMX 2.1 API in CSV format.

    Eurostat SDMX 2.1 ignores dimension filters in query parameters.
    Use the ``key`` argument for path-based filtering instead::

        fetch_sdmx_csv("LFSA_EGAI2D", key="A..Y_GE15.T.THS_PER.CY")

    Args:
        dataset: Eurostat dataset code (e.g. 'LFSA_EGAI2D').
        key: SDMX dimension key for path-based filtering (dot-separated).
            Empty positions match all values for that dimension.
        params: Dict of query parameters (only for non-dimension params
            like ``lastNPeriods`` and ``format``).
        client: Optional httpx.Client for connection reuse.
        verbose: Print request URL and response info for debugging.

    Returns:
        List of dicts, one per row in the CSV response.
    """
    url = f"{BASE_URL}/{dataset}/{key}" if key else f"{BASE_URL}/{dataset}"
    query = {"format": "SDMX-CSV"}
    if params:
        query.update(params)

    if client is None:
        with httpx.Client(timeout=60) as c:
            response = c.get(url, params=query)
    else:
        response = client.get(url, params=query)

    if verbose:
        print(f"  [eurostat] GET {response.url}")
        print(f"  [eurostat] Status: {response.status_code}, bytes: {len(response.text)}")

    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))
    return list(reader)


def fetch_json_stat(dataset, params=None, client=None):
    """Fetch data from Eurostat JSON-stat API.

    Args:
        dataset: Eurostat dataset code (e.g. 'LFSA_EGAI2D').
        params: Dict of query parameters to filter the data.
        client: Optional httpx.Client for connection reuse.

    Returns:
        Parsed JSON response as a dict.
    """
    url = f"{JSON_STAT_URL}/{dataset}"
    query = params or {}

    if client is None:
        with httpx.Client(timeout=60) as c:
            response = c.get(url, params=query)
    else:
        response = client.get(url, params=query)

    response.raise_for_status()
    return response.json()


def fetch_employment_by_occupation(geo="CY", sex="T", age="Y_GE15", last_n=1, client=None, verbose=False):
    """Fetch employment counts by ISCO-08 2-digit occupation for a country.

    Uses SDMX path-based key filtering. LFSA_EGAI2D dimensions (in order):
    ``freq.isco08.age.sex.unit.geo``

    Args:
        geo: Country code (default 'CY' for Cyprus).
        sex: Sex filter ('T' total, 'M' male, 'F' female).
        age: Age group filter (default 'Y_GE15' = 15+).
        last_n: Number of most recent periods to fetch.
        client: Optional httpx.Client.
        verbose: Print debug info.

    Returns:
        List of dicts with keys: isco_code, isco_label, employment_thousands, year.
    """
    # LFSA_EGAI2D dimensions: freq.isco08.age.sex.unit.geo
    # Leave isco08 empty to get all occupation codes.
    key = f"A..{age}.{sex}.THS_PER.{geo}"
    params = {"lastNPeriods": str(last_n)}

    rows = fetch_sdmx_csv("LFSA_EGAI2D", key=key, params=params, client=client, verbose=verbose)

    # Safety: verify geo filtering worked
    if rows and "geo" in rows[0]:
        rows = [r for r in rows if r.get("geo") == geo]

    # lastNPeriods may return multiple years; keep only the most recent.
    if rows:
        max_year = max(r.get("TIME_PERIOD", "") for r in rows)
        rows = [r for r in rows if r.get("TIME_PERIOD") == max_year]

    results = []
    for row in rows:
        isco_code = row.get("isco08", "")
        value = row.get("OBS_VALUE", "")
        time_period = row.get("TIME_PERIOD", "")

        if not value or value == ":":
            continue

        label = ISCO08_2DIGIT.get(isco_code, ISCO08_MAJOR_GROUPS.get(isco_code, isco_code))

        results.append(
            {
                "isco_code": isco_code,
                "isco_label": label,
                "employment_thousands": float(value),
                "year": time_period,
            }
        )

    return results


def fetch_earnings_by_occupation(geo="CY", last_n=1, client=None, verbose=False):
    """Fetch mean gross hourly earnings by ISCO-08 1-digit occupation.

    Uses the earn_ses_hourly dataset (Structure of Earnings Survey).
    SES data is only published every 4 years (latest available: 2022).

    earn_ses_hourly dimensions (in order):
    ``freq.nace_r2.isco08.worktime.age.sex.indic_se.geo``

    Args:
        geo: Country code (default 'CY' for Cyprus).
        last_n: Number of most recent periods to fetch.
        client: Optional httpx.Client.
        verbose: Print debug info.

    Returns:
        List of dicts with keys: isco_code, isco_label, hourly_earnings_eur, year.
    """
    # earn_ses_hourly dimensions: freq.nace_r2.isco08.worktime.age.sex.indic_se.geo
    # Use a broad key (leave nace_r2, worktime, age, sex open) to avoid
    # invalid dimension values, then post-filter for the rows we need.
    # OC0 (armed forces) is not available in earn_ses_hourly.
    isco_codes = [k for k in ISCO08_MAJOR_GROUPS if k != "OC0"]
    isco_list = "+".join(isco_codes)
    key = f"A..{isco_list}....MEAN_E_EUR.{geo}"
    params = {"lastNPeriods": str(last_n)}

    try:
        rows = fetch_sdmx_csv("earn_ses_hourly", key=key, params=params, client=client, verbose=verbose)
    except Exception as exc:
        print(f"WARNING: Earnings fetch failed: {exc}")
        rows = []

    # Post-filter: keep only aggregate rows (all sectors, all working times,
    # all ages, both sexes).  Prefer the most-aggregate nace_r2 value available.
    valid_isco = set(isco_codes)
    filtered: dict[str, dict] = {}  # isco_code -> best row
    # Preference order for nace_r2 (most aggregate first)
    nace_rank = {"B-S": 0, "B-N": 1, "TOTAL": 2}
    for r in rows:
        if r.get("geo") != geo or r.get("isco08") not in valid_isco:
            continue
        # Skip non-aggregate breakdowns
        if r.get("sex", "T") not in ("T", "TOTAL", ""):
            continue
        if r.get("worktime", "TOTAL") not in ("TOTAL", ""):
            continue
        if r.get("age", "TOTAL") not in ("TOTAL", ""):
            continue
        code = r["isco08"]
        rank = nace_rank.get(r.get("nace_r2", ""), 99)
        prev = filtered.get(code)
        if prev is None or rank < nace_rank.get(prev.get("nace_r2", ""), 99):
            filtered[code] = r
    rows = list(filtered.values())

    if not rows:
        print(f"WARNING: No earnings data returned for {geo}.")
        print("  Run 'uv run python diagnose_eurostat.py' for details.")

    results = []
    for row in rows:
        isco_code = row.get("isco08", "")
        value = row.get("OBS_VALUE", "")
        time_period = row.get("TIME_PERIOD", "")

        if not value or value == ":":
            continue

        label = ISCO08_MAJOR_GROUPS.get(isco_code, isco_code)

        results.append(
            {
                "isco_code": isco_code,
                "isco_label": label,
                "hourly_earnings_eur": float(value),
                "year": time_period,
            }
        )

    return results


def build_occupation_summary(employment_data, earnings_data):
    """Merge employment and earnings data into a unified summary.

    Args:
        employment_data: Output of fetch_employment_by_occupation().
        earnings_data: Output of fetch_earnings_by_occupation().

    Returns:
        List of dicts with merged employment + earnings per ISCO major group.
    """
    # Index earnings by ISCO 1-digit code
    earnings_by_code = {}
    for row in earnings_data:
        earnings_by_code[row["isco_code"]] = row

    # Aggregate 2-digit employment into 1-digit groups
    employment_by_major = {}
    detail_by_major = {}

    for row in employment_data:
        code = row["isco_code"]
        # Determine 1-digit parent (OC25 -> OC2)
        if len(code) == 4:  # 2-digit like OC25
            major = code[:3]
        elif len(code) == 3:  # 1-digit like OC2
            major = code
        else:
            continue

        if major not in employment_by_major:
            employment_by_major[major] = 0.0
            detail_by_major[major] = []

        # Only count 2-digit entries to avoid double-counting with 1-digit totals
        if len(code) == 4:
            employment_by_major[major] += row["employment_thousands"]
            detail_by_major[major].append(row)

    summary = []
    for code in sorted(ISCO08_MAJOR_GROUPS.keys()):
        earnings = earnings_by_code.get(code, {})

        # Prefer 1-digit total from source data if available
        one_digit_rows = [r for r in employment_data if r["isco_code"] == code]
        if one_digit_rows:
            emp = one_digit_rows[0]["employment_thousands"]
            year = one_digit_rows[0]["year"]
        else:
            emp = employment_by_major.get(code, 0.0)
            year = detail_by_major.get(code, [{}])[0].get("year", "")

        summary.append(
            {
                "isco_code": code,
                "isco_label": ISCO08_MAJOR_GROUPS[code],
                "employment_thousands": round(emp, 1),
                "hourly_earnings_eur": earnings.get("hourly_earnings_eur"),
                "annual_earnings_eur": round(earnings["hourly_earnings_eur"] * 2080)
                if earnings.get("hourly_earnings_eur")
                else None,
                "year_employment": year,
                "year_earnings": earnings.get("year", ""),
                "sub_occupations": detail_by_major.get(code, []),
            }
        )

    return summary


def main():
    parser = argparse.ArgumentParser(description="Fetch Cyprus labour market data from Eurostat")
    parser.add_argument("--dataset", default="LFSA_EGAI2D", help="Eurostat dataset code")
    parser.add_argument("--geo", default="CY", help="Country code (default: CY)")
    parser.add_argument("--output", help="Output CSV file path")
    parser.add_argument("--json", action="store_true", help="Output as JSON instead of CSV")
    args = parser.parse_args()

    print(f"Fetching data from Eurostat: {args.dataset} for {args.geo}...")

    with httpx.Client(timeout=60) as client:
        employment = fetch_employment_by_occupation(geo=args.geo, client=client)
        earnings = fetch_earnings_by_occupation(geo=args.geo, client=client)

    summary = build_occupation_summary(employment, earnings)

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    if args.output:
        fieldnames = [
            "isco_code",
            "isco_label",
            "employment_thousands",
            "hourly_earnings_eur",
            "annual_earnings_eur",
            "year_employment",
            "year_earnings",
        ]
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(summary)
        print(f"Wrote {len(summary)} rows to {args.output}")
    else:
        print(f"\n{'ISCO':<6} {'Occupation':<50} {'Emp (K)':<10} {'€/hr':<8} {'€/yr':<10}")
        print("-" * 90)
        for row in summary:
            emp = f"{row['employment_thousands']:.1f}" if row["employment_thousands"] else "—"
            hourly = f"{row['hourly_earnings_eur']:.2f}" if row["hourly_earnings_eur"] else "—"
            annual = f"{row['annual_earnings_eur']:,}" if row["annual_earnings_eur"] else "—"
            print(f"{row['isco_code']:<6} {row['isco_label']:<50} {emp:<10} {hourly:<8} {annual:<10}")


if __name__ == "__main__":
    main()
