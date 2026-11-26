"""Integrity checks on the committed data that the site publishes.

These run against the real files in the repository (no mocks), so a broken
pipeline run or a hand edit is caught before it is deployed:

- occupations_cy.csv and site/data.json can be rebuilt from the cached inputs
  and match what is committed
- employment adds up: the 2-digit groups sum to their 1-digit totals and no
  group is given its whole parent's total
- every occupation has the values the site shows, in a sensible range
- the score files cover exactly the published occupations
- the data is not out of date
"""

import csv
import datetime
import json
import os
from collections import defaultdict

import pytest

from build_site_data import merge_cyprus
from forecasts import enrich
from make_cy_csv import FIELDNAMES, build_csv_rows, load_cached_data, load_occupations

ROOT = os.path.join(os.path.dirname(__file__), "..")


def _path(*parts):
    return os.path.join(ROOT, *parts)


def _json(*parts):
    with open(_path(*parts)) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def site_data():
    return _json("site", "data.json")


@pytest.fixture(scope="module")
def csv_rows():
    with open(_path("occupations_cy.csv"), newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def employment():
    return _json("data", "cache", "employment.json")


# ── Reproducibility ─────────────────────────────────────────────────────


def test_csv_matches_rebuild_from_cache(csv_rows, monkeypatch):
    monkeypatch.chdir(ROOT)
    occupations = load_occupations(_path("occupations_cy.json"))
    emp, earn = load_cached_data(_path("data", "cache"))
    rebuilt = build_csv_rows(occupations, emp, earn)
    as_text = [{k: "" if r.get(k) is None else str(r.get(k)) for k in FIELDNAMES} for r in rebuilt]
    assert as_text == csv_rows, (
        "occupations_cy.csv is out of date: run `uv run python make_cy_csv.py --cached data/cache`"
    )


def test_site_data_matches_rebuild(site_data, csv_rows, monkeypatch):
    monkeypatch.chdir(ROOT)
    scores = {s["slug"]: s for s in _json("scores.json")}
    outlook = {s["slug"]: s for s in _json("outlook_scores.json")}
    rebuilt = merge_cyprus([dict(r) for r in csv_rows], scores, outlook)
    enrich(rebuilt)
    # Round-trip through JSON so tuples/floats compare the way they are stored
    rebuilt = json.loads(json.dumps(rebuilt))
    assert rebuilt == site_data, "site/data.json is out of date: run `uv run python build_site_data.py`"


# ── Employment adds up ──────────────────────────────────────────────────


def test_two_digit_groups_sum_to_major_group_totals(site_data, employment):
    major = {r["isco_code"]: r["employment_thousands"] for r in employment if len(r["isco_code"]) == 3}
    by_major = defaultdict(float)
    for d in site_data:
        if d["jobs"]:
            by_major[d["isco_code"][:3]] += d["jobs"] / 1000
    for code, total in by_major.items():
        expected = major.get(code)
        if expected is None:
            continue
        assert abs(total - expected) <= max(0.2, expected * 0.01), (
            f"{code}: 2-digit groups add up to {total:.1f}k, Eurostat total is {expected:.1f}k"
        )


def test_no_group_is_given_its_parents_total(site_data, employment):
    major = {r["isco_code"]: r["employment_thousands"] for r in employment if len(r["isco_code"]) == 3}
    children = defaultdict(int)
    for d in site_data:
        children[d["isco_code"][:3]] += 1
    for d in site_data:
        parent = d["isco_code"][:3]
        if children[parent] > 1 and d["jobs"] and parent in major:
            assert abs(d["jobs"] / 1000 - major[parent]) > 0.05, (
                f"{d['isco_code']} {d['title']} has its whole major group's employment ({major[parent]}k)"
            )


def test_total_jobs_is_plausible(site_data):
    total = sum(d["jobs"] or 0 for d in site_data)
    # Cyprus has roughly 450-550k people in work
    assert 400_000 <= total <= 600_000, f"Total jobs {total:,} looks wrong"


# ── Every occupation has sensible values ────────────────────────────────


def test_every_occupation_has_the_values_the_site_shows(site_data):
    for d in site_data:
        for field in ("jobs", "pay", "education", "exposure", "outlook"):
            assert d.get(field) not in (None, ""), f"{d['title']}: missing {field}"


def test_values_in_range(site_data):
    for d in site_data:
        t = d["title"]
        assert 0 <= d["exposure"] <= 10 and isinstance(d["exposure"], int), f"{t}: exposure {d['exposure']}"
        assert -60 <= d["outlook"] <= 100, f"{t}: outlook {d['outlook']}"
        assert 8_000 <= d["pay"] <= 200_000, f"{t}: pay {d['pay']}"
        assert d["jobs"] > 0, f"{t}: jobs {d['jobs']}"
        if d.get("pay_p10") and d.get("pay_p90"):
            assert d["pay_p10"] <= (d.get("pay_median") or d["pay_p10"]) <= d["pay_p90"], f"{t}: P10/median/P90"


def test_hrda_openings_add_up(site_data):
    for d in site_data:
        if d.get("hrda_openings_per_year") is None:
            continue
        parts = d["hrda_expansion_per_year"] + d["hrda_replacement_per_year"]
        assert abs(parts - d["hrda_openings_per_year"]) <= 1, (
            f"{d['title']}: {d['hrda_expansion_per_year']} new + {d['hrda_replacement_per_year']} "
            f"replacement != {d['hrda_openings_per_year']} openings"
        )


def test_education_levels_are_known(site_data):
    known = {
        "Lower secondary or below",
        "Upper secondary / Vocational",
        "Short-cycle tertiary / Associate",
        "Bachelor's degree or higher",
        "Varies (military)",
    }
    for d in site_data:
        assert d["education"] in known, f"{d['title']}: unknown education level {d['education']!r}"


# ── Score files match the published occupations ─────────────────────────


@pytest.mark.parametrize("filename", ["scores.json", "outlook_scores.json"])
def test_score_files_cover_exactly_the_occupations(site_data, filename):
    slugs = {d["slug"] for d in site_data}
    scored = [s["slug"] for s in _json(filename)]
    assert len(scored) == len(set(scored)), f"{filename} has duplicate slugs"
    assert set(scored) == slugs, (
        f"{filename}: missing {sorted(slugs - set(scored))}, extra {sorted(set(scored) - slugs)}"
    )


# ── Freshness ───────────────────────────────────────────────────────────


def test_employment_data_is_recent(site_data):
    years = {int(d["year_employment"]) for d in site_data if d.get("year_employment")}
    assert len(years) == 1, f"Mixed employment years: {sorted(years)}"
    year = years.pop()
    # LFS for year Y is published in spring of Y+1; allow one more year of slack
    assert datetime.date.today().year - year <= 2, f"Employment data is from {year}: refresh it from Eurostat"
