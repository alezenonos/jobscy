"""Tests for the Cyprus vs EU layers: location quotient and pay vs EU/Greece."""

import json

import pytest

from forecasts import add_eu_compare
from refresh_data import fetch_eu_compare, flatten_json_stat, main, update_eu_compare


def _json_stat(dims, values):
    """Build a minimal JSON-stat response. dims: [(name, [codes])], values: {flat position: value}."""
    return {
        "id": [d for d, _ in dims],
        "size": [len(c) for _, c in dims],
        "dimension": {d: {"category": {"index": {code: i for i, code in enumerate(c)}}} for d, c in dims},
        "value": {str(k): v for k, v in values.items()},
    }


EMPLOYMENT = _json_stat(
    [
        ("freq", ["A"]),
        ("isco08", ["TOTAL", "OC2", "OC21", "OC22", "OC1-5"]),
        ("geo", ["EU27_2020"]),
        ("time", ["2025"]),
    ],
    {0: 200000.0, 1: 50000.0, 2: 8000.0, 3: 6000.0, 4: 1.0},
)


def _earnings(unit_factor=1.0):
    # geo order on purpose not CY first, as Eurostat returns it
    return _json_stat(
        [
            ("isco08", ["OC2", "OC9", "OC1-5"]),
            ("unit", ["EUR"]),
            ("geo", ["EU27_2020", "EL", "CY"]),
            ("time", ["2022"]),
        ],
        {
            0: 50000 * unit_factor,
            1: 30000 * unit_factor,
            2: 40000 * unit_factor,
            3: 24000 * unit_factor,
            5: 16000 * unit_factor,
            6: 1.0,
        },
    )


def fake_fetch(dataset, params=None):
    if dataset == "lfsa_egai2d":
        return EMPLOYMENT
    return _earnings(1.1 if params["unit"] == "PPS" else 1.0)


def test_flatten_json_stat_maps_positions_to_codes():
    rows = flatten_json_stat(_earnings())
    by = {(r["geo"], r["isco08"]): r["value"] for r in rows}
    assert by[("CY", "OC2")] == 40000
    assert by[("EL", "OC2")] == 30000
    assert by[("EU27_2020", "OC9")] == 24000
    assert ("EL", "OC9") not in by  # missing value is skipped


def test_flatten_json_stat_accepts_value_list():
    data = _json_stat([("geo", ["CY", "EL"])], {})
    data["value"] = [1.5, None]
    assert flatten_json_stat(data) == [{"geo": "CY", "value": 1.5}]


def test_fetch_eu_compare_keeps_single_groups():
    out = fetch_eu_compare(fake_fetch)
    assert out["employment"]["year"] == "2025"
    assert out["employment"]["thousands"] == {"OC2": 50000.0, "OC21": 8000.0, "OC22": 6000.0, "TOTAL": 200000.0}
    assert out["earnings"]["year"] == "2022"
    assert out["earnings"]["EUR"]["CY"] == {"OC2": 40000, "OC9": 16000}
    assert "OC9" not in out["earnings"]["EUR"]["EL"]
    assert out["earnings"]["PPS"]["EU27_2020"]["OC2"] == pytest.approx(55000)


def test_update_eu_compare_writes_cache(tmp_path):
    update_eu_compare(str(tmp_path), fetch=fake_fetch)
    saved = json.loads((tmp_path / "eu_compare.json").read_text())
    assert saved["employment"]["thousands"]["OC21"] == 8000.0


def test_eu_compare_command_keeps_cache_when_eurostat_fails(tmp_path, monkeypatch, capsys):
    (tmp_path / "eu_compare.json").write_text('{"keep": true}')

    def boom(*a, **k):
        raise RuntimeError("blocked")

    monkeypatch.setattr("refresh_data.fetch_json_stat", boom)
    assert main(["eu-compare", "--cache-dir", str(tmp_path)]) == 0
    assert json.loads((tmp_path / "eu_compare.json").read_text()) == {"keep": True}
    assert "not updated" in capsys.readouterr().out


@pytest.fixture
def cache(tmp_path):
    update_eu_compare(str(tmp_path), fetch=fake_fetch)
    return str(tmp_path)


def test_location_quotient(cache):
    records = [
        {"isco_code": "OC21", "jobs": 3000},  # 30% of Cyprus vs 8/14 = 57% of EU
        {"isco_code": "OC22", "jobs": 7000},  # 70% of Cyprus vs 6/14 = 43% of EU
        {"isco_code": "OC99", "jobs": 5000},  # no EU figure: left out of both totals
    ]
    add_eu_compare(records, cache)
    assert records[0]["jobs_lq"] == pytest.approx(0.3 / (8 / 14), abs=0.01)
    assert records[1]["jobs_lq"] == pytest.approx(0.7 / (6 / 14), abs=0.01)
    assert records[1]["jobs_cy_share_pct"] == 70.0
    assert records[1]["jobs_eu_year"] == "2025"
    assert "jobs_lq" not in records[2]


def test_pay_vs_eu_and_greece(cache):
    (d,) = add_eu_compare([{"isco_code": "OC21", "jobs": 1000}], cache)
    assert d["pay_vs_eu_pct"] == 80
    assert d["pay_vs_el_pct"] == 133
    assert d["pay_vs_eu_pps_pct"] == 80
    assert d["pay_eu"] == 50000 and d["pay_el"] == 30000
    assert d["pay_compare_year"] == "2022"


def test_missing_cyprus_pay_is_skipped(cache):
    (d,) = add_eu_compare([{"isco_code": "OC31", "jobs": 1000}], cache)
    assert "pay_vs_eu_pct" not in d


def test_no_cache_file_changes_nothing(tmp_path):
    rec = {"isco_code": "OC21", "jobs": 1000}
    add_eu_compare([rec], str(tmp_path))
    assert rec == {"isco_code": "OC21", "jobs": 1000}


def test_committed_data_has_eu_fields():
    with open("site/data.json") as f:
        data = json.load(f)
    with_lq = [d for d in data if d.get("jobs_lq") is not None]
    assert len(with_lq) == len(data)
    # Shares over the same groups sum to 100% on both sides
    assert sum(d["jobs_cy_share_pct"] for d in data) == pytest.approx(100, abs=0.5)
    assert sum(d["jobs_eu_share_pct"] for d in data) == pytest.approx(100, abs=0.5)
    assert all(d.get("pay_vs_eu_pct") for d in data)
