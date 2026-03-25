"""
Score each occupation's 10-year employment growth outlook using an LLM via OpenRouter.

Reads ISCO-08 occupation titles from occupations_cy.json and optionally
Eurostat historical CAGR data, then asks an LLM to project 10-year
employment growth for each occupation in the Cyprus/EU context.

Results are cached incrementally to outlook_scores.json so the script can be
resumed if interrupted.

Usage:
    uv run python score_outlook.py
    uv run python score_outlook.py --cagr-file cagr.json
    uv run python score_outlook.py --model google/gemini-3-flash-preview
    uv run python score_outlook.py --start 0 --end 10
"""

import argparse
import json
import os
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "google/gemini-3-flash-preview"
OUTPUT_FILE = "outlook_scores.json"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """\
You are an expert labour market analyst projecting 10-year employment growth \
for occupations in the Cyprus and EU labour market. You will be given an \
occupation description based on the ISCO-08 international classification.

Estimate the **projected 10-year employment change** as a percentage. \
Positive means growth (more jobs), negative means decline (fewer jobs).

Consider these factors:
- AI and automation impact on the occupation
- Demographic trends in Cyprus and the EU (ageing population, migration)
- Cyprus-specific sector dynamics:
  - Tourism and hospitality are major employers
  - Financial services, shipping, and professional services are key sectors
  - Construction and real estate are significant economic drivers
  - Public sector employment is proportionally larger than in the US
  - EU Digital Decade targets drive digital skills demand
  - Cyprus is positioning as an EU tech/fintech hub
- Global and EU megatrends (green transition, digital transformation, \
  healthcare demand growth)
- Whether the occupation is growing or declining across EU member states

Use these anchors to calibrate:

- **-10% or worse: Strong decline.** The occupation faces structural decline \
from automation, offshoring, or shrinking industries. \
Examples: data entry clerks, certain clerical/recording roles.

- **-5% to -1%: Moderate decline.** Some erosion from technology or changing \
demand, but not disappearing. \
Examples: some manufacturing assembly roles, basic administrative support.

- **0% to +2%: Stable.** Roughly keeping pace with population/economy. \
Examples: protective services, some trade occupations.

- **+3% to +6%: Moderate growth.** Growing demand from economic or \
demographic drivers. \
Examples: health professionals, business professionals, managers.

- **+7% to +12%: Strong growth.** High-demand occupation driven by \
technology, demographics, or policy. \
Examples: ICT professionals, personal care workers, health associate \
professionals.

- **+12% or more: Exceptional growth.** Reserved for occupations with \
extraordinary demand drivers. Rare — use sparingly.

Respond with ONLY a JSON object in this exact format, no other text:
{
  "outlook": <number, the projected 10-year employment change as a percentage>,
  "rationale": "<2-3 sentences explaining the key growth/decline drivers>"
}\
"""


def parse_llm_response(content):
    """Parse LLM response, stripping markdown fences if present."""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
    return json.loads(content)


def score_outlook(client, text, model):
    """Send one occupation to the LLM and parse the outlook response."""
    response = client.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "temperature": 0.2,
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return parse_llm_response(content)


def build_outlook_prompt(occ, cagr_data=None):
    """Build an outlook scoring prompt for an ISCO-08 occupation.

    Args:
        occ: Dict with title, isco_code, category_label, etc.
        cagr_data: Optional dict with historical CAGR info for this occupation.

    Returns:
        String prompt for LLM scoring.
    """
    lines = [f"# {occ['title']}"]
    lines.append("")

    if occ.get("isco_code"):
        lines.append(f"**ISCO-08 Code:** {occ['isco_code']}")
    if occ.get("category_label"):
        lines.append(f"**Major Group:** {occ['category_label']}")
    lines.append("")

    if cagr_data:
        cagr = cagr_data.get("cagr")
        start_year = cagr_data.get("start_year")
        end_year = cagr_data.get("end_year")
        if cagr is not None:
            lines.append(f"**Historical employment CAGR ({start_year}-{end_year}):** {cagr:+.1f}% per year")
            lines.append("")

    lines.append(
        f'This is the ISCO-08 sub-major group "{occ["title"]}". '
        "Project the 10-year employment change for this occupation group "
        "in the Cyprus/EU labour market. Consider AI impact, demographic "
        "trends, and sector-specific dynamics."
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score occupation growth outlook via LLM")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--occupations", default=None, help="Occupations JSON file (default: occupations_cy.json)")
    parser.add_argument("--cagr-file", default=None, help="JSON file with historical CAGR data per ISCO code")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--force", action="store_true", help="Re-score even if already cached")
    args = parser.parse_args()

    occ_path = args.occupations or "occupations_cy.json"

    with open(occ_path) as f:
        occupations = json.load(f)

    print(f"Using {occ_path}")

    # Load historical CAGR data if available
    cagr_by_code = {}
    if args.cagr_file and os.path.exists(args.cagr_file):
        with open(args.cagr_file) as f:
            cagr_by_code = json.load(f)
        print(f"Loaded CAGR data for {len(cagr_by_code)} ISCO codes")

    subset = occupations[args.start : args.end]

    # Load existing scores
    scores = {}
    if os.path.exists(OUTPUT_FILE) and not args.force:
        with open(OUTPUT_FILE) as f:
            for entry in json.load(f):
                scores[entry["slug"]] = entry

    print(f"Scoring outlook for {len(subset)} occupations with {args.model}")
    print(f"Already cached: {len(scores)}")

    errors = []
    client = httpx.Client()

    for i, occ in enumerate(subset):
        slug = occ["slug"]

        if slug in scores:
            continue

        cagr_data = cagr_by_code.get(occ.get("isco_code"))
        text = build_outlook_prompt(occ, cagr_data)

        print(f"  [{i + 1}/{len(subset)}] {occ['title']}...", end=" ", flush=True)

        try:
            result = score_outlook(client, text, args.model)
            scores[slug] = {
                "slug": slug,
                "title": occ["title"],
                "outlook": result["outlook"],
                "outlook_rationale": result["rationale"],
            }
            outlook = result["outlook"]
            print(f"outlook={outlook:+.1f}%")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(slug)

        # Save after each one (incremental checkpoint)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(list(scores.values()), f, indent=2)

        if i < len(subset) - 1:
            time.sleep(args.delay)

    client.close()

    print(f"\nDone. Scored {len(scores)} occupations, {len(errors)} errors.")
    if errors:
        print(f"Errors: {errors}")

    # Summary stats
    vals = [s for s in scores.values() if "outlook" in s]
    if vals:
        avg = sum(s["outlook"] for s in vals) / len(vals)
        growing = sum(1 for s in vals if s["outlook"] > 0)
        declining = sum(1 for s in vals if s["outlook"] < 0)
        stable = sum(1 for s in vals if s["outlook"] == 0)
        print(f"\nAverage outlook across {len(vals)} occupations: {avg:+.1f}%")
        print(f"Growing: {growing}, Stable: {stable}, Declining: {declining}")


if __name__ == "__main__":
    main()
