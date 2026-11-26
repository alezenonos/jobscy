# Handover Document — JobsCY

> **Last updated:** 2026-11-26 (keyboard access and data table, data integrity CI, safe LLM scoring, yearly data refresh)
> **Default branch:** `master`
> **Repo:** https://github.com/alezenonos/jobscy
> **Status:** Functional end-to-end, version 1.1.0 plus the changes in CHANGELOG.md "Unreleased". The sections under "Completed work" are the original build history.

---

## Project overview

JobsCY adapts [karpathy/jobs](https://github.com/karpathy/jobs) (a US BLS occupational treemap) for the **Cyprus labour market** using EU/Cyprus data sources. The result is an interactive treemap of Cyprus occupations sized by employment and coloured by growth outlook, average pay (EUR), job openings, education level, or AI exposure score.

## Architecture

```
  ISCO-08 data ──► generate_cy_occupations.py ──► occupations_cy.json
  Eurostat API ──► make_cy_csv.py ──► occupations_cy.csv ─────────────┐
  Eurostat API ──► make_cagr.py ──► cagr.json                          │
  LLM (OpenRouter) ──► score.py ──────────► scores.json ───────────────┤
  LLM (OpenRouter) + cagr.json ──► score_outlook.py ──► outlook_scores.json
                                                                       │
  data/cache (wage index, sector pay, HRDA, Cedefop) ──► forecasts.py ─┤
                                                                       ▼
                                   build_site_data.py ──► site/data.json ──► site/index.html

Yearly refresh on 1 June (.github/workflows/refresh-data.yml):
  make_cy_csv.py + make_cagr.py + refresh_data.py wage-index ──► build_site_data.py ──► pull request

Utilities:
  make_prompt.py ──► prompt.md (single-file LLM analysis document)
```

### Key modules

| Module | Purpose | Status |
|--------|---------|--------|
| `eurostat.py` | Fetch Cyprus employment/wage data from Eurostat REST API | **Done (PR 2)** |
| `generate_cy_occupations.py` | Generate `occupations_cy.json` from ISCO-08 classification | **Done (PR 3)** |
| `make_cy_csv.py` | Build `occupations_cy.csv` from Eurostat data (EUR, ISCO) | **Done (PR 3)** |
| `build_site_data.py` | Merge CSV + scores → `site/data.json` | **Done (PR 3)** |
| `forecasts.py` | 2025 pay estimate, pay by sector, HRDA + Cedefop forecasts for the site | **Done (PR 27)** |
| `score.py` | LLM-based AI exposure scoring via OpenRouter | **Done (PR 4)** |
| `make_cagr.py` | Historical employment CAGR per ISCO code → `cagr.json` | Done |
| `score_outlook.py` | LLM 10-year growth outlook, grounded with `cagr.json` | Done |
| `llm_scoring.py` | Shared scoring loop: keeps cached scores, validates, retries, records model/date | Done |
| `refresh_data.py` | Wage index fetch and change report for the yearly refresh | Done |
| `tests/test_data_integrity.py` | Checks on the committed data (rebuilds, totals, ranges, freshness) | Done |
| `make_prompt.py` | Generate single-file LLM prompt | **Done (PR 6)** |
| `site/index.html` | Interactive treemap visualisation (EUR, ISCO-08) | **Done (PR 5)** |
## Data sources (Cyprus/EU)

| Source | What it provides | Access method | Priority |
|--------|-----------------|---------------|----------|
| **HRDA/AnAD** | Forecasts 2022-2032 per ISCO 2-digit group (used) and ~309 detailed occupations (not yet) | [PDF](https://www.anad.org.cy/wps/wcm/connect/hrda/b6fbcbf8-14b0-4ee2-817b-ab97496d90a5/Provlepseis+2022-2032.pdf?MOD=AJPERES), chapter 6, transcribed to `data/cache/hrda_2022_2032.csv` | Primary |
| **Eurostat API** | Employment by ISCO-08 2-digit, wages by ISCO-08 1-digit, `geo=CY` | REST API (CSV/JSON) | Primary |
| **EURES** | Shortage/surplus occupations, vacancy stats by ESCO | Web dashboard | Secondary |
| **CEDEFOP** | Job openings and growth 2022-2035 per ISCO 2-digit group (used) | Skills Intelligence tool, CSV export, saved to `data/cache/cedefop_2035.json` | Secondary |
| **CYSTAT** | Aggregate employment, unemployment, labour costs | CYSTAT-DB / data.gov.cy | Supporting |

### Key Eurostat datasets

| Dataset code | Content | Granularity |
|---|---|---|
| `LFSA_EGAI2D` | Employment by occupation | ISCO-08 2-digit, by country, sex, age |
| `lfsa_eisn2` | Employment by occupation × economic activity | ISCO 1-digit × NACE |
| `earn_ses_hourly` | Mean, median and decile gross hourly earnings (SES) | ISCO 1-digit × NACE aggregates, by country |
| `earn_ses22_28` | Mean gross annual earnings (SES 2022) | ISCO 1-digit, by country, sex, age |
| `earn_ses22_49` / `earn_ses22_54` | Mean annual earnings / employees by occupation × sector (SES 2022) | ISCO 1-digit × NACE section → `data/cache/earnings_by_sector.json` |
| `lc_lci_r2_a` | Labour cost index, wages and salaries (D11), 2020=100 | NACE aggregates, yearly → `data/cache/wage_index.json` |

### Eurostat API format

```
# CSV endpoint (SDMX 2.1)
https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{DATASET}?format=SDMX-CSV&geo=CY

# JSON-stat endpoint
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{DATASET}?geo=CY
```

## Completed work

### PR 1: CI/CD + Testing + Cyprus Rebrand ✅
- GitHub Actions CI (`.github/workflows/ci.yml`) — lint (ruff) + test (pytest)
- 37 unit tests across 5 test files
- Ruff linter + formatter configured in `pyproject.toml`
- README rewritten for Cyprus/EU context
- All script docstrings updated
- Currency changed from USD → EUR in `make_prompt.py`
- Pay bands changed from US ranges to EU ranges
- `.gitignore` updated

### PR 2: Eurostat API Client + HANDOVER.md ✅
- `eurostat.py` — full client module for Eurostat SDMX 2.1 REST API
  - `fetch_sdmx_csv()` — generic CSV fetcher for any Eurostat dataset
  - `fetch_json_stat()` — JSON-stat endpoint fetcher
  - `fetch_employment_by_occupation()` — ISCO-08 2-digit employment for Cyprus
  - `fetch_earnings_by_occupation()` — ISCO-08 1-digit earnings (SES) for Cyprus
  - `build_occupation_summary()` — merges employment + earnings into unified view
  - Complete ISCO-08 reference data (10 major groups, 39 sub-major groups)
  - CLI interface with CSV/JSON output options
- 21 new tests (`tests/test_eurostat.py`) using mocked HTTP responses
- CI workflow fixed to target `master` branch (was incorrectly set to `main`)
- `HANDOVER.md` created as living project status document

### PR 3: Cyprus Data Pipeline ✅
- `generate_cy_occupations.py` — generates `occupations_cy.json` from ISCO-08 classification
  - 39 sub-major group occupations with ISCO codes, categories, and slugs
  - Optional inclusion of 10 major groups for aggregated views
  - ISCO-based category system (managers, professionals, technicians, etc.)
- `make_cy_csv.py` — builds `occupations_cy.csv` from Eurostat data
  - Merges ISCO-08 occupation list with employment counts and EUR earnings
  - Supports both live API fetching and cached JSON data
  - Education level mapping by ISCO major group (ISCED-aligned)
  - Cache save/load for offline development
- `build_site_data.py` — merges Cyprus CSV + scores into site/data.json
  - `merge_cyprus()` function: ISCO codes, EUR pay, employment in thousands→absolute
  - CLI args for explicit CSV/scores/output paths
- 30 new tests across 3 test files (88 total)

### PR 4: Scoring Adaptation ✅
- `score.py` — fully adapted for Cyprus/EU labour market
  - New `SYSTEM_PROMPT` with Cyprus/EU context (tourism, shipping, financial services, EU Digital Decade, public sector)
  - ISCO-08 occupation examples as scoring anchors (replacing BLS examples)
  - Extracted `parse_llm_response()` — robust JSON parsing with markdown fence stripping
  - New `build_isco_prompt()` — constructs scoring prompts from ISCO-08 metadata when no markdown exists
  - New `detect_occupation_format()` — auto-detects BLS vs Cyprus occupation lists
  - Updated `main()` — auto-detects `occupations_cy.json` vs `occupations.json`
- 12 new tests in `tests/test_score.py` (97 total)

### PR 5: Visualisation + Site Update ✅
- `site/index.html` — fully adapted for Cyprus/EU
  - Title, header, descriptions updated (removed all US/BLS/karpathy references)
  - GitHub links point to `alezenonos/jobscy`
  - Currency: USD ($) → EUR (€) throughout (formatPay, pay bands, wages, legend)
  - Pay scales: $25K–$250K → €10K–€80K (appropriate for Cyprus wage levels)
  - Pay bands: US ranges → EU/Cyprus ranges (<€20K through €75K+)
  - Pay histogram buckets adjusted for Cyprus wage distribution
  - Education levels: BLS (8 US levels) → ISCED-aligned (5 EU levels matching `make_cy_csv.py`)
  - Total jobs/wages: formatNumber() and billions (€B) instead of hardcoded M/trillions
  - Scoring prompt: updated to Cyprus/EU ISCO-08 version
  - "BLS Outlook" → "Growth Outlook", "Jobs (2024)" → "Employment"

### PR 6: Documentation Final Pass ✅
- `README.md` — comprehensive rewrite with architecture diagram, accurate file list, Cyprus pipeline commands
- `CONTRIBUTING.md` — new file: development setup, branch conventions, code quality, testing, PR process
- `make_prompt.py` — adapted for Cyprus: ISCED education groups, ISCO-08 anchors
- `HANDOVER.md` — final update with troubleshooting section, all PRs marked complete
- New tests for `make_prompt.py` (load_records_cyprus)

### PR 7: CI/CD Hardening + Vercel Deployment ✅
- `vercel.json` — added security headers:
  - HSTS (`Strict-Transport-Security`) — forces HTTPS at browser level
  - CSP (`Content-Security-Policy`) — restricts script/style/image sources to self only
  - `Permissions-Policy` — denies unused browser APIs (camera, mic, geolocation, payment)
  - `X-DNS-Prefetch-Control` — disables DNS prefetching for privacy
- `site/index.html` — removed hardcoded Eurostat click handler (was opening same static URL for all boxes)
- Documentation updates:
  - `README.md` — added author attribution, deployment section, updated test count
  - `CONTRIBUTING.md` — added British English convention
  - `HANDOVER.md` — updated with PR 7 details
  - `prompt.md` — fixed American English (optimize → optimise, labor → labour)

## Future enhancements

These are optional improvements beyond the initial 6-PR scope:

- **HRDA detail:** The 2-digit forecasts are integrated; the ~309 detailed occupations could add finer granularity
- **Growth outlook:** Still an LLM estimate grounded with Eurostat historical CAGR (`make_cagr.py`). HRDA and Cedefop forecasts are now shown next to it and could be fed into the scoring prompt on the next re-score
- **Refreshing the forecast caches:** employment, earnings, employment history and `wage_index.json` are refreshed yearly (1 June) by the workflow. The sector pay file only changes with a new SES wave (expected ~2028). HRDA and Cedefop values were transcribed by hand and need updating when new editions come out
- **EURES shortage data:** Add shortage/surplus indicators from EURES vacancy statistics
- **3-digit ISCO:** Expand from 39 sub-major groups to ~130 minor groups if Eurostat provides sufficient Cyprus data
- **Multilingual:** Greek language support for occupation titles (ISCO-08 has official Greek labels)

## Troubleshooting

### Eurostat API returns 403
The Eurostat API (`ec.europa.eu`) may be blocked in sandboxed environments (e.g. egress proxy returns `403 host_not_allowed`). Use the cache mechanism in `make_cy_csv.py`:
```bash
# Save cached data (from an environment with API access)
uv run python make_cy_csv.py --save-cache data/cache

# Load from cache (in sandboxed environments)
uv run python make_cy_csv.py --cached data/cache
```

GitHub Actions runners can reach Eurostat, so the refresh workflow (Actions tab → "Refresh data" → "Run workflow") is the easiest way to fetch new data. It needs "Allow GitHub Actions to create and approve pull requests" enabled under Settings → Actions → General.

### CI fails on push
- Ensure branch name starts with `claude/` or is `master`
- Run locally first: `uv run ruff check . && uv run ruff format --check . && uv run pytest -v`

### OpenRouter API errors
- Ensure `OPENROUTER_API_KEY` is set in `.env`
- `score.py` and `score_outlook.py` save after each occupation, so they can be resumed after interruption. Rate limits and server errors are retried with backoff
- Use `--start` and `--end` flags to test on a subset first. `--force` re-scores only that range and keeps the rest
- The scripts exit with status 1 when any occupation failed; re-run to retry just those

### Tests fail due to ISCO-08 count mismatch
The `ISCO08_2DIGIT` dict in `eurostat.py` has 39 entries. Tests use `len(ISCO08_2DIGIT)` dynamically to avoid hardcoded count mismatches.

## Development setup

```bash
uv sync --extra dev          # install all deps including pytest/ruff
uv run pytest -v             # run tests
uv run ruff check .          # lint
uv run ruff format .         # format
```

Requires `.env` with `OPENROUTER_API_KEY` for LLM scoring only.

## Conventions

- **Default branch:** `master` (not `main`)
- **Currency:** EUR (€), never USD
- **Classification:** ISCO-08 for occupations, NACE Rev. 2 for sectors, ISCED 2011 for education
- **Data period:** Eurostat LFS latest available year (employment), SES 2022 (earnings, carried forward with the wage index), HRDA 2022-2032 and Cedefop 2022-2035 forecasts
- **Python:** 3.10+, formatted with ruff, tested with pytest
- **CI:** GitHub Actions on push to `master` and `claude/*` branches, and on PRs to `master`
- **Tests:** 180+ tests, no external API calls. Unit tests are mocked; `tests/test_data_integrity.py` checks the committed data files
