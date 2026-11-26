"""
Score each occupation's AI exposure using an LLM via OpenRouter.

Reads ISCO-08 occupation titles from occupations_cy.json and scores each
for AI exposure in the Cyprus/EU labour market context.

Results are cached incrementally to scores.json so the script can be
resumed if interrupted. See llm_scoring.py for validation, retries and how
--force keeps the scores outside the selected range. Exits non-zero if any
occupation failed.

Usage:
    uv run python score.py                                    # auto-detect input
    uv run python score.py --occupations occupations_cy.json  # Cyprus occupations
    uv run python score.py --model openai/gpt-6-luna
    uv run python score.py --start 0 --end 10                 # test on first 10
"""

import argparse
import json
import sys

from dotenv import load_dotenv

import llm_scoring
from llm_scoring import InvalidScoreError, parse_llm_response, require_rationale  # noqa: F401 - re-exported

load_dotenv()

DEFAULT_MODEL = "openai/gpt-6-luna"
OUTPUT_FILE = "scores.json"

SYSTEM_PROMPT = """\
You are an expert labour market analyst evaluating how exposed different \
occupations are to AI. You will be given an occupation description based on \
the ISCO-08 international classification, in the context of the Cyprus and \
EU labour market.

Rate the occupation's overall **AI Exposure** on a scale from 0 to 10.

AI Exposure measures: how much will AI reshape this occupation? Consider both \
direct effects (AI automating tasks currently done by humans) and indirect \
effects (AI making each worker so productive that fewer are needed).

A key signal is whether the job's work product is fundamentally digital. If \
the job can be done entirely from a home office on a computer — writing, \
coding, analysing, communicating — then AI exposure is inherently high (7+), \
because AI capabilities in digital domains are advancing rapidly. Even if \
today's AI can't handle every aspect of such a job, the trajectory is steep \
and the ceiling is very high. Conversely, jobs requiring physical presence, \
manual skill, or real-time human interaction in the physical world have a \
natural barrier to AI exposure.

Consider the Cyprus/EU context where relevant:
- Tourism and hospitality are major employers in Cyprus
- Financial services and shipping are key sectors
- The EU Digital Decade targets drive digital skills demand
- Public sector employment is proportionally larger than in the US
- Construction and real estate are significant economic drivers

Use these anchors to calibrate your score:

- **0–1: Minimal exposure.** The work is almost entirely physical, hands-on, \
or requires real-time human presence in unpredictable environments. AI has \
essentially no impact on daily work. \
Examples: agricultural labourer, construction labourer, commercial diver.

- **2–3: Low exposure.** Mostly physical or interpersonal work. AI might help \
with minor peripheral tasks (scheduling, paperwork) but doesn't touch the \
core job. \
Examples: electrician, plumber, firefighter, building trades worker.

- **4–5: Moderate exposure.** A mix of physical/interpersonal work and \
knowledge work. AI can meaningfully assist with the information-processing \
parts but a substantial share of the job still requires human presence. \
Examples: health associate professional, police officer, personal care worker.

- **6–7: High exposure.** Predominantly knowledge work with some need for \
human judgment, relationships, or physical presence. AI tools are already \
useful and workers using AI may be substantially more productive. \
Examples: teaching professional, manager, business administration professional.

- **8–9: Very high exposure.** The job is almost entirely done on a computer. \
All core tasks — writing, coding, analysing, designing, communicating — are \
in domains where AI is rapidly improving. The occupation faces major \
restructuring. \
Examples: ICT professional, legal professional, business/admin associate \
professional.

- **10: Maximum exposure.** Routine information processing, fully digital, \
with no physical component. AI can already do most of it today. \
Examples: general clerk, numerical recording clerk, data entry operator.

Respond with ONLY a JSON object in this exact format, no other text:
{
  "exposure": <0-10>,
  "rationale": "<2-3 sentences explaining the key factors>"
}\
"""


def to_entry(occ, result):
    """Validate the model's answer and return the fields to store."""
    exposure = result.get("exposure")
    if isinstance(exposure, float) and exposure.is_integer():
        exposure = int(exposure)
    if not isinstance(exposure, int) or isinstance(exposure, bool) or not 0 <= exposure <= 10:
        raise InvalidScoreError(f"exposure must be a whole number 0-10, got {exposure!r}")
    return {"exposure": exposure, "rationale": require_rationale(result)}


def build_isco_prompt(occ):
    """Build a scoring prompt from an ISCO-08 occupation entry.

    When no detailed markdown description is available, constructs a
    prompt from the occupation metadata (title, ISCO code, category).

    Args:
        occ: Dict with title, isco_code, category_label, etc.

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
    lines.append(
        f'This is the ISCO-08 sub-major group "{occ["title"]}". '
        "Score this occupation group's AI exposure based on the typical "
        "duties and work environment of workers in this category within "
        "the Cyprus/EU labour market."
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score occupation AI exposure via LLM")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--occupations", default=None, help="Occupations JSON file (default: occupations_cy.json)")
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

    scores, errors = llm_scoring.run(
        occupations[args.start : args.end],
        output_file=OUTPUT_FILE,
        model=args.model,
        system_prompt=SYSTEM_PROMPT,
        build_prompt=build_isco_prompt,
        to_entry=to_entry,
        force=args.force,
        delay=args.delay,
    )

    # Summary stats
    vals = [s for s in scores.values() if "exposure" in s]
    if vals:
        avg = sum(s["exposure"] for s in vals) / len(vals)
        by_score = {}
        for s in vals:
            by_score[s["exposure"]] = by_score.get(s["exposure"], 0) + 1
        print(f"\nAverage exposure across {len(vals)} occupations: {avg:.1f}")
        print("Distribution:")
        for k in sorted(by_score):
            print(f"  {k}: {'█' * by_score[k]} ({by_score[k]})")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
