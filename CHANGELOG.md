# Changelog

All notable changes to JobsCY are listed here. The project follows [Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-11

### Fixed
- **Employment no longer double-counted.** Eurostat suppresses Cyprus 2-digit values for OC62, OC82 and OC95, and the pipeline previously gave each of them the whole 1-digit group total. Total employment drops from an overstated 572.1k to **480.2k**. Suppressed groups are now estimated as the residual of their major group and flagged as estimates in the CSV, `site/data.json` and the tooltip.
- **Pay is labelled correctly.** The SES figures are mean gross earnings, so the site now says "Average pay" instead of "Median pay".

### Changed
- **Growth Outlook is grounded in Eurostat history.** `make_cagr.py` computes each group's historical employment CAGR from the multi-year LFS series (`cagr.json`), and `score_outlook.py` includes it in the prompt. The tooltip shows the historical CAGR and period. The outlook is labelled as an LLM estimate and no longer implies it comes from HRDA forecasts.
- Cached outlook scores made without the current historical data are re-scored automatically.
- Default scoring model is now `openai/gpt-6-luna` (was `google/gemini-3-flash-preview`).

### Added
- `LICENSE` (MIT) and this changelog.

## [1.0.0] — 2026-03-28

First public release: interactive treemap of 39 ISCO-08 occupation groups in Cyprus, Eurostat employment and earnings pipeline, LLM-scored AI exposure and growth outlook, CI on GitHub Actions and deployment on Vercel.

[1.1.0]: https://github.com/alezenonos/jobscy/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/alezenonos/jobscy/releases/tag/v1.0.0
