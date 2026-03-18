"""Tests for generate_cy_occupations.py — ISCO-08 occupation list generation."""

from generate_cy_occupations import ISCO_CATEGORIES, generate_occupations, make_slug


class TestMakeSlug:
    def test_basic(self):
        assert make_slug("Chief executives") == "chief-executives"

    def test_special_chars(self):
        # & is stripped, consecutive hyphens collapsed
        assert make_slug("Science & engineering professionals") == "science-engineering-professionals"

    def test_commas(self):
        slug = make_slug("Building and related trades workers, excluding electricians")
        assert "," not in slug
        assert slug == "building-and-related-trades-workers-excluding-electricians"

    def test_uppercase(self):
        assert make_slug("ICT Professionals") == "ict-professionals"

    def test_empty(self):
        assert make_slug("") == ""


class TestGenerateOccupations:
    def test_returns_2digit_occupations(self):
        occs = generate_occupations()
        # Should be exactly the number of ISCO-08 2-digit codes (39 sub-major groups)
        from eurostat import ISCO08_2DIGIT

        assert len(occs) == len(ISCO08_2DIGIT)

    def test_all_have_required_fields(self):
        occs = generate_occupations()
        for occ in occs:
            assert "title" in occ
            assert "isco_code" in occ
            assert "isco_parent" in occ
            assert "category" in occ
            assert "category_label" in occ
            assert "slug" in occ

    def test_isco_codes_are_2digit(self):
        occs = generate_occupations()
        for occ in occs:
            assert len(occ["isco_code"]) == 4  # e.g. "OC25"
            assert occ["isco_code"].startswith("OC")

    def test_parent_codes_are_1digit(self):
        occs = generate_occupations()
        for occ in occs:
            assert len(occ["isco_parent"]) == 3  # e.g. "OC2"

    def test_categories_are_valid(self):
        occs = generate_occupations()
        valid_cats = set(ISCO_CATEGORIES.values())
        for occ in occs:
            assert occ["category"] in valid_cats, f"Invalid category: {occ['category']}"

    def test_slugs_are_unique(self):
        occs = generate_occupations()
        slugs = [o["slug"] for o in occs]
        assert len(slugs) == len(set(slugs)), "Duplicate slugs found"

    def test_sorted_by_isco_code(self):
        occs = generate_occupations()
        codes = [o["isco_code"] for o in occs]
        assert codes == sorted(codes)

    def test_include_major_groups(self):
        occs = generate_occupations(include_major_groups=True)
        from eurostat import ISCO08_2DIGIT, ISCO08_MAJOR_GROUPS

        assert len(occs) == len(ISCO08_2DIGIT) + len(ISCO08_MAJOR_GROUPS)

        # Check major groups have no parent
        majors = [o for o in occs if o["isco_parent"] is None]
        assert len(majors) == 10

    def test_ict_professionals_present(self):
        occs = generate_occupations()
        ict = [o for o in occs if o["isco_code"] == "OC25"]
        assert len(ict) == 1
        assert "information and communications technology" in ict[0]["title"].lower()
        assert ict[0]["category"] == "professionals"


class TestIscoCategories:
    def test_all_major_groups_have_category(self):
        from eurostat import ISCO08_MAJOR_GROUPS

        for code in ISCO08_MAJOR_GROUPS:
            assert code in ISCO_CATEGORIES, f"Missing category for {code}"

    def test_categories_are_slug_format(self):
        for cat in ISCO_CATEGORIES.values():
            assert " " not in cat
            assert cat == cat.lower()
