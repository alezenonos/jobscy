"""
Generate the Cyprus master occupation list from ISCO-08 classification.

Produces occupations_cy.json with all ISCO-08 2-digit sub-major groups,
each tagged with its 1-digit major group as category. This is the Cyprus
equivalent of the BLS occupations.json.

Usage:
    uv run python generate_cy_occupations.py
    uv run python generate_cy_occupations.py --output occupations_cy.json
"""

import argparse
import json
import re

from eurostat import ISCO08_2DIGIT, ISCO08_MAJOR_GROUPS

# Map ISCO-08 1-digit codes to human-readable category names
ISCO_CATEGORIES = {
    "OC0": "armed-forces",
    "OC1": "managers",
    "OC2": "professionals",
    "OC3": "technicians-and-associate-professionals",
    "OC4": "clerical-support-workers",
    "OC5": "service-and-sales-workers",
    "OC6": "skilled-agriculture-forestry-fishery",
    "OC7": "craft-and-related-trades",
    "OC8": "plant-and-machine-operators",
    "OC9": "elementary-occupations",
}


def make_slug(title):
    """Convert an occupation title to a URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug


def generate_occupations(include_major_groups=False):
    """Generate the full list of Cyprus occupations from ISCO-08.

    Args:
        include_major_groups: If True, also include 1-digit major groups
            as separate entries (useful for aggregated views).

    Returns:
        List of occupation dicts with title, isco_code, category, slug.
    """
    occupations = []

    # Add 2-digit sub-major groups (the primary occupation units)
    for code in sorted(ISCO08_2DIGIT.keys()):
        title = ISCO08_2DIGIT[code]
        parent = code[:3]  # OC25 -> OC2
        category = ISCO_CATEGORIES.get(parent, "other")
        category_label = ISCO08_MAJOR_GROUPS.get(parent, "Other")

        occupations.append(
            {
                "title": title,
                "isco_code": code,
                "isco_parent": parent,
                "category": category,
                "category_label": category_label,
                "slug": make_slug(title),
            }
        )

    if include_major_groups:
        for code in sorted(ISCO08_MAJOR_GROUPS.keys()):
            title = ISCO08_MAJOR_GROUPS[code]
            category = ISCO_CATEGORIES.get(code, "other")

            occupations.append(
                {
                    "title": title,
                    "isco_code": code,
                    "isco_parent": None,
                    "category": category,
                    "category_label": title,
                    "slug": make_slug(title),
                }
            )

    return occupations


def main():
    parser = argparse.ArgumentParser(description="Generate Cyprus occupation list from ISCO-08")
    parser.add_argument("--output", default="occupations_cy.json", help="Output JSON file")
    parser.add_argument(
        "--include-major-groups",
        action="store_true",
        help="Include 1-digit major groups as separate entries",
    )
    args = parser.parse_args()

    occupations = generate_occupations(include_major_groups=args.include_major_groups)

    with open(args.output, "w") as f:
        json.dump(occupations, f, indent=2)

    print(f"Generated {len(occupations)} occupations → {args.output}")

    # Summary by category
    from collections import Counter

    cats = Counter(o["category"] for o in occupations)
    print("\nBy category:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
