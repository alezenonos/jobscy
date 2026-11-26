from make_cagr import build_cagr


def test_build_cagr_basic():
    history = {"OC25": {"2014": 10.0, "2019": 12.0, "2024": 20.0}}
    result = build_cagr(history)
    assert result["OC25"]["start_year"] == "2014"
    assert result["OC25"]["end_year"] == "2024"
    assert result["OC25"]["n_obs"] == 3
    assert abs(result["OC25"]["cagr"] - 7.18) < 0.01


def test_build_cagr_skips_short_series():
    history = {"OC62": {"2023": 0.4, "2024": 0.3}, "OC91": {"2020": 1.0, "2022": 1.0, "2024": 1.0}}
    result = build_cagr(history)
    assert "OC62" not in result
    assert result["OC91"]["cagr"] == 0.0


def test_build_cagr_skips_zero_values():
    history = {"OC01": {"2014": 0.0, "2019": 1.0, "2024": 2.0}}
    assert build_cagr(history) == {}
