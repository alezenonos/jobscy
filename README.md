# JobsCY — Cyprus Job Market Visualiser

[![CI](https://github.com/alezenonos/jobscy/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/alezenonos/jobscy/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Coverage 46%](https://img.shields.io/badge/coverage-46%25-yellow.svg)](https://github.com/alezenonos/jobscy/actions)
[![Licence MIT](https://img.shields.io/badge/licence-MIT-green.svg)](#)
[![Deployed on Vercel](https://img.shields.io/badge/deployed-Vercel-black.svg)](https://vercel.com)

An interactive treemap visualisation of the Cyprus labour market, with AI exposure scoring for occupations. Built on [Eurostat](https://ec.europa.eu/eurostat) employment and earnings data for Cyprus, with LLM-estimated growth outlook and AI exposure.

**Created and maintained by [Alexandros Zenonos](https://github.com/alezenonos)**, adapted from [karpathy/jobs](https://github.com/karpathy/jobs) for the Cyprus labour market using EU data sources and international classifications (ISCO-08, NACE, ISCED).

## What's here

An interactive treemap of **39 ISCO-08 occupation groups** covering the Cyprus labour market. Each rectangle's **area** is proportional to employment and **colour** shows the selected metric — toggle between growth outlook, median pay (EUR), education level, and AI exposure.

Data is sourced from the Eurostat SDMX REST API (employment by ISCO-08 2-digit, earnings by ISCO-08 1-digit, filtered to `geo=CY`). Growth outlook and AI exposure are **LLM estimates** (see below), not official forecasts. HRDA occupational forecasts are not yet integrated.

## Data sources

| Source | Dataset | What it provides | Link |
|--------|---------|-----------------|------|
| **Eurostat** | [`LFSA_EGAI2D`](https://ec.europa.eu/eurostat/databrowser/view/lfsa_egai2d/default/table?lang=en) | Employment by ISCO-08 2-digit, filtered to Cyprus (2024) | [SDMX API docs](https://wikis.ec.europa.eu/display/EUROSTATHELP/Transition+to+the+new+dissemination+chain) |
| **Eurostat** | [`earn_ses_hourly`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses_hourly/default/table?lang=en) | Mean gross hourly earnings by ISCO-08 1-digit, Cyprus (SES 2022) | [Dataset explorer](https://ec.europa.eu/eurostat/databrowser/view/earn_ses_hourly/default/table?lang=en) |
| **Eurostat** | [`LFSA_EGAI2D`](https://ec.europa.eu/eurostat/databrowser/view/lfsa_egai2d/default/table?lang=en) (multi-year) | Historical employment growth (CAGR) per ISCO-08 2-digit, used to ground the growth outlook | — |

**Not yet used** (candidates for future integration):

| Source | What it would provide | Link |
|--------|-----------------|------|
| **HRDA/AnAD** | 309 occupation forecasts (2022-2032), expansion + replacement demand | [anad.org.cy](https://www.anad.org.cy) |
| **EURES** | Shortage/surplus occupations, vacancy statistics by ESCO occupation | [eures.europa.eu](https://eures.europa.eu) |
| **CEDEFOP** | Skills forecasts to 2035 by sector and occupation group | [cedefop.europa.eu](https://www.cedefop.europa.eu/en/tools/skills-intelligence) |
| **CYSTAT** | Aggregate employment, unemployment, labour costs | [cystat.gov.cy](https://www.cystat.gov.cy) |

### Employment methodology

Employment comes from the Eurostat LFS at ISCO 2-digit level. Eurostat suppresses some Cyprus 2-digit values as unreliable (currently OC62, OC82 and OC95). For those, employment is **estimated as the residual** of the 1-digit major group total minus the known sub-groups, and flagged as an estimate in the CSV (`employment_estimated`), `site/data.json` (`jobs_estimated`) and the tooltip.

### Growth outlook methodology

The 10-year growth outlook is produced by `score_outlook.py`, which asks an LLM to project employment change per occupation group. To ground the estimate, `make_cagr.py` computes each group's historical employment CAGR from the multi-year Eurostat LFS series and writes `cagr.json`, which `score_outlook.py` reads by default and includes in the prompt. The historical CAGR and period are shown in the tooltip when used. Note that the LFS has a break in series in 2021, so historical growth across that year should be read with care.

### Earnings methodology

Salary figures are derived from the Eurostat **Structure of Earnings Survey** ([`earn_ses_hourly`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses_hourly/default/table?lang=en)), the official EU-wide enterprise survey on wages:

- **Granularity:** SES provides earnings at **ISCO 1-digit** (major group) level only — all 2-digit occupations under the same group share the same figure (e.g. all Professionals = €36,878/year)
- **Conversion:** Hourly earnings × 2,080 hours (40 h/week × 52 weeks) = annual pay
- **Coverage:** Enterprises with **10+ employees** — excludes self-employed, micro-firms, and the informal economy
- **Survey year:** 2022 (SES is published every 4 years; next wave: 2026)
- **Metric:** Mean gross hourly earnings in EUR (`MEAN_E_EUR`)

These are **statistical averages, not market salaries.** Actual compensation for specific roles in Cyprus may differ significantly due to sector, firm size, seniority, and private-sector premiums not captured by SES.

## Architecture

```
Cyprus pipeline:
  ISCO-08 data ──► generate_cy_occupations.py ──► occupations_cy.json
  Eurostat API ──► make_cy_csv.py ─────────────► occupations_cy.csv
                                                        │
  LLM (OpenRouter) ──► score.py ──► scores.json ◄──────┘
                                         │
                     build_site_data.py ──┘──► site/data.json ──► site/index.html
```

## LLM-powered colouring

The repo includes a pipeline for scoring occupations using LLMs via OpenRouter. You write a prompt, the LLM scores each occupation, and the treemap colours accordingly. The "Digital AI Exposure" layer estimates how much current AI will reshape each occupation within the Cyprus/EU labour market context (considering tourism, shipping, financial services, EU Digital Decade targets).

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
| `make_cagr.py` | Historical employment CAGR per ISCO-08 code from Eurostat → `cagr.json` |
| `score_outlook.py` | LLM-based 10-year growth outlook, grounded with `cagr.json` |
| `build_site_data.py` | Merge CSV + scores → `site/data.json` |
| `make_prompt.py` | Generate single-file LLM prompt from all data |
| `site/index.html` | Interactive treemap visualisation (EUR, ISCO-08, Cyprus) |
| `occupations_cy.json` | Master list of 39 ISCO-08 occupation groups |
| `occupations_cy.csv` | Summary stats: pay (EUR), employment, education, ISCO codes |
| `scores.json` | AI exposure scores (0-10) with rationales |

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

# Score AI exposure (uses OpenRouter API)
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
uv run pytest -v           # run tests (110+ tests)
uv run ruff check .        # lint
uv run ruff format .       # auto-format
```

CI runs automatically on push via GitHub Actions (lint + test + site validation). See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

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

## Acknowledgements

This project adapts the visualisation approach from [karpathy/jobs](https://github.com/karpathy/jobs) (a US BLS occupational treemap) for the Cyprus labour market using EU data sources and international classifications.
