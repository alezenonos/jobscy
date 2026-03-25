"""Tests for score_outlook.py — LLM outlook scoring utilities."""

from score_outlook import (
    SYSTEM_PROMPT,
    build_outlook_prompt,
    parse_llm_response,
)

# --- parse_llm_response ---


def test_parse_llm_response_clean_json():
    raw = '{"outlook": 5.2, "rationale": "Growing demand."}'
    result = parse_llm_response(raw)
    assert result["outlook"] == 5.2
    assert result["rationale"] == "Growing demand."


def test_parse_llm_response_with_json_fences():
    raw = '```json\n{"outlook": -3.0, "rationale": "Declining sector."}\n```'
    result = parse_llm_response(raw)
    assert result["outlook"] == -3.0


def test_parse_llm_response_with_whitespace():
    raw = '  \n  {"outlook": 0, "rationale": "Stable."}  \n  '
    result = parse_llm_response(raw)
    assert result["outlook"] == 0


# --- build_outlook_prompt ---


def test_build_outlook_prompt_basic():
    occ = {
        "title": "ICT Professionals",
        "isco_code": "OC25",
        "category_label": "Professionals",
        "slug": "ict-professionals",
    }
    prompt = build_outlook_prompt(occ)
    assert "# ICT Professionals" in prompt
    assert "**ISCO-08 Code:** OC25" in prompt
    assert "Cyprus/EU labour market" in prompt
    assert "10-year employment change" in prompt


def test_build_outlook_prompt_with_cagr():
    occ = {
        "title": "ICT Professionals",
        "isco_code": "OC25",
        "slug": "ict-professionals",
    }
    cagr_data = {"cagr": 3.5, "start_year": "2019", "end_year": "2024"}
    prompt = build_outlook_prompt(occ, cagr_data)
    assert "+3.5%" in prompt
    assert "2019" in prompt
    assert "2024" in prompt


def test_build_outlook_prompt_without_cagr():
    occ = {
        "title": "General Clerks",
        "slug": "general-clerks",
    }
    prompt = build_outlook_prompt(occ)
    assert "# General Clerks" in prompt
    assert "Historical" not in prompt


def test_build_outlook_prompt_minimal():
    occ = {"title": "Test Occupation", "slug": "test"}
    prompt = build_outlook_prompt(occ)
    assert "# Test Occupation" in prompt
    assert "ISCO-08 Code" not in prompt


# --- SYSTEM_PROMPT content ---


def test_system_prompt_contains_cyprus_context():
    assert "Cyprus" in SYSTEM_PROMPT
    assert "ISCO-08" in SYSTEM_PROMPT
    assert "EU" in SYSTEM_PROMPT


def test_system_prompt_contains_sector_references():
    assert "tourism" in SYSTEM_PROMPT.lower()
    assert "shipping" in SYSTEM_PROMPT.lower()
    assert "financial services" in SYSTEM_PROMPT.lower()


def test_system_prompt_contains_outlook_anchors():
    assert "Strong decline" in SYSTEM_PROMPT
    assert "Strong growth" in SYSTEM_PROMPT
    assert "data entry" in SYSTEM_PROMPT.lower()


def test_system_prompt_requests_json_format():
    assert '"outlook"' in SYSTEM_PROMPT
    assert '"rationale"' in SYSTEM_PROMPT
