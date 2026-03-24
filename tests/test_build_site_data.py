"""Tests for build_site_data.py — site data merging logic."""

from build_site_data import merge_cyprus


class TestMergeCyprus:
    def test_merge_logic(self):
        rows = [
            {
                "title": "ICT Professionals",
                "slug": "ict-professionals",
                "category": "professionals",
                "isco_code": "OC25",
                "median_pay_annual_eur": "38064",
                "median_pay_hourly_eur": "18.30",
                "entry_education": "Bachelor's degree or higher",
                "employment_thousands": "12.5",
                "year_employment": "2023",
                "year_earnings": "2022",
            }
        ]
        scores = {
            "ict-professionals": {
                "slug": "ict-professionals",
                "exposure": 8,
                "rationale": "Digital work.",
            }
        }

        data = merge_cyprus(rows, scores)
        assert len(data) == 1
        assert data[0]["title"] == "ICT Professionals"
        assert data[0]["pay"] == 38064
        assert data[0]["pay_hourly"] == 18.30
        assert data[0]["jobs"] == 12500  # 12.5K * 1000
        assert data[0]["isco_code"] == "OC25"
        assert data[0]["exposure"] == 8

    def test_empty_employment(self):
        rows = [
            {
                "title": "Test",
                "slug": "test",
                "category": "other",
                "isco_code": "OC99",
                "median_pay_annual_eur": "",
                "median_pay_hourly_eur": "",
                "entry_education": "",
                "employment_thousands": "",
                "year_employment": "",
                "year_earnings": "",
            }
        ]
        data = merge_cyprus(rows, {})
        assert data[0]["pay"] is None
        assert data[0]["jobs"] is None
        assert data[0]["exposure"] is None
