"""
Score each occupation's 10-year employment growth outlook using an LLM via OpenRouter.

Reads ISCO-08 occupation titles from occupations_cy.json and optionally
Eurostat historical CAGR data, then asks an LLM to project 10-year
employment growth for each occupation in the Cyprus/EU context.

Results are cached incrementally to outlook_scores.json so the script can be
resumed if interrupted.

Usage:
    uv run python make_cagr.py          # build cagr.json first (historical Eurostat growth)
    uv run python score_outlook.py      # reads cagr.json by default
    uv run python score_outlook.py --cagr-file other.json
    uv run python score_outlook.py --no-cagr   # score without historical data (not recommended)
    uv run python score_outlook.py --model openai/gpt-6-luna
    uv run python score_outlook.py --start 0 --end 10
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

import llm_scoring
from llm_scoring import InvalidScoreError, parse_llm_response, require_rationale  # noqa: F401 - re-exported

load_dotenv()

DEFAULT_MODEL = "openai/gpt-6-luna"
OUTPUT_FILE = "outlook_scores.json"

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


def make_to_entry(cagr_by_code):
    """Return a validator that turns the model's answer into the fields to store."""

    def to_entry(occ, result):
        outlook = result.get("outlook")
        if isinstance(outlook, str):
            try:
                outlook = float(outlook.strip().rstrip("%"))
            except ValueError:
                outlook = None
        if not isinstance(outlook, (int, float)) or isinstance(outlook, bool) or not -60 <= outlook <= 100:
            raise InvalidScoreError(f"outlook must be a % change between -60 and 100, got {result.get('outlook')!r}")
        if isinstance(outlook, float) and outlook.is_integer():
            outlook = int(outlook)
        entry = {"outlook": outlook, "outlook_rationale": require_rationale(result)}
        cagr_data = cagr_by_code.get(occ.get("isco_code"))
        if cagr_data and cagr_data.get("cagr") is not None:
            entry["historical_cagr"] = cagr_data["cagr"]
            entry["historical_period"] = f"{cagr_data['start_year']}-{cagr_data['end_year']}"
        return entry

    return to_entry


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


def is_stale(cached, cagr_data):
    """True if a cached score was made without the historical CAGR now available."""
    if not cagr_data or cagr_data.get("cagr") is None:
        return False
    return cached.get("historical_cagr") != cagr_data["cagr"]


def main():
    parser = argparse.ArgumentParser(description="Score occupation growth outlook via LLM")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--occupations", default=None, help="Occupations JSON file (default: occupations_cy.json)")
    parser.add_argument(
        "--cagr-file", default="cagr.json", help="JSON file with historical CAGR per ISCO code (from make_cagr.py)"
    )
    parser.add_argument("--no-cagr", action="store_true", help="Score without historical growth data")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument(
        "--force", action="store_true", help="Re-score the selected occupations even if cached (others are kept)"
    )
    args = parser.parse_args()

    occ_path = args.occupations or "occupations_cy.json"

    with open(occ_path) as f:
        occupations = json.load(f)

    print(f"Using {occ_path}")

    # Load historical CAGR data if available
    cagr_by_code = {}
    if not args.no_cagr:
        if not os.path.exists(args.cagr_file):
            parser.error(
                f"{args.cagr_file} not found. Run 'uv run python make_cagr.py' first, "
                "or pass --no-cagr to score without historical data."
            )
        with open(args.cagr_file) as f:
            cagr_by_code = json.load(f)
        print(f"Loaded CAGR data for {len(cagr_by_code)} ISCO codes")

    scores, errors = llm_scoring.run(
        occupations[args.start : args.end],
        output_file=OUTPUT_FILE,
        model=args.model,
        system_prompt=SYSTEM_PROMPT,
        build_prompt=lambda occ: build_outlook_prompt(occ, cagr_by_code.get(occ.get("isco_code"))),
        to_entry=make_to_entry(cagr_by_code),
        needs_scoring=lambda occ, cached: is_stale(cached, cagr_by_code.get(occ.get("isco_code"))),
        force=args.force,
        delay=args.delay,
    )

    # Summary stats
    vals = [s for s in scores.values() if "outlook" in s]
    if vals:
        avg = sum(s["outlook"] for s in vals) / len(vals)
        growing = sum(1 for s in vals if s["outlook"] > 0)
        declining = sum(1 for s in vals if s["outlook"] < 0)
        stable = sum(1 for s in vals if s["outlook"] == 0)
        print(f"\nAverage outlook across {len(vals)} occupations: {avg:+.1f}%")
        print(f"Growing: {growing}, Stable: {stable}, Declining: {declining}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
