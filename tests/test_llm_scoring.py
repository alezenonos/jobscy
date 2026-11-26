"""Tests for llm_scoring.py and the validators in score.py / score_outlook.py."""

import json

import httpx
import pytest

import llm_scoring
from llm_scoring import InvalidScoreError
from score import to_entry as exposure_entry
from score_outlook import make_to_entry

OCCS = [{"slug": f"occ-{i}", "title": f"Occupation {i}", "isco_code": f"OC{i}"} for i in range(1, 6)]
NOW = "2026-11-26T00:00:00+00:00"


def _run(tmp_path, answers, occupations=OCCS, **kw):
    """Run the loop with a fake LLM that returns `answers` in turn (or raises them)."""
    calls = []

    def fake_call(client, system_prompt, text, model):
        calls.append(text)
        a = answers.pop(0) if isinstance(answers, list) else answers
        if isinstance(a, Exception):
            raise a
        return a

    out = tmp_path / "scores.json"
    scores, errors = llm_scoring.run(
        occupations,
        output_file=str(out),
        model="test/model",
        system_prompt="sys",
        build_prompt=lambda occ: occ["title"],
        to_entry=exposure_entry,
        client=object(),
        call=fake_call,
        sleep=lambda s: None,
        now=lambda: NOW,
        delay=0,
        **kw,
    )
    return scores, errors, calls, out


def _write(path, entries):
    path.write_text(json.dumps(entries))


# --- keeping saved scores ---


def test_force_on_a_subset_keeps_the_other_scores(tmp_path):
    out = tmp_path / "scores.json"
    _write(out, [{"slug": o["slug"], "title": o["title"], "exposure": 1, "rationale": "old"} for o in OCCS])
    scores, errors, calls, _ = _run(tmp_path, {"exposure": 9, "rationale": "new"}, occupations=OCCS[:2], force=True)
    saved = {e["slug"]: e for e in json.loads(out.read_text())}
    assert len(saved) == 5
    assert saved["occ-1"]["exposure"] == 9 and saved["occ-2"]["exposure"] == 9
    assert all(saved[f"occ-{i}"]["rationale"] == "old" for i in (3, 4, 5))
    assert len(calls) == 2 and errors == []


def test_cached_scores_are_skipped_without_force(tmp_path):
    out = tmp_path / "scores.json"
    _write(out, [{"slug": "occ-1", "title": "Occupation 1", "exposure": 3, "rationale": "x"}])
    _, _, calls, _ = _run(tmp_path, {"exposure": 5, "rationale": "y"})
    assert calls == ["Occupation 2", "Occupation 3", "Occupation 4", "Occupation 5"]


def test_needs_scoring_hook_rescores_stale_entries(tmp_path):
    out = tmp_path / "scores.json"
    _write(out, [{"slug": o["slug"], "title": o["title"], "exposure": 3, "rationale": "x"} for o in OCCS])
    _, _, calls, _ = _run(
        tmp_path, {"exposure": 5, "rationale": "y"}, needs_scoring=lambda occ, cached: occ["slug"] == "occ-3"
    )
    assert calls == ["Occupation 3"]


def test_failed_item_keeps_its_old_score(tmp_path):
    out = tmp_path / "scores.json"
    _write(out, [{"slug": "occ-1", "title": "Occupation 1", "exposure": 3, "rationale": "old"}])
    scores, errors, _, _ = _run(tmp_path, [RuntimeError("boom")], occupations=OCCS[:1], force=True)
    assert errors == ["occ-1"]
    assert json.loads(out.read_text())[0]["rationale"] == "old"


def test_save_is_atomic_and_leaves_no_temp_file(tmp_path):
    _, _, _, out = _run(tmp_path, {"exposure": 5, "rationale": "y"}, occupations=OCCS[:1])
    assert out.exists() and not (tmp_path / "scores.json.tmp").exists()


# --- validation and provenance ---


def test_invalid_answer_is_retried_once_then_accepted(tmp_path):
    scores, errors, calls, _ = _run(
        tmp_path, [{"exposure": 14, "rationale": "too high"}, {"exposure": 7, "rationale": "ok"}], occupations=OCCS[:1]
    )
    assert errors == [] and len(calls) == 2 and scores["occ-1"]["exposure"] == 7


def test_invalid_twice_counts_as_error(tmp_path):
    scores, errors, calls, _ = _run(
        tmp_path, [{"exposure": "high", "rationale": "x"}, {"exposure": 5, "rationale": ""}], occupations=OCCS[:1]
    )
    assert errors == ["occ-1"] and len(calls) == 2 and "occ-1" not in scores


def test_entries_record_model_and_time(tmp_path):
    scores, _, _, _ = _run(tmp_path, {"exposure": 5, "rationale": "y"}, occupations=OCCS[:1])
    assert scores["occ-1"]["model"] == "test/model"
    assert scores["occ-1"]["scored_at"] == NOW


@pytest.mark.parametrize(
    "answer, ok",
    [
        ({"exposure": 0, "rationale": "r"}, True),
        ({"exposure": 10.0, "rationale": "r"}, True),
        ({"exposure": 11, "rationale": "r"}, False),
        ({"exposure": -1, "rationale": "r"}, False),
        ({"exposure": 4.5, "rationale": "r"}, False),
        ({"exposure": True, "rationale": "r"}, False),
        ({"exposure": 5}, False),
        ({"exposure": 5, "rationale": "  "}, False),
    ],
)
def test_exposure_validation(answer, ok):
    if ok:
        assert 0 <= exposure_entry({}, answer)["exposure"] <= 10
    else:
        with pytest.raises(InvalidScoreError):
            exposure_entry({}, answer)


@pytest.mark.parametrize(
    "answer, expected",
    [
        ({"outlook": 5, "rationale": "r"}, 5),
        ({"outlook": -3.5, "rationale": "r"}, -3.5),
        ({"outlook": "+7%", "rationale": "r"}, 7),
        ({"outlook": 400, "rationale": "r"}, None),
        ({"outlook": "lots", "rationale": "r"}, None),
        ({"outlook": 3}, None),
    ],
)
def test_outlook_validation(answer, expected):
    to_entry = make_to_entry({"OC1": {"cagr": 1.2, "start_year": 2011, "end_year": 2025}})
    occ = {"isco_code": "OC1"}
    if expected is None:
        with pytest.raises(InvalidScoreError):
            to_entry(occ, answer)
    else:
        entry = to_entry(occ, answer)
        assert entry["outlook"] == expected
        assert entry["historical_cagr"] == 1.2 and entry["historical_period"] == "2011-2025"


# --- HTTP retries ---


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.posts = 0

    def post(self, *args, **kwargs):
        self.posts += 1
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def _ok(content):
    return httpx.Response(
        200, json={"choices": [{"message": {"content": content}}]}, request=httpx.Request("POST", "x")
    )


def _status(code, headers=None):
    return httpx.Response(code, headers=headers or {}, request=httpx.Request("POST", "x"))


def test_call_llm_retries_rate_limits_and_server_errors(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    waits = []
    client = FakeClient([_status(429, {"retry-after": "7"}), _status(503), _ok('{"exposure": 4, "rationale": "r"}')])
    result = llm_scoring.call_llm(client, "s", "t", "m", backoff=1, sleep=waits.append)
    assert result == {"exposure": 4, "rationale": "r"}
    assert waits == [7.0, 2]  # Retry-After honoured, then exponential backoff (1 * 2**1)


def test_call_llm_retries_timeouts(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    client = FakeClient([httpx.ReadTimeout("slow"), _ok('```json\n{"exposure": 2, "rationale": "r"}\n```')])
    assert llm_scoring.call_llm(client, "s", "t", "m", sleep=lambda s: None)["exposure"] == 2


def test_call_llm_gives_up_after_retries(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    client = FakeClient([_status(500)] * 3)
    with pytest.raises(httpx.HTTPStatusError):
        llm_scoring.call_llm(client, "s", "t", "m", retries=2, sleep=lambda s: None)
    assert client.posts == 3


def test_call_llm_does_not_retry_client_errors(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    client = FakeClient([_status(401)])
    with pytest.raises(httpx.HTTPStatusError):
        llm_scoring.call_llm(client, "s", "t", "m", sleep=lambda s: None)
    assert client.posts == 1


def test_call_llm_non_json_answer_is_invalid(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    with pytest.raises(InvalidScoreError):
        llm_scoring.call_llm(FakeClient([_ok("I think about 5")]), "s", "t", "m", sleep=lambda s: None)
