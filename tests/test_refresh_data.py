"""Tests for refresh_data.py (scheduled data refresh helpers)."""

import json

from refresh_data import build_report, main, parse_wage_index, stale_outlook, update_wage_index


def test_parse_wage_index_skips_missing_values():
    rows = [
        {"TIME_PERIOD": "2024", "OBS_VALUE": "120.63"},
        {"TIME_PERIOD": "2025", "OBS_VALUE": ""},
        {"TIME_PERIOD": "2023", "OBS_VALUE": "115.4"},
        {"TIME_PERIOD": "", "OBS_VALUE": "1"},
    ]
    assert parse_wage_index(rows) == {"2023": 115.4, "2024": 120.6}


def test_update_wage_index_merges_into_cache(tmp_path):
    (tmp_path / "wage_index.json").write_text(json.dumps({"index": {"2020": 100.0, "2025": 124.7}}))
    seen = {}

    def fake_fetch(dataset, key):
        seen["dataset"], seen["key"] = dataset, key
        return [{"TIME_PERIOD": "2025", "OBS_VALUE": "125.0"}, {"TIME_PERIOD": "2026", "OBS_VALUE": "129.9"}]

    index = update_wage_index(str(tmp_path), fetch=fake_fetch)
    assert seen == {"dataset": "lc_lci_r2_a", "key": "A.I20.D11.B-S.CY"}
    assert index == {"2020": 100.0, "2025": 125.0, "2026": 129.9}
    saved = json.loads((tmp_path / "wage_index.json").read_text())
    assert saved["dataset"] == "lc_lci_r2_a" and saved["geo"] == "CY" and saved["index"] == index


def _rec(slug, jobs, pay, year="2025"):
    return {"slug": slug, "title": slug.title(), "jobs": jobs, "pay": pay, "year_employment": year}


def test_report_lists_changes():
    old = [_rec("a", 1000, 20000, "2024"), _rec("b", 2000, 30000, "2024")]
    new = [_rec("a", 1500, 20000), _rec("b", 2000, 30000)]
    report = build_report(old, new)
    assert "2024 → 2025" in report
    assert "3,000 → 3,500" in report
    assert "| A | 1.0k → 1.5k |" in report
    assert "| B |" not in report


def test_report_no_changes():
    data = [_rec("a", 1000, 20000)]
    assert build_report(data, data) == "No changes to the published data."


def test_stale_outlook():
    occs = [{"slug": "a", "title": "A", "isco_code": "OC1"}, {"slug": "b", "title": "B", "isco_code": "OC2"}]
    cagr = {"OC1": {"cagr": 1.5}, "OC2": {"cagr": 2.0}}
    outlook = {"a": {"historical_cagr": 1.5}, "b": {"historical_cagr": 1.9}}
    assert stale_outlook(cagr, outlook, occs) == ["B"]


def test_report_command_on_committed_data_has_no_changes(capsys, monkeypatch):
    import os

    monkeypatch.chdir(os.path.join(os.path.dirname(__file__), ".."))
    assert main(["report", "--old", "site/data.json"]) == 0
    assert capsys.readouterr().out.strip() == "No changes to the published data."
