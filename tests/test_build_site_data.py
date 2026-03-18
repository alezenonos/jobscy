"""Tests for build_site_data.py — site data merging logic."""

from build_site_data import detect_format, merge_bls, merge_cyprus


class TestDetectFormat:
    def test_cyprus_format(self):
        assert detect_format(["title", "isco_code", "slug"]) == "cyprus"

    def test_bls_format(self):
        assert detect_format(["title", "soc_code", "slug"]) == "bls"

    def test_unknown_format(self):
        assert detect_format(["title", "slug"]) == "unknown"


class TestMergeBls:
    def test_merge_logic(self):
        rows = [
            {
                "title": "Software Developer",
                "slug": "software-developers",
                "category": "Computer and Information Technology",
                "median_pay_annual": "130000",
                "num_jobs_2024": "1800000",
                "outlook_pct": "17",
                "outlook_desc": "Much faster than average",
                "entry_education": "Bachelor's degree",
                "url": "https://example.com/software-developers",
            }
        ]
        scores = {
            "software-developers": {
                "slug": "software-developers",
                "exposure": 9,
                "rationale": "Highly digital work.",
            }
        }

        data = merge_bls(rows, scores)
        assert len(data) == 1
        assert data[0]["title"] == "Software Developer"
        assert data[0]["pay"] == 130000
        assert data[0]["jobs"] == 1800000
        assert data[0]["exposure"] == 9
        assert data[0]["outlook"] == 17

    def test_missing_score(self):
        rows = [
            {
                "title": "Test",
                "slug": "test",
                "category": "other",
                "median_pay_annual": "",
                "num_jobs_2024": "",
                "outlook_pct": "",
                "outlook_desc": "",
                "entry_education": "",
                "url": "",
            }
        ]
        data = merge_bls(rows, {})
        assert data[0]["exposure"] is None
        assert data[0]["pay"] is None
        assert data[0]["jobs"] is None


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
