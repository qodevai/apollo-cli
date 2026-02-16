# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
- Centralized error handling with semantic exit codes (80-83)
- Rich markdown rendering for terminal output
- Pagination support with page/limit controls
