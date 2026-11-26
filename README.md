# JobsCY — Cyprus Job Market Visualiser

[![CI](https://github.com/alezenonos/jobscy/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/alezenonos/jobscy/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Licence MIT](https://img.shields.io/badge/licence-MIT-green.svg)](LICENSE)
[![Deployed on Vercel](https://img.shields.io/badge/deployed-Vercel-black.svg)](https://vercel.com)

An interactive treemap visualisation of the Cyprus labour market, with AI exposure scoring for occupations. Built on [Eurostat](https://ec.europa.eu/eurostat) employment and earnings data for Cyprus, with LLM-estimated growth outlook and AI exposure.

**Created and maintained by [Alexandros Zenonos](https://github.com/alezenonos)**, adapted from [karpathy/jobs](https://github.com/karpathy/jobs) for the Cyprus labour market using EU data sources and international classifications (ISCO-08, NACE, ISCED).

## What's here

An interactive treemap of **39 ISCO-08 occupation groups** covering the Cyprus labour market. Each rectangle's **area** is proportional to employment and **colour** shows the selected metric — toggle between growth outlook, average pay (EUR, mean gross earnings), job openings, education level, and AI exposure. Tiles can be explored with a mouse, by tapping on a phone, or with the keyboard (Tab to the chart, then the arrow keys), and the same data is in a sortable table under the treemap.

Data is sourced from the Eurostat SDMX REST API (employment by ISCO-08 2-digit, earnings by ISCO-08 1-digit, filtered to `geo=CY`). Growth outlook and AI exposure are **LLM estimates** (see below), not official forecasts. Official job-openings forecasts from HRDA (2022-2032) and Cedefop (2022-2035) are shown alongside them and drive the Job Openings layer.

## Data sources

| Source | Dataset | What it provides | Link |
|--------|---------|-----------------|------|
| **Eurostat** | [`LFSA_EGAI2D`](https://ec.europa.eu/eurostat/databrowser/view/lfsa_egai2d/default/table?lang=en) | Employment by ISCO-08 2-digit, filtered to Cyprus (2025) | [Eurostat API docs](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction) |
| **Eurostat** | [`earn_ses_hourly`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses_hourly/default/table?lang=en) | Mean, median, P10 and P90 gross hourly earnings by ISCO-08 1-digit, Cyprus (SES 2022) | [Dataset explorer](https://ec.europa.eu/eurostat/databrowser/view/earn_ses_hourly/default/table?lang=en) |
| **Eurostat** | [`LFSA_EGAI2D`](https://ec.europa.eu/eurostat/databrowser/view/lfsa_egai2d/default/table?lang=en) (multi-year) | Historical employment growth (CAGR) per ISCO-08 2-digit, 2011-2025, used to ground the growth outlook | — |
| **Eurostat** | [`earn_ses22_28`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses22_28/default/table?lang=en) | Mean gross **annual** earnings by ISCO-08 1-digit (includes 13th salary and bonuses), Cyprus (SES 2022) | — |
| **Eurostat** | [`earn_ses22_49`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses22_49/default/table?lang=en), [`earn_ses22_54`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses22_54/default/table?lang=en) | Mean annual earnings and employee counts by ISCO-08 1-digit × NACE section (pay by sector) | `data/cache/earnings_by_sector.json` |
| **Eurostat** | [`lc_lci_r2_a`](https://ec.europa.eu/eurostat/databrowser/view/lc_lci_r2_a/default/table?lang=en) | Cyprus labour cost index, wages and salaries (business economy), used to carry 2022 pay forward to 2025 | `data/cache/wage_index.json` |
| **HRDA** | [Forecasts of Employment Needs in Cyprus 2022-2032](https://www.anad.org.cy/wps/wcm/connect/hrda/b6fbcbf8-14b0-4ee2-817b-ab97496d90a5/Provlepseis+2022-2032.pdf?MOD=AJPERES) (chapter 6) | Employment 2022/2032 and yearly expansion, replacement and total demand per ISCO-08 2-digit group | `data/cache/hrda_2022_2032.csv` |
| **Cedefop** | [Skills Forecast 2025](https://www.cedefop.europa.eu/en/tools/skills-intelligence) | Job openings and employment growth 2022-2035 per ISCO-08 2-digit group, Cyprus | `data/cache/cedefop_2035.json` |

**Not yet used** (candidates for future integration):

| Source | What it would provide | Link |
|--------|-----------------|------|
| **HRDA/AnAD** | Forecasts for ~309 detailed occupations (finer than the 2-digit groups used here) | [anad.org.cy](https://www.anad.org.cy) |
| **EURES** | Shortage/surplus occupations, vacancy statistics by ESCO occupation | [eures.europa.eu](https://eures.europa.eu) |
| **CYSTAT** | Aggregate employment, unemployment, labour costs | [cystat.gov.cy](https://www.cystat.gov.cy) |

### Employment methodology

Employment comes from the Eurostat LFS at ISCO 2-digit level. Eurostat suppresses some Cyprus 2-digit values as unreliable (currently OC62, OC82 and OC95). For those, employment is **estimated as the residual** of the 1-digit major group total minus the known sub-groups, and flagged as an estimate in the CSV (`employment_estimated`), `site/data.json` (`jobs_estimated`) and the tooltip.

### Growth outlook methodology

The 10-year growth outlook is produced by `score_outlook.py`, which asks an LLM to project employment change per occupation group. To ground the estimate, `make_cagr.py` computes each group's historical employment CAGR from the multi-year Eurostat LFS series and writes `cagr.json`, which `score_outlook.py` reads by default and includes in the prompt. The historical CAGR and period are shown in the tooltip when used. Note that the LFS has a break in series in 2021, so historical growth across that year should be read with care.

### Job openings methodology

`forecasts.py` adds the official forecasts to `site/data.json`:

- **HRDA 2022-2032** (`hrda_*` fields): employment in 2022 and 2032, and average yearly openings split into expansion demand (new jobs) and replacement demand (people retiring or leaving). Transcribed by hand from chapter 6 of the HRDA report into `data/cache/hrda_2022_2032.csv`. The Job Openings layer colours each tile by yearly openings as a share of 2022 employment.
- **Cedefop 2022-2035** (`cedefop_*` fields): total job openings and employment growth from the Skills Forecast for Cyprus, saved in `data/cache/cedefop_2035.json`. Cedefop does not publish assemblers (OC82) for Cyprus.

HRDA's 2022 employment can differ from the Eurostat LFS 2025 figure used for tile sizes, because the base year and model differ. Both forecasts are shown next to the LLM growth outlook in its tooltip for comparison; the outlook scores themselves were not re-run.

### Earnings methodology

Salary figures are derived from the Eurostat **Structure of Earnings Survey** (SES), the official EU-wide enterprise survey on wages:

- **Granularity:** SES provides Cyprus earnings at **ISCO 1-digit** (major group) level only — all 2-digit occupations under the same group share the same figure (e.g. all Professionals = €41,771/year)
- **Average pay:** mean gross annual earnings ([`earn_ses22_28`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses22_28/default/table?lang=en)), which include the 13th salary and annual bonuses. If unavailable, the pipeline falls back to hourly mean × 2,080 hours.
- **Pay range:** median, 10th percentile (P10) and 90th percentile (P90) of gross hourly earnings ([`earn_ses_hourly`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses_hourly/default/table?lang=en), `MED_E_EUR`, `D1_E_EUR`, `D9_E_EUR`), annualised with the same annual/hourly ratio as the group's mean. This is an approximation; it shows, for example, that the top 10% of managers earn above roughly €124K.
- **Sector aggregate:** `B-S_X_O` (whole economy excluding public administration). Earlier versions accidentally averaged the per-sector figures without weights, which understated pay (e.g. Professionals €36.9K instead of €41.8K).
- **Coverage:** Enterprises with **10+ employees** — excludes self-employed, micro-firms, the public administration sector and the informal economy
- **Survey year:** 2022 (SES is published every 4 years; the 2026 wave is expected around 2028)
- **2025 estimate:** the site shows pay carried forward from 2022 to the latest year of the Eurostat labour cost index for wages and salaries (`lc_lci_r2_a`, B-S, 2022 = 108.0, 2025 = 124.7, so +15.5%). The uplift is the same for every group, so it moves levels, not the ranking. The original survey figure stays in `site/data.json` as `pay_survey` and in the tooltip. `occupations_cy.csv` keeps the survey values.
- **Pay by sector:** mean annual earnings per major group in each NACE section (`earn_ses22_49`), uplifted the same way; sector cells with fewer than 500 employees are dropped as too noisy.

These are **statistical averages, not market salaries.** Actual compensation for specific roles in Cyprus may differ significantly due to sector, firm size, seniority, and private-sector premiums not captured by SES.

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
```

The data is refreshed automatically: `.github/workflows/refresh-data.yml` runs on the 1st of each month (or by hand from the Actions tab), fetches the latest Eurostat data, rebuilds `site/data.json` and opens a pull request when anything changed. It never re-runs the LLM; the pull request lists any growth-outlook scores that should be re-scored because the historical growth changed.

## LLM-powered colouring

The repo includes a pipeline for scoring occupations using LLMs via OpenRouter. The default model is `openai/gpt-6-luna` (override with `--model`). You write a prompt, the LLM scores each occupation, and the treemap colours accordingly. The "Digital AI Exposure" layer estimates how much current AI will reshape each occupation within the Cyprus/EU labour market context (considering tourism, shipping, financial services, EU Digital Decade targets).

Fork `score.py` to write your own scoring criteria — e.g. green economy relevance, remote work potential, EU Digital Decade alignment.

**What "AI Exposure" is NOT:**
- It does **not** predict that a job will disappear
- It does **not** account for demand elasticity, regulatory barriers, or social preferences
- The scores are LLM estimates, not rigorous predictions

## Key files

| File | Description |
|------|-------------|
| `eurostat.py` | Eurostat SDMX 2.1 REST API client (employment + earnings data) |
| `generate_cy_occupations.py` | Generate `occupations_cy.json` from ISCO-08 classification |
| `make_cy_csv.py` | Build `occupations_cy.csv` from Eurostat data (EUR, ISCO-08) |
| `score.py` | LLM-based AI exposure scoring via OpenRouter (ISCO-08 / Cyprus context) |
| `llm_scoring.py` | Shared scoring loop: keeps cached scores, validates answers, retries rate limits, records model and date |
| `make_cagr.py` | Historical employment CAGR per ISCO-08 code from Eurostat → `cagr.json` |
| `score_outlook.py` | LLM-based 10-year growth outlook, grounded with `cagr.json` |
| `build_site_data.py` | Merge CSV + scores → `site/data.json` |
| `forecasts.py` | Add 2025 pay estimate, pay by sector, HRDA and Cedefop forecasts to the site data |
| `make_prompt.py` | Generate single-file LLM prompt from all data |
| `refresh_data.py` | Wage index fetch and change report used by the monthly refresh workflow |
| `site/index.html` | Interactive treemap visualisation (EUR, ISCO-08, Cyprus) |
| `occupations_cy.json` | Master list of 39 ISCO-08 occupation groups |
| `occupations_cy.csv` | Summary stats: pay (EUR), employment, education, ISCO codes |
| `scores.json` | AI exposure scores (0-10) with rationales |
| `cagr.json` | Historical employment CAGR per ISCO-08 code (generated by `make_cagr.py`) |
| `outlook_scores.json` | 10-year growth outlook estimates (%) with rationales |

## Setup

```bash
uv sync                  # install dependencies
uv sync --extra dev      # includes pytest, ruff for development
```

Requires an OpenRouter API key in `.env` (for LLM scoring only):
```
OPENROUTER_API_KEY=your_key_here
```

## Usage

```bash
# Generate occupation list from ISCO-08
uv run python generate_cy_occupations.py

# Fetch Eurostat data and build CSV
uv run python make_cy_csv.py

# Score AI exposure (uses OpenRouter API). Cached scores are kept; --force with
# --start/--end re-scores only that range. Exits non-zero if any occupation failed.
uv run python score.py

# Build historical growth (Eurostat) and score growth outlook (uses OpenRouter API)
uv run python make_cagr.py --save-cache data/cache
uv run python score_outlook.py   # re-scores any entry made without the current historical data

# Build website data
uv run python build_site_data.py

# Generate LLM analysis prompt
uv run python make_prompt.py

# Serve the site locally
cd site && python -m http.server 8000
```

## Development

```bash
uv run pytest -v           # run tests
uv run ruff check .        # lint
uv run ruff format .       # auto-format
```

CI runs automatically on push via GitHub Actions: lint, tests on Python 3.10-3.12, a `uv.lock` check, and integrity checks on the published data (`tests/test_data_integrity.py`: the CSV and `site/data.json` rebuild from `data/cache`, employment adds up to the Eurostat totals, values are in range, and the employment data is at most two years old). See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Deployment

The site is deployed as a static site on [Vercel](https://vercel.com). Configuration is in `vercel.json`:

- **Output directory:** `site/`
- **No build step** — the site is pre-built and committed to the repository
- **Security headers:** HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- **Caching:** `data.json` is cached for 1 hour with 24-hour stale-while-revalidate

## Currency and classifications

- **Currency:** EUR (€) — all monetary values
- **Occupations:** ISCO-08 (International Standard Classification of Occupations)
- **Sectors:** NACE Rev. 2 (Statistical Classification of Economic Activities)
- **Education:** ISCED 2011 (International Standard Classification of Education)
- **Data period:** Eurostat LFS latest available year (employment), SES 2022 (earnings)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) and the [Releases](https://github.com/alezenonos/jobscy/releases) page.

## Licence

Released under the [MIT Licence](LICENSE).

## Acknowledgements

This project adapts the visualisation approach from [karpathy/jobs](https://github.com/karpathy/jobs) (a US BLS occupational treemap) for the Cyprus labour market using EU data sources and international classifications.
