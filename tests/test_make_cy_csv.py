"""Tests for make_cy_csv.py — Cyprus CSV builder from Eurostat data."""

import os
import tempfile

from make_cy_csv import FIELDNAMES, build_csv_rows, load_cached_data, save_cached_data


def _sample_occupations():
    return [
        {
            "title": "Chief executives, senior officials and legislators",
            "isco_code": "OC11",
            "isco_parent": "OC1",
            "category": "managers",
            "slug": "chief-executives-senior-officials-and-legislators",
        },
        {
            "title": "Information and communications technology professionals",
            "isco_code": "OC25",
            "isco_parent": "OC2",
            "category": "professionals",
            "slug": "information-and-communications-technology-professionals",
        },
        {
            "title": "Cleaners and helpers",
            "isco_code": "OC91",
            "isco_parent": "OC9",
            "category": "elementary-occupations",
            "slug": "cleaners-and-helpers",
        },
    ]


def _sample_employment():
    return [
        {"isco_code": "OC11", "isco_label": "Chief executives", "employment_thousands": 5.2, "year": "2023"},
        {"isco_code": "OC25", "isco_label": "ICT professionals", "employment_thousands": 12.5, "year": "2023"},
        {"isco_code": "OC91", "isco_label": "Cleaners and helpers", "employment_thousands": 18.0, "year": "2023"},
    ]


def _sample_earnings():
    return [
        {"isco_code": "OC1", "isco_label": "Managers", "hourly_earnings_eur": 22.50, "year": "2022"},
        {"isco_code": "OC2", "isco_label": "Professionals", "hourly_earnings_eur": 18.30, "year": "2022"},
        {"isco_code": "OC9", "isco_label": "Elementary occupations", "hourly_earnings_eur": 7.20, "year": "2022"},
    ]


class TestBuildCsvRows:
    def test_returns_correct_count(self):
        rows = build_csv_rows(_sample_occupations(), _sample_employment(), _sample_earnings())
        assert len(rows) == 3

    def test_all_fieldnames_present(self):
        rows = build_csv_rows(_sample_occupations(), _sample_employment(), _sample_earnings())
        for row in rows:
            for field in FIELDNAMES:
                assert field in row, f"Missing field: {field}"

    def test_annual_pay_calculated(self):
        rows = build_csv_rows(_sample_occupations(), _sample_employment(), _sample_earnings())
        # OC11 parent is OC1 → 22.50 * 2080 = 46800
        oc11 = next(r for r in rows if r["isco_code"] == "OC11")
        assert oc11["median_pay_annual_eur"] == round(22.50 * 2080)

    def test_hourly_pay_preserved(self):
        rows = build_csv_rows(_sample_occupations(), _sample_employment(), _sample_earnings())
        oc25 = next(r for r in rows if r["isco_code"] == "OC25")
        assert oc25["median_pay_hourly_eur"] == "18.30"

    def test_employment_data_mapped(self):
        rows = build_csv_rows(_sample_occupations(), _sample_employment(), _sample_earnings())
        oc25 = next(r for r in rows if r["isco_code"] == "OC25")
        assert oc25["employment_thousands"] == 12.5

    def test_education_from_isco_group(self):
        rows = build_csv_rows(_sample_occupations(), _sample_employment(), _sample_earnings())
        # Managers → Bachelor's degree or higher
        oc11 = next(r for r in rows if r["isco_code"] == "OC11")
        assert "Bachelor" in oc11["entry_education"]
        # Elementary → Lower secondary or below
        oc91 = next(r for r in rows if r["isco_code"] == "OC91")
        assert "Lower secondary" in oc91["entry_education"]

    def test_missing_employment_returns_empty(self):
        occs = [
            {
                "title": "Test occupation",
                "isco_code": "OC35",
                "isco_parent": "OC3",
                "category": "technicians",
                "slug": "test-occupation",
            }
        ]
        rows = build_csv_rows(occs, [], _sample_earnings())
        assert rows[0]["employment_thousands"] == ""

    def test_missing_earnings_returns_empty(self):
        occs = [
            {
                "title": "Test occupation",
                "isco_code": "OC35",
                "isco_parent": "OC3",
                "category": "technicians",
                "slug": "test-occupation",
            }
        ]
        rows = build_csv_rows(occs, _sample_employment(), [])
        assert rows[0]["median_pay_annual_eur"] == ""
        assert rows[0]["median_pay_hourly_eur"] == ""


class TestCacheRoundtrip:
    def test_save_and_load(self):
        emp = _sample_employment()
        earn = _sample_earnings()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_cached_data(emp, earn, tmpdir)

            assert os.path.exists(os.path.join(tmpdir, "employment.json"))
            assert os.path.exists(os.path.join(tmpdir, "earnings.json"))

            loaded_emp, loaded_earn = load_cached_data(tmpdir)

        assert len(loaded_emp) == len(emp)
        assert len(loaded_earn) == len(earn)
        assert loaded_emp[0]["isco_code"] == emp[0]["isco_code"]
        assert loaded_earn[0]["hourly_earnings_eur"] == earn[0]["hourly_earnings_eur"]
