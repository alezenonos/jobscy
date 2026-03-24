"""Diagnostic script for Eurostat API issues.

Run from a machine with internet access (e.g. GitHub Codespace):
    uv run python diagnose_eurostat.py

Tests path-based SDMX key filtering (the correct approach) and validates
that employment and earnings data for Cyprus are sensible.
"""

import csv
import io
import sys

import httpx

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data"


def fetch_csv(dataset, key="", params=None, client=None):
    """Fetch SDMX-CSV from Eurostat using path-based key, return (rows, url)."""
    url = f"{BASE_URL}/{dataset}/{key}" if key else f"{BASE_URL}/{dataset}"
    query = {"format": "SDMX-CSV"}
    if params:
        query.update(params)
    try:
        resp = client.get(url, params=query)
        print(f"  URL: {resp.url}")
        print(f"  Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"  Body: {resp.text[:300]}")
            return [], str(resp.url)
        rows = list(csv.DictReader(io.StringIO(resp.text)))
        return rows, str(resp.url)
    except Exception as e:
        print(f"  ERROR: {e}")
        return [], ""


def diagnose_employment(client):
    """Check employment data for CY using path-based key."""
    print("\n" + "=" * 70)
    print("EMPLOYMENT DIAGNOSTICS (LFSA_EGAI2D)")
    print("=" * 70)

    # LFSA_EGAI2D dimensions: freq.isco08.age.sex.unit.geo
    print("\n--- Test 1: Path-based key (FIXED approach) ---")
    key = "A..Y_GE15.T.THS_PER.CY"
    rows, _ = fetch_csv("LFSA_EGAI2D", key=key, params={"lastNPeriods": "1"}, client=client)
    print(f"  Rows returned: {len(rows)}")

    if not rows:
        print("  No data returned!")
        # Fallback: try without key to compare
        print("\n--- Fallback: query params only (OLD broken approach) ---")
        rows, _ = fetch_csv(
            "LFSA_EGAI2D",
            params={"geo": "CY", "sex": "T", "age": "Y_GE15", "unit": "THS_PER", "lastNPeriods": "1"},
            client=client,
        )
        print(f"  Rows returned: {len(rows)}")
        if rows:
            geos = {row.get("geo", "?") for row in rows}
            print(f"  Unique geos (expected only CY): {geos}")
        return

    # Show first 3 raw rows
    print("\n  Sample raw rows:")
    for i, row in enumerate(rows[:3]):
        print(f"    Row {i}: {dict(row)}")

    # Check geo
    geos = {row.get("geo", "?") for row in rows}
    print(f"\n  Unique geo values: {geos}")
    if geos == {"CY"}:
        print("  OK: Only CY data returned.")
    else:
        print("  WARNING: Non-CY data present!")

    # Sum 2-digit employment for CY
    cy_rows = [r for r in rows if r.get("geo") == "CY"]
    total = 0.0
    two_digit = []
    for row in cy_rows:
        code = row.get("isco08", "")
        val = row.get("OBS_VALUE", "")
        if len(code) == 4 and val and val != ":":
            total += float(val)
            two_digit.append((code, float(val), row.get("TIME_PERIOD", "")))

    print(f"\n  CY 2-digit employment total: {total:.1f} thousand ({total * 1000:.0f} people)")
    if 100 < total < 600:
        print("  OK: Plausible for Cyprus workforce.")
    elif total > 600:
        print("  WARNING: Too high — geo filter may not be working.")
    else:
        print("  WARNING: Too low — check data availability.")

    print("\n  2-digit values (first 10):")
    for code, val, year in sorted(two_digit)[:10]:
        print(f"    {code}: {val:.1f}K ({year})")


def diagnose_earnings(client):
    """Check earnings data for CY using path-based key and earn_ses_hourly."""
    print("\n" + "=" * 70)
    print("EARNINGS DIAGNOSTICS (earn_ses_hourly)")
    print("=" * 70)

    # earn_ses_hourly dimensions: freq.nace_r2.isco08.worktime.age.sex.indic_se.geo
    # OC0 not available in earn_ses_hourly; valid indicator is MEAN_E_EUR
    isco_list = "+".join([f"OC{i}" for i in range(1, 10)])

    print("\n--- Test 1: earn_ses_hourly with path key (FIXED approach) ---")
    key = f"A.B-S.{isco_list}.TOTAL...MEAN_E_EUR.CY"
    rows, _ = fetch_csv("earn_ses_hourly", key=key, params={"lastNPeriods": "1"}, client=client)
    print(f"  Rows: {len(rows)}")

    if rows:
        geos = {row.get("geo", "?") for row in rows}
        print(f"  Unique geos: {geos}")
        print("\n  Earnings data:")
        for row in rows:
            code = row.get("isco08", "?")
            val = row.get("OBS_VALUE", "?")
            year = row.get("TIME_PERIOD", "?")
            print(f"    {code}: €{val}/hr ({year})")
    else:
        print("  No data returned with full key. Trying broader queries...")

    # Test 2: earn_ses_hourly with just geo in key, minimal filters
    print("\n--- Test 2: earn_ses_hourly — broader key (just geo) ---")
    key2 = f"A..{isco_list}......CY"
    rows, _ = fetch_csv("earn_ses_hourly", key=key2, params={"lastNPeriods": "1"}, client=client)
    print(f"  Rows: {len(rows)}")
    if rows:
        print("  Sample columns:", list(rows[0].keys()))
        for row in rows[:5]:
            print(
                f"    isco08={row.get('isco08', '?')} indic_se={row.get('indic_se', '?')} "
                f"val={row.get('OBS_VALUE', '?')} year={row.get('TIME_PERIOD', '?')}"
            )

    # Test 3: earn_ses_hourly — just CY, no ISCO filter
    print("\n--- Test 3: earn_ses_hourly — just geo=CY, all dimensions open ---")
    key3 = "A.......CY"
    rows, _ = fetch_csv("earn_ses_hourly", key=key3, params={"lastNPeriods": "1"}, client=client)
    print(f"  Rows: {len(rows)}")
    if rows:
        isco_vals = {row.get("isco08", "?") for row in rows}
        indic_vals = {row.get("indic_se", "?") for row in rows}
        print(f"  Available isco08 values: {sorted(isco_vals)}")
        print(f"  Available indic_se values: {sorted(indic_vals)}")

    # Test 4: compare with old broken approach
    print("\n--- Test 4: earn_ses_pub1s (OLD dataset — no ISCO dimension) ---")
    rows, _ = fetch_csv("earn_ses_pub1s", params={"geo": "CY", "lastNPeriods": "1"}, client=client)
    print(f"  Rows: {len(rows)}")
    if rows:
        print("  Columns:", list(rows[0].keys()))
        print("  NOTE: No isco08 column = wrong dataset")


def main():
    print("Eurostat API Diagnostics (path-based key approach)")
    print(f"Python: {sys.version}")

    with httpx.Client(timeout=60) as client:
        diagnose_employment(client)
        diagnose_earnings(client)

    print("\n" + "=" * 70)
    print("DONE — paste this output back to Claude for analysis")
    print("=" * 70)


if __name__ == "__main__":
    main()
