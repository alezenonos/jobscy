"""Tests for eurostat.py — Eurostat API client for Cyprus labour market data."""

import json
from unittest.mock import MagicMock

from eurostat import (
    ISCO08_2DIGIT,
    ISCO08_MAJOR_GROUPS,
    build_occupation_summary,
    fetch_earnings_by_occupation,
    fetch_employment_by_occupation,
    fetch_json_stat,
    fetch_sdmx_csv,
)

# --- Sample CSV responses mimicking Eurostat SDMX-CSV format ---

SAMPLE_EMPLOYMENT_CSV = """\
DATAFLOW,LAST UPDATE,freq,age,isco08,sex,unit,geo,TIME_PERIOD,OBS_VALUE,OBS_FLAG
ESTAT:LFSA_EGAI2D(1.0),2024-06-01,A,Y_GE15,OC1,T,THS_PER,CY,2023,25.3,
ESTAT:LFSA_EGAI2D(1.0),2024-06-01,A,Y_GE15,OC2,T,THS_PER,CY,2023,82.1,
ESTAT:LFSA_EGAI2D(1.0),2024-06-01,A,Y_GE15,OC25,T,THS_PER,CY,2023,12.5,
ESTAT:LFSA_EGAI2D(1.0),2024-06-01,A,Y_GE15,OC22,T,THS_PER,CY,2023,8.3,
ESTAT:LFSA_EGAI2D(1.0),2024-06-01,A,Y_GE15,OC5,T,THS_PER,CY,2023,55.0,
ESTAT:LFSA_EGAI2D(1.0),2024-06-01,A,Y_GE15,OC9,T,THS_PER,CY,2023,30.2,
"""

SAMPLE_EMPLOYMENT_CSV_WITH_MISSING = """\
DATAFLOW,LAST UPDATE,freq,age,isco08,sex,unit,geo,TIME_PERIOD,OBS_VALUE,OBS_FLAG
ESTAT:LFSA_EGAI2D(1.0),2024-06-01,A,Y_GE15,OC1,T,THS_PER,CY,2023,25.3,
ESTAT:LFSA_EGAI2D(1.0),2024-06-01,A,Y_GE15,OC3,T,THS_PER,CY,2023,:,
ESTAT:LFSA_EGAI2D(1.0),2024-06-01,A,Y_GE15,OC5,T,THS_PER,CY,2023,,
"""

SAMPLE_EARNINGS_CSV = """\
DATAFLOW,LAST UPDATE,freq,isco08,indic_se,nace_r2,worktime,geo,TIME_PERIOD,OBS_VALUE,OBS_FLAG
ESTAT:earn_ses_pub1s(1.0),2024-03-01,A,OC1,MEAN_ME_HRS,B-S,TOTAL,CY,2022,22.50,
ESTAT:earn_ses_pub1s(1.0),2024-03-01,A,OC2,MEAN_ME_HRS,B-S,TOTAL,CY,2022,18.30,
ESTAT:earn_ses_pub1s(1.0),2024-03-01,A,OC5,MEAN_ME_HRS,B-S,TOTAL,CY,2022,9.80,
ESTAT:earn_ses_pub1s(1.0),2024-03-01,A,OC9,MEAN_ME_HRS,B-S,TOTAL,CY,2022,7.20,
"""


def _mock_response(text, status_code=200):
    """Create a mock httpx.Response."""
    resp = MagicMock()
    resp.text = text
    resp.status_code = status_code
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value=json.loads(text) if text.startswith("{") else {})
    return resp


def _mock_client(response_text):
    """Create a mock httpx.Client that returns the given CSV text."""
    client = MagicMock()
    client.get.return_value = _mock_response(response_text)
    return client


# --- ISCO code reference tests ---


class TestIscoReferences:
    def test_major_groups_count(self):
        assert len(ISCO08_MAJOR_GROUPS) == 10

    def test_major_groups_codes(self):
        for code in ISCO08_MAJOR_GROUPS:
            assert code.startswith("OC")
            assert len(code) == 3

    def test_2digit_codes(self):
        for code in ISCO08_2DIGIT:
            assert code.startswith("OC")
            assert len(code) == 4

    def test_2digit_parent_exists(self):
        """Every 2-digit code's parent (first 3 chars) should be a valid major group."""
        for code in ISCO08_2DIGIT:
            parent = code[:3]
            assert parent in ISCO08_MAJOR_GROUPS, f"{code} parent {parent} not in major groups"


# --- fetch_sdmx_csv tests ---


class TestFetchSdmxCsv:
    def test_parses_csv_response(self):
        client = _mock_client(SAMPLE_EMPLOYMENT_CSV)
        rows = fetch_sdmx_csv("LFSA_EGAI2D", params={"geo": "CY"}, client=client)

        assert len(rows) == 6
        assert rows[0]["isco08"] == "OC1"
        assert rows[0]["OBS_VALUE"] == "25.3"
        assert rows[0]["TIME_PERIOD"] == "2023"

    def test_passes_correct_url(self):
        client = _mock_client(SAMPLE_EMPLOYMENT_CSV)
        fetch_sdmx_csv("LFSA_EGAI2D", params={"geo": "CY"}, client=client)

        call_args = client.get.call_args
        assert "LFSA_EGAI2D" in call_args[0][0]
        assert call_args[1]["params"]["format"] == "SDMX-CSV"
        assert call_args[1]["params"]["geo"] == "CY"

    def test_empty_response(self):
        csv_text = "DATAFLOW,LAST UPDATE,freq,isco08,geo,TIME_PERIOD,OBS_VALUE\n"
        client = _mock_client(csv_text)
        rows = fetch_sdmx_csv("LFSA_EGAI2D", client=client)
        assert rows == []


# --- fetch_employment_by_occupation tests ---


class TestFetchEmployment:
    def test_returns_parsed_records(self):
        client = _mock_client(SAMPLE_EMPLOYMENT_CSV)
        results = fetch_employment_by_occupation(geo="CY", client=client)

        assert len(results) == 6
        assert results[0]["isco_code"] == "OC1"
        assert results[0]["employment_thousands"] == 25.3
        assert results[0]["year"] == "2023"

    def test_labels_major_groups(self):
        client = _mock_client(SAMPLE_EMPLOYMENT_CSV)
        results = fetch_employment_by_occupation(client=client)

        oc1 = next(r for r in results if r["isco_code"] == "OC1")
        assert oc1["isco_label"] == "Managers"

    def test_labels_2digit(self):
        client = _mock_client(SAMPLE_EMPLOYMENT_CSV)
        results = fetch_employment_by_occupation(client=client)

        oc25 = next(r for r in results if r["isco_code"] == "OC25")
        assert oc25["isco_label"] == "Information and communications technology professionals"

    def test_skips_missing_values(self):
        client = _mock_client(SAMPLE_EMPLOYMENT_CSV_WITH_MISSING)
        results = fetch_employment_by_occupation(client=client)

        # Only OC1 should remain (OC3 has ":" and OC5 has empty value)
        assert len(results) == 1
        assert results[0]["isco_code"] == "OC1"

    def test_passes_parameters(self):
        client = _mock_client(SAMPLE_EMPLOYMENT_CSV)
        fetch_employment_by_occupation(geo="EL", sex="F", age="Y20-64", last_n=3, client=client)

        call_args = client.get.call_args
        params = call_args[1]["params"]
        assert params["geo"] == "EL"
        assert params["sex"] == "F"
        assert params["age"] == "Y20-64"
        assert params["lastNPeriods"] == "3"


# --- fetch_earnings_by_occupation tests ---


class TestFetchEarnings:
    def test_returns_parsed_records(self):
        client = _mock_client(SAMPLE_EARNINGS_CSV)
        results = fetch_earnings_by_occupation(geo="CY", client=client)

        assert len(results) == 4
        assert results[0]["isco_code"] == "OC1"
        assert results[0]["hourly_earnings_eur"] == 22.50
        assert results[0]["year"] == "2022"

    def test_labels_correctly(self):
        client = _mock_client(SAMPLE_EARNINGS_CSV)
        results = fetch_earnings_by_occupation(client=client)

        oc2 = next(r for r in results if r["isco_code"] == "OC2")
        assert oc2["isco_label"] == "Professionals"


# --- build_occupation_summary tests ---


class TestBuildOccupationSummary:
    def _sample_employment(self):
        return [
            {"isco_code": "OC1", "isco_label": "Managers", "employment_thousands": 25.3, "year": "2023"},
            {"isco_code": "OC2", "isco_label": "Professionals", "employment_thousands": 82.1, "year": "2023"},
            {"isco_code": "OC25", "isco_label": "ICT professionals", "employment_thousands": 12.5, "year": "2023"},
            {"isco_code": "OC22", "isco_label": "Health professionals", "employment_thousands": 8.3, "year": "2023"},
            {
                "isco_code": "OC5",
                "isco_label": "Service and sales workers",
                "employment_thousands": 55.0,
                "year": "2023",
            },
        ]

    def _sample_earnings(self):
        return [
            {"isco_code": "OC1", "isco_label": "Managers", "hourly_earnings_eur": 22.50, "year": "2022"},
            {"isco_code": "OC2", "isco_label": "Professionals", "hourly_earnings_eur": 18.30, "year": "2022"},
            {
                "isco_code": "OC5",
                "isco_label": "Service and sales workers",
                "hourly_earnings_eur": 9.80,
                "year": "2022",
            },
        ]

    def test_merges_data(self):
        summary = build_occupation_summary(self._sample_employment(), self._sample_earnings())

        # Should have all 10 major groups
        assert len(summary) == 10

        oc1 = next(s for s in summary if s["isco_code"] == "OC1")
        assert oc1["employment_thousands"] == 25.3
        assert oc1["hourly_earnings_eur"] == 22.50
        assert oc1["annual_earnings_eur"] == round(22.50 * 2080)

    def test_annual_earnings_calculation(self):
        summary = build_occupation_summary(self._sample_employment(), self._sample_earnings())

        oc5 = next(s for s in summary if s["isco_code"] == "OC5")
        assert oc5["annual_earnings_eur"] == round(9.80 * 2080)

    def test_missing_earnings_returns_none(self):
        summary = build_occupation_summary(self._sample_employment(), self._sample_earnings())

        # OC3 has no employment or earnings data
        oc3 = next(s for s in summary if s["isco_code"] == "OC3")
        assert oc3["hourly_earnings_eur"] is None
        assert oc3["annual_earnings_eur"] is None

    def test_sub_occupations_populated(self):
        summary = build_occupation_summary(self._sample_employment(), self._sample_earnings())

        oc2 = next(s for s in summary if s["isco_code"] == "OC2")
        # OC25 and OC22 are sub-occupations of OC2
        assert len(oc2["sub_occupations"]) == 2
        sub_codes = {s["isco_code"] for s in oc2["sub_occupations"]}
        assert sub_codes == {"OC25", "OC22"}

    def test_uses_1digit_total_over_aggregation(self):
        """When 1-digit total exists in source data, use it instead of summing 2-digit."""
        summary = build_occupation_summary(self._sample_employment(), self._sample_earnings())

        oc2 = next(s for s in summary if s["isco_code"] == "OC2")
        # OC2 total (82.1) should be used, not sum of OC25+OC22 (20.8)
        assert oc2["employment_thousands"] == 82.1

    def test_sorted_by_isco_code(self):
        summary = build_occupation_summary(self._sample_employment(), self._sample_earnings())

        codes = [s["isco_code"] for s in summary]
        assert codes == sorted(codes)


# --- JSON-stat endpoint tests ---


class TestFetchJsonStat:
    def test_parses_json_response(self):
        sample_json = json.dumps({"version": "2.0", "class": "dataset", "value": [25.3]})
        client = _mock_client(sample_json)
        # Override the mock to return parsed JSON
        client.get.return_value.json.return_value = json.loads(sample_json)

        result = fetch_json_stat("LFSA_EGAI2D", params={"geo": "CY"}, client=client)
        assert result["version"] == "2.0"
        assert result["value"] == [25.3]
