# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- **internal**: Extracted the inline comma-splitting logic (used in `contacts update --label-ids`, `people search --titles/--locations`, `tasks create --contact-ids`, and `notes create --contact-ids/--account-ids`) into a shared `apollo_cli.util.parse_comma_list` helper. Behavior is now consistent across every comma-list flag.

### Fixed

- **comma-list flags — forgiving on typos, loud on garbage.** All comma-separated CLI arguments now drop embedded empty segments, whitespace-only tokens, and leading/trailing commas — so `--contact-ids "a,,b"` sends `["a", "b"]` instead of `["a", "", "b"]` (which Apollo rejects with a 400). Empty (`""`) or whitespace-only input maps to "flag not provided", but input like `",,,"` — where the user typed *something* that collapses to nothing — now surfaces as a validation error (exit code 83, `"validation"`) via the CLI's central error handler, instead of a raw Python traceback or a silent flag-omit. Affects every command that takes a comma-list flag.

## [0.1.0] - 2026-02-26

### Added

- Initial CLI implementation with cyclopts framework
- Dual output mode: Markdown (default, agent/human-friendly) and JSON (`--json`)
- Global options: `--json`, `--api-key`, `--limit`, `--page`
- **contacts**: search, get, create, update, find-by-linkedin, stages
- **accounts**: search, get
- **deals**: search, get
- **pipelines**: list, get, stages
- **stages**: list (all stages across pipelines)
- **enrich**: org (free), person (1 credit)
- **people**: search (global database)
- **notes**: search, create
- **tasks**: search, create, complete
- **calls**: search, list (per contact)
- **emails**: search
- **news**: list (per account)
- **jobs**: list (per account)
- **usage**: API usage stats and rate limits
- **install**: Install AI agent skill files with `--skills` flag
- Centralized error handling with semantic exit codes (80-83)
- Rich markdown rendering for terminal output with `help_format="rich"`
- Pagination support with page/limit controls
- Comprehensive README.md with command reference and usage examples
- MIT License
- Full PyPI metadata in pyproject.toml
- CI/CD workflows (lint, typecheck, test, publish)
- Complete test suite with pytest and pytest-asyncio
- AI agent skill files (SKILL.md + workflow references)
- Dynamic help epilogue with all commands
- Dev dependencies (ruff, mypy, pytest)
- Tool configurations (ruff, mypy, pytest)
