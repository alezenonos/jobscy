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
