"""Tests for forecasts.py: wage uplift, sector pay and official forecast loaders."""

import json
import os

import pytest

from forecasts import enrich, load_cedefop, load_hrda, load_sector_pay, load_wage_uplift


@pytest.fixture
def cache(tmp_path):
    (tmp_path / "wage_index.json").write_text(json.dumps({"index": {"2020": 100.0, "2022": 108.0, "2025": 124.7}}))
    (tmp_path / "earnings_by_sector.json").write_text(
        json.dumps(
            [
                {"isco_code": "OC2", "nace_r2": "J", "annual_earnings_eur": 53572.0, "employees": 5957},
                {"isco_code": "OC2", "nace_r2": "I", "annual_earnings_eur": 25173.0, "employees": 1473},
                {"isco_code": "OC2", "nace_r2": "L", "annual_earnings_eur": 99999.0, "employees": 120},
                {"isco_code": "OC2", "nace_r2": "S", "annual_earnings_eur": 30000.0, "employees": None},
            ]
        )
    )
    (tmp_path / "hrda_2022_2032.csv").write_text(
        "isco_code,emp_2022,emp_2032,expansion_per_year,replacement_per_year,total_per_year\n"
        "OC25,6816,10174,336,82,417\n"
    )
    (tmp_path / "cedefop_2035.json").write_text(
        json.dumps(
            {"occupations": {"OC25": {"job_openings": 9200, "growth_pct": 67.73, "growth": 6100, "replacement": 3100}}}
        )
    )
    return str(tmp_path)


class TestWageUplift:
    def test_factor_to_latest_year(self, cache):
        factor, year = load_wage_uplift("2022", cache)
        assert year == "2025"
        assert factor == pytest.approx(124.7 / 108.0)

    def test_missing_base_year(self, cache):
        assert load_wage_uplift("2014", cache) == (1.0, "2014")

    def test_missing_file(self, tmp_path):
        assert load_wage_uplift("2022", str(tmp_path)) == (1.0, "2022")


class TestSectorPay:
    def test_drops_small_and_unknown_cells_and_sorts(self, cache):
        out = load_sector_pay(cache)
        assert [s["sector"] for s in out["OC2"]] == ["J", "I"]
        assert out["OC2"][0]["name"] == "ICT & media"
        assert out["OC2"][0]["pay"] == 53572


class TestForecastLoaders:
    def test_hrda(self, cache):
        h = load_hrda(cache)["OC25"]
        assert h == {"emp_2022": 6816, "emp_2032": 10174, "expansion": 336, "replacement": 82, "total": 417}

    def test_cedefop(self, cache):
        assert load_cedefop(cache)["OC25"]["job_openings"] == 9200

    def test_missing_files_give_empty(self, tmp_path):
        assert load_hrda(str(tmp_path)) == {}
        assert load_cedefop(str(tmp_path)) == {}
        assert load_sector_pay(str(tmp_path)) == {}


class TestEnrich:
    def _record(self):
        return {
            "isco_code": "OC25",
            "pay": 41771,
            "pay_hourly": 18.9,
            "pay_median": 36486,
            "pay_p10": 18386,
            "pay_p90": 72986,
            "year_earnings": "2022",
        }

    def test_pay_uplift_keeps_survey_value(self, cache):
        (d,) = enrich([self._record()], cache)
        factor = 124.7 / 108.0
        assert d["pay_survey"] == 41771
        assert d["pay_survey_year"] == "2022"
        assert d["pay"] == round(41771 * factor)
        assert d["pay_p90"] == round(72986 * factor)
        assert d["pay_hourly"] == round(18.9 * factor, 2)
        assert d["pay_estimated"] is True
        assert d["pay_year"] == "2025"
        assert d["pay_uplift_pct"] == 15.5

    def test_sector_pay_is_uplifted_too(self, cache):
        (d,) = enrich([self._record()], cache)
        assert d["pay_by_sector"][0]["pay"] == round(53572 * 124.7 / 108.0)

    def test_forecasts(self, cache):
        (d,) = enrich([self._record()], cache)
        assert d["hrda_openings_per_year"] == 417
        assert d["hrda_change_pct"] == pytest.approx(49.3)
        assert d["hrda_openings_rate"] == pytest.approx(6.12)
        assert d["cedefop_openings_2035"] == 9200
        assert d["cedefop_growth_pct"] == 67.73

    def test_no_index_leaves_pay_unchanged(self, tmp_path):
        (d,) = enrich([self._record()], str(tmp_path))
        assert d["pay"] == 41771
        assert d["pay_estimated"] is False
        assert "hrda_openings_per_year" not in d


def test_real_cache_covers_every_site_group():
    """The committed HRDA and Cedefop files cover the occupations on the site."""
    root = os.path.join(os.path.dirname(__file__), "..")
    with open(os.path.join(root, "site", "data.json")) as f:
        codes = {r["isco_code"] for r in json.load(f)}
    hrda = load_hrda(os.path.join(root, "data", "cache"))
    cedefop = load_cedefop(os.path.join(root, "data", "cache"))
    assert codes <= set(hrda)
    # Cedefop does not publish assemblers (OC82) for Cyprus.
    assert codes - set(cedefop) <= {"OC82"}
