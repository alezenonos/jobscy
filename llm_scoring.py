"""
Shared LLM scoring loop for score.py (AI exposure) and score_outlook.py (growth outlook).

What it guarantees:
- Saved scores are never lost. The cache is always loaded; --force only re-scores
  the occupations in the selected range and keeps every other entry. Each save
  writes a temporary file and renames it, so an interrupted run can't leave a
  half-written JSON file.
- Every answer is validated (type, range, non-empty rationale). An invalid answer
  is retried once, then counted as an error and the old score is kept.
- Rate limits (429), server errors (5xx), timeouts and connection errors are
  retried with exponential backoff.
- Each new entry records the model and the time it was scored.
- run() returns the failed slugs, and the scripts exit non-zero when any failed.
"""

import datetime
import json
import os
import time

import httpx

API_URL = "https://openrouter.ai/api/v1/chat/completions"
RETRYABLE_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}


class InvalidScoreError(ValueError):
    """The model answered, but not with a usable score."""


def parse_llm_response(content):
    """Parse an LLM response as JSON, stripping markdown fences if present."""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
    return json.loads(content)


def call_llm(client, system_prompt, text, model, retries=4, backoff=2.0, sleep=time.sleep):
    """Ask the model and return its parsed JSON answer.

    Retries rate limits, 5xx errors, timeouts and connection errors, waiting
    backoff, 2×backoff, 4×backoff... seconds (or the server's Retry-After).
    """
    for attempt in range(retries + 1):
        try:
            response = client.post(
                API_URL,
                headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                    "temperature": 0.2,
                },
                timeout=60,
            )
            if response.status_code in RETRYABLE_STATUS and attempt < retries:
                wait = _retry_after(response) or backoff * (2**attempt)
                print(f"(HTTP {response.status_code}, retrying in {wait:.0f}s)", end=" ", flush=True)
                sleep(wait)
                continue
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            try:
                result = parse_llm_response(content)
            except (json.JSONDecodeError, IndexError) as e:
                raise InvalidScoreError(f"not valid JSON: {content[:80]!r}") from e
            if not isinstance(result, dict):
                raise InvalidScoreError(f"expected a JSON object, got {type(result).__name__}")
            return result
        except (httpx.TimeoutException, httpx.TransportError):
            if attempt >= retries:
                raise
            wait = backoff * (2**attempt)
            print(f"(network error, retrying in {wait:.0f}s)", end=" ", flush=True)
            sleep(wait)
    raise RuntimeError("unreachable")


def _retry_after(response):
    try:
        return float(response.headers.get("retry-after", ""))
    except ValueError:
        return None


def require_rationale(result):
    rationale = result.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise InvalidScoreError("missing rationale")
    return rationale.strip()


def load_scores(path):
    """Load cached scores as {slug: entry}. Missing file → empty."""
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return {entry["slug"]: entry for entry in json.load(f)}


def save_scores(path, scores):
    """Write scores atomically, so an interrupted run can't corrupt the file."""
    tmp = f"{path}.tmp"
    with open(tmp, "w") as f:
        json.dump(list(scores.values()), f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def run(
    occupations,
    *,
    output_file,
    model,
    system_prompt,
    build_prompt,
    to_entry,
    needs_scoring=None,
    force=False,
    delay=0.5,
    client=None,
    call=call_llm,
    sleep=time.sleep,
    now=None,
):
    """Score each occupation that needs it and save after each one.

    Args:
        occupations: The occupations to consider (already sliced by --start/--end).
        output_file: JSON cache, e.g. scores.json. Entries outside `occupations` are kept.
        build_prompt: occ -> user prompt text.
        to_entry: (occ, parsed answer) -> dict of fields to store. Raise InvalidScoreError
            if the answer is unusable.
        needs_scoring: (occ, cached entry) -> bool, for extra staleness rules.
        force: Re-score every occupation in `occupations` even if cached.

    Returns:
        (scores dict, list of slugs that failed).
    """
    scores = load_scores(output_file)
    now = now or (lambda: datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat())
    own_client = client is None
    client = client or httpx.Client()
    errors = []

    todo = [
        occ
        for occ in occupations
        if force or occ["slug"] not in scores or (needs_scoring is not None and needs_scoring(occ, scores[occ["slug"]]))
    ]
    print(f"Scoring {len(todo)} of {len(occupations)} occupations with {model} ({len(scores)} cached)")

    try:
        for i, occ in enumerate(todo):
            slug = occ["slug"]
            print(f"  [{i + 1}/{len(todo)}] {occ['title']}...", end=" ", flush=True)
            entry = None
            for attempt in range(2):
                try:
                    result = call(client, system_prompt, build_prompt(occ), model)
                    entry = to_entry(occ, result)
                    break
                except InvalidScoreError as e:
                    if attempt == 0:
                        print(f"(invalid answer: {e}; asking again)", end=" ", flush=True)
                        continue
                    print(f"ERROR: {e}")
                except Exception as e:  # noqa: BLE001 - report and carry on with the next occupation
                    print(f"ERROR: {e}")
                    break
            if entry is None:
                errors.append(slug)
            else:
                scores[slug] = {"slug": slug, "title": occ["title"], **entry, "model": model, "scored_at": now()}
                print("ok")
                save_scores(output_file, scores)
            if i < len(todo) - 1:
                sleep(delay)
    finally:
        if own_client:
            client.close()

    print(f"\nDone. {len(scores)} occupations in {output_file}, {len(errors)} errors.")
    if errors:
        print(f"Failed: {', '.join(errors)}")
    return scores, errors
