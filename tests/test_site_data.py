"""Tests to validate the static site is deployable and data.json schema is correct."""

import json
import os

SITE_DIR = os.path.join(os.path.dirname(__file__), "..", "site")
DATA_PATH = os.path.join(SITE_DIR, "data.json")
INDEX_PATH = os.path.join(SITE_DIR, "index.html")

REQUIRED_FIELDS = {"title", "slug", "category", "isco_code", "pay", "jobs", "education", "exposure"}
NUMERIC_FIELDS = {"pay", "jobs", "exposure"}


class TestSiteDataJson:
    def test_data_json_exists(self):
        assert os.path.isfile(DATA_PATH), "site/data.json must exist"

    def test_data_json_is_valid_json(self):
        with open(DATA_PATH) as f:
            data = json.load(f)
        assert isinstance(data, list), "data.json must be a JSON array"

    def test_data_json_not_empty(self):
        with open(DATA_PATH) as f:
            data = json.load(f)
        assert len(data) > 0, "data.json must contain at least one occupation"

    def test_all_records_have_required_fields(self):
        with open(DATA_PATH) as f:
            data = json.load(f)
        for i, record in enumerate(data):
            missing = REQUIRED_FIELDS - set(record.keys())
            assert not missing, f"Record {i} ({record.get('title', '?')}) missing fields: {missing}"

    def test_numeric_fields_are_numbers(self):
        with open(DATA_PATH) as f:
            data = json.load(f)
        for i, record in enumerate(data):
            for field in NUMERIC_FIELDS:
                val = record.get(field)
                if val is not None:
                    assert isinstance(val, (int, float)), (
                        f"Record {i} ({record.get('title', '?')}): {field} must be a number, got {type(val).__name__}"
                    )

    def test_exposure_scores_in_range(self):
        with open(DATA_PATH) as f:
            data = json.load(f)
        for record in data:
            exposure = record.get("exposure")
            if exposure is not None:
                assert 0 <= exposure <= 10, f"{record['title']}: exposure {exposure} not in 0-10"

    def test_slugs_are_unique(self):
        with open(DATA_PATH) as f:
            data = json.load(f)
        slugs = [r["slug"] for r in data]
        assert len(slugs) == len(set(slugs)), "Duplicate slugs found in data.json"


class TestSiteIndexHtml:
    def test_index_html_exists(self):
        assert os.path.isfile(INDEX_PATH), "site/index.html must exist"

    def test_index_html_contains_doctype(self):
        with open(INDEX_PATH) as f:
            content = f.read()
        assert content.strip().startswith("<!DOCTYPE html>"), "index.html must start with <!DOCTYPE html>"

    def test_index_html_contains_visualiser_title(self):
        with open(INDEX_PATH) as f:
            content = f.read()
        assert "Visualiser" in content, "index.html must use British English 'Visualiser'"

    def test_index_html_has_meta_description(self):
        with open(INDEX_PATH) as f:
            content = f.read()
        assert 'meta name="description"' in content, "index.html must have a meta description for SEO"

    def test_index_html_has_loading_state(self):
        with open(INDEX_PATH) as f:
            content = f.read()
        assert 'id="loading"' in content, "index.html must have a loading state element"

    def test_index_html_has_error_handling(self):
        with open(INDEX_PATH) as f:
            content = f.read()
        assert ".catch(" in content, "index.html must have error handling on fetch"


def test_no_occupation_inherits_its_major_group_total():
    """Regression: suppressed 2-digit codes used to get the whole 1-digit total."""
    cache = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "employment.json")
    with open(cache) as f:
        emp = json.load(f)
    parent_totals = {r["isco_code"]: r["employment_thousands"] for r in emp if len(r["isco_code"]) == 3}
    with open(DATA_PATH) as f:
        data = json.load(f)
    by_parent = {}
    for d in data:
        by_parent.setdefault(d["isco_code"][:3], []).append(d)
    for parent, children in by_parent.items():
        total_k = sum(c["jobs"] or 0 for c in children) / 1000
        assert abs(total_k - parent_totals[parent]) <= max(0.5, 0.02 * parent_totals[parent]), (
            f"{parent}: children sum to {total_k}k but major group total is {parent_totals[parent]}k"
        )
        if len(children) > 1:
            for c in children:
                assert c["jobs"] != round(parent_totals[parent] * 1000), f"{c['title']} equals its major group total"
