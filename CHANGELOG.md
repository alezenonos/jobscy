# Changelog

All notable changes to JobsCY are listed here. The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **"Distinctly Cypriot" layer.** Colours each occupation by how much more (or less) common it is in Cyprus than across the EU27: its share of Cyprus jobs divided by its share of EU jobs (a location quotient, Eurostat LFS `lfsa_egai2d`). Cleaners and helpers are 2.5× as common, business and administration associate professionals 1.6×.
- **"Pay vs EU" layer.** Cyprus mean annual pay per major group as a % of the EU27 average, in euros and adjusted for prices (PPS), and compared with Greece, from the same SES 2022 table (`earn_ses22_28`).
- `refresh_data.py eu-compare` fetches both into `data/cache/eu_compare.json`; the yearly refresh workflow runs it.

## [1.2.0] — 2026-11-26

### Fixed
- **Scoring scripts no longer lose saved scores.** `--force` with `--start`/`--end` used to shrink `scores.json` to that range. Scoring now goes through `llm_scoring.py`, which validates each answer, retries rate limits and server errors, records the model and date, and exits non-zero when anything failed.
- Education legend and labels matched the wrong levels ("No degree → Doctoral", "HS/BS/PhD"), and three education tiers shared one colour.
- **Pay was understated.** The earnings fetch did not recognise Cyprus's headline SES aggregate (`B-S_X_O`) and fell back to an unweighted average of sector figures. It now uses the official aggregate: Professionals go from €36.9K to €41.8K, Managers from €65.8K to €73.6K.
- `prompt.md` no longer claims data from HRDA, and its totals are regenerated on the corrected employment figures (was 572K jobs).
- Docs named `earn_ses_pub1s` as the earnings dataset; it is `earn_ses_hourly` (plus `earn_ses22_28`).

### Changed
- Removed unused `playwright` and `beautifulsoup4` dependencies; Dependabot now updates `uv.lock`; CI checks the lock file is in sync. The hard-coded coverage badge was removed and the CI coverage floor raised from 45% to 60%.
- **Employment refreshed to LFS 2025** (499.0k across the 39 groups, was 480.2k for 2024).
- **Average pay is SES mean annual earnings** (`earn_ses22_28`), which includes the 13th salary and bonuses, instead of hourly × 2,080.
- CSV pay columns renamed to `mean_pay_annual_eur` and `mean_pay_hourly_eur`, since they were never medians.

### Added
- **Keyboard access and a data table.** The treemap can be explored with Tab and the arrow keys, screen readers hear each tile, and a sortable table under the treemap lists all 39 occupations.
- **Tap on phones and tablets** shows a tile's details. The page no longer scrolls sideways on phones, the header shows the data years, and the methods and caveats sit behind one "About the data" toggle so the treemap is near the top.
- **Yearly data refresh.** A workflow scheduled for 1 June each year fetches the latest Eurostat data, rebuilds the site data and opens a pull request listing what changed and which growth-outlook scores need re-scoring.
- **Data integrity checks in CI** (`tests/test_data_integrity.py`): the CSV and site data rebuild from the cache, employment adds up to the Eurostat totals, values are in range, and the data is at most two years old.
- **2025 pay estimate.** SES 2022 pay is carried forward to 2025 with Cyprus's wage growth (Eurostat labour cost index, +15.5%) and labelled as an estimate; the 2022 survey figure stays in the tooltip. Managers now show €84.9K, Professionals €48.2K.
- **Pay by sector.** The pay tooltip lists the best- and worst-paying sectors for each major group (SES 2022 `earn_ses22_49`, cells under 500 employees dropped).
- **Job Openings layer** from HRDA's *Forecasts of Employment Needs in Cyprus 2022-2032*: yearly openings, split into new jobs and replacement of leavers, per ISCO 2-digit group.
- **Cedefop Skills Forecast 2022-2035** job openings and employment growth in the tooltip.
- The growth outlook tooltip shows HRDA's and Cedefop's official employment forecasts next to the LLM estimate.
- New `forecasts.py` module and cached inputs in `data/cache/` (`wage_index.json`, `earnings_by_sector.json`, `hrda_2022_2032.csv`, `cedefop_2035.json`).
- **Pay distribution.** Median, P10 and P90 earnings per major group (`earn_ses_hourly`), shown in the tooltip as the range the middle 80% earn, and in `site/data.json` as `pay_median`, `pay_p10`, `pay_p90`.

## [1.1.0] — 2026-11

### Fixed
- **Employment no longer double-counted.** Eurostat suppresses Cyprus 2-digit values for OC62, OC82 and OC95, and the pipeline previously gave each of them the whole 1-digit group total. Total employment drops from an overstated 572.1k to **480.2k**. Suppressed groups are now estimated as the residual of their major group and flagged as estimates in the CSV, `site/data.json` and the tooltip.
- **Pay is labelled correctly.** The SES figures are mean gross earnings, so the site now says "Average pay" instead of "Median pay".

### Changed
- **Growth Outlook is grounded in Eurostat history.** `make_cagr.py` computes each group's historical employment CAGR from the multi-year LFS series (`cagr.json`), and `score_outlook.py` includes it in the prompt. The tooltip shows the historical CAGR and period. The outlook is labelled as an LLM estimate and no longer implies it comes from HRDA forecasts.
- Cached outlook scores made without the current historical data are re-scored automatically.
- Default scoring model is now `openai/gpt-6-luna` (was `google/gemini-3-flash-preview`).
- **All scores regenerated** with `openai/gpt-6-luna` on the corrected data (#25). AI exposure: 20 of 39 scores changed, average 5.3 → 4.7. Growth Outlook: 36 of 39 groups now use their historical Eurostat growth, average +1.2% → +2.3%.

### Removed
- 342 unused US occupation entries left over in `scores.json` from the original project.

### Added
- `LICENSE` (MIT) and this changelog.

## [1.0.0] — 2026-03-28

First public release: interactive treemap of 39 ISCO-08 occupation groups in Cyprus, Eurostat employment and earnings pipeline, LLM-scored AI exposure and growth outlook, CI on GitHub Actions and deployment on Vercel.

[1.2.0]: https://github.com/alezenonos/jobscy/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/alezenonos/jobscy/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/alezenonos/jobscy/releases/tag/v1.0.0
