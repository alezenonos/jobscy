"""
Load the official forecasts and pay extras that enrich site/data.json.

All inputs are small cached files under data/cache/, refreshed by hand
(see HANDOVER.md for where each one comes from):

- wage_index.json        Eurostat lc_lci_r2_a (Cyprus labour cost index, wages
                         and salaries, business economy B-S, 2020=100). Used to
                         carry SES 2022 pay forward to the latest year as an
                         estimate.
- earnings_by_sector.json Eurostat earn_ses22_49 / earn_ses22_54: mean annual
                         earnings and employee counts by ISCO major group and
                         NACE section (SES 2022).
- hrda_2022_2032.csv     HRDA "Forecasts of Employment Needs in Cyprus
                         2022-2032", chapter 6 (one row per ISCO 2-digit group).
- cedefop_2035.json      Cedefop Skills Forecast, Cyprus, 2022-2035.
- eu_compare.json        Eurostat lfsa_egai2d for EU27 (jobs by 2-digit group)
                         and earn_ses22_28 for CY, EU27 and Greece (mean annual
                         pay by major group, in EUR and PPS). Refreshed by
                         `refresh_data.py eu-compare`.
"""

import csv
import json
import os

CACHE_DIR = os.path.join("data", "cache")

# NACE Rev. 2 section names, short enough for a tooltip.
NACE_NAMES = {
    "B": "Mining",
    "C": "Manufacturing",
    "D": "Energy",
    "E": "Water & waste",
    "F": "Construction",
    "G": "Retail & wholesale",
    "H": "Transport & shipping",
    "I": "Hotels & restaurants",
    "J": "ICT & media",
    "K": "Finance & insurance",
    "L": "Real estate",
    "M": "Professional services",
    "N": "Admin & support",
    "O": "Public administration",
    "P": "Education",
    "Q": "Health & social care",
    "R": "Arts & recreation",
    "S": "Other services",
}

# Sector cells with fewer employees than this are too noisy to show (SES is a
# sample survey; e.g. technicians in real estate, n=427, average €135K).
MIN_SECTOR_EMPLOYEES = 500


def _path(name, cache_dir=None):
    return os.path.join(cache_dir or CACHE_DIR, name)


def load_wage_uplift(base_year, cache_dir=None):
    """Return (factor, target_year) to carry pay from base_year to the latest index year.

    Returns (1.0, base_year) when the index file or the base year is missing.
    """
    path = _path("wage_index.json", cache_dir)
    if not os.path.exists(path):
        return 1.0, str(base_year)
    with open(path) as f:
        index = json.load(f).get("index", {})
    base = index.get(str(base_year))
    if not base or not index:
        return 1.0, str(base_year)
    target_year = max(index)
    return index[target_year] / base, target_year


def load_sector_pay(cache_dir=None, min_employees=MIN_SECTOR_EMPLOYEES):
    """Return {major group code (e.g. "OC2"): [ {sector, name, pay, employees}, ... ]}.

    Each list is sorted from highest to lowest pay and drops small cells.
    """
    path = _path("earnings_by_sector.json", cache_dir)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        rows = json.load(f)
    out = {}
    for r in rows:
        n = r.get("employees") or 0
        pay = r.get("annual_earnings_eur")
        if n < min_employees or pay is None:
            continue
        out.setdefault(r["isco_code"], []).append(
            {
                "sector": r["nace_r2"],
                "name": NACE_NAMES.get(r["nace_r2"], r["nace_r2"]),
                "pay": round(pay),
                "employees": n,
            }
        )
    for v in out.values():
        v.sort(key=lambda s: -s["pay"])
    return out


def load_hrda(cache_dir=None):
    """Return {isco_code: {emp_2022, emp_2032, expansion, replacement, total}} (per-year averages)."""
    path = _path("hrda_2022_2032.csv", cache_dir)
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            out[r["isco_code"]] = {
                "emp_2022": int(r["emp_2022"]),
                "emp_2032": int(r["emp_2032"]),
                "expansion": int(r["expansion_per_year"]),
                "replacement": int(r["replacement_per_year"]),
                "total": int(r["total_per_year"]),
            }
    return out


def load_cedefop(cache_dir=None):
    """Return {isco_code: {job_openings, growth_pct, growth, replacement}} for 2022-2035."""
    path = _path("cedefop_2035.json", cache_dir)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f).get("occupations", {})


def _scale(value, factor):
    return round(value * factor) if value is not None else None


def enrich(records, cache_dir=None):
    """Add 2025 pay estimates, sector pay and official forecasts to site records in place."""
    sector_pay = load_sector_pay(cache_dir)
    hrda = load_hrda(cache_dir)
    cedefop = load_cedefop(cache_dir)
    uplift_cache = {}

    for d in records:
        code = d.get("isco_code", "")
        major = code[:3]

        base_year = d.get("year_earnings") or ""
        if base_year not in uplift_cache:
            uplift_cache[base_year] = load_wage_uplift(base_year, cache_dir)
        factor, target_year = uplift_cache[base_year]

        d["pay_survey"] = d.get("pay")
        d["pay_survey_year"] = base_year
        if factor != 1.0:
            d["pay"] = _scale(d.get("pay"), factor)
            d["pay_median"] = _scale(d.get("pay_median"), factor)
            d["pay_p10"] = _scale(d.get("pay_p10"), factor)
            d["pay_p90"] = _scale(d.get("pay_p90"), factor)
            if d.get("pay_hourly") is not None:
                d["pay_hourly"] = round(d["pay_hourly"] * factor, 2)
            d["pay_year"] = target_year
            d["pay_estimated"] = True
            d["pay_uplift_pct"] = round((factor - 1) * 100, 1)
        else:
            d["pay_year"] = base_year
            d["pay_estimated"] = False

        sectors = sector_pay.get(major, [])
        d["pay_by_sector"] = [{**s, "pay": _scale(s["pay"], factor)} for s in sectors]

        h = hrda.get(code)
        if h:
            d["hrda_emp_2022"] = h["emp_2022"]
            d["hrda_emp_2032"] = h["emp_2032"]
            d["hrda_change_pct"] = round((h["emp_2032"] / h["emp_2022"] - 1) * 100, 1) if h["emp_2022"] else None
            d["hrda_openings_per_year"] = h["total"]
            d["hrda_expansion_per_year"] = h["expansion"]
            d["hrda_replacement_per_year"] = h["replacement"]
            d["hrda_openings_rate"] = round(h["total"] / h["emp_2022"] * 100, 2) if h["emp_2022"] else None

        c = cedefop.get(code)
        if c:
            d["cedefop_openings_2035"] = c["job_openings"]
            d["cedefop_growth_pct"] = c["growth_pct"]
            d["cedefop_replacement_2035"] = c["replacement"]
    add_eu_compare(records, cache_dir)
    return records


def load_eu_compare(cache_dir=None):
    """Return the cached EU comparison data (eu_compare.json), or {} when missing.

    Layout: {"employment": {"year", "thousands": {isco: EU27 jobs in thousands}},
             "earnings": {"year", "EUR": {geo: {isco: pay}}, "PPS": {geo: {isco: pay}}}}
    """
    path = _path("eu_compare.json", cache_dir)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _ratio_pct(a, b):
    return round(a / b * 100) if a and b else None


def add_eu_compare(records, cache_dir=None):
    """Add the "Distinctly Cypriot" location quotient and Cyprus pay vs EU and Greece, in place.

    - jobs_lq: the group's share of Cyprus jobs divided by its share of EU27 jobs
      (1 = same as the EU, 2 = twice as common in Cyprus). Both shares are taken
      over the 2-digit groups in records, so suppressed or residual groups don't
      skew the totals.
    - pay_vs_eu_pct / pay_vs_eu_pps_pct / pay_vs_el_pct: Cyprus mean annual pay
      for the major group as a % of the EU27 (in euros and in purchasing power
      standards) and of Greece, all from the same SES 2022 table.
    """
    eu = load_eu_compare(cache_dir)
    if not eu:
        return records

    emp = eu.get("employment", {})
    eu_jobs = emp.get("thousands", {})
    cy_total = sum(d.get("jobs") or 0 for d in records if eu_jobs.get(d.get("isco_code")))
    eu_total = sum(eu_jobs[d["isco_code"]] for d in records if d.get("jobs") and eu_jobs.get(d.get("isco_code")))

    earn = eu.get("earnings", {})
    eur, pps = earn.get("EUR", {}), earn.get("PPS", {})

    for d in records:
        code = d.get("isco_code", "")
        e = eu_jobs.get(code)
        if e and d.get("jobs") and cy_total and eu_total:
            cy_share = d["jobs"] / cy_total
            eu_share = e / eu_total
            d["jobs_cy_share_pct"] = round(cy_share * 100, 2)
            d["jobs_eu_share_pct"] = round(eu_share * 100, 2)
            d["jobs_lq"] = round(cy_share / eu_share, 2)
            d["jobs_eu_year"] = emp.get("year")

        major = code[:3]
        cy_pay = eur.get("CY", {}).get(major)
        eu_pay = eur.get("EU27_2020", {}).get(major)
        el_pay = eur.get("EL", {}).get(major)
        if cy_pay and eu_pay:
            d["pay_eu"] = round(eu_pay)
            d["pay_el"] = round(el_pay) if el_pay else None
            d["pay_vs_eu_pct"] = _ratio_pct(cy_pay, eu_pay)
            d["pay_vs_el_pct"] = _ratio_pct(cy_pay, el_pay)
            d["pay_vs_eu_pps_pct"] = _ratio_pct(pps.get("CY", {}).get(major), pps.get("EU27_2020", {}).get(major))
            d["pay_compare_year"] = earn.get("year")
    return records
