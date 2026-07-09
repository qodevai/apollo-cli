# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.3.0] - 2026-07-09

### Added

- `deals create` command — create a deal/opportunity from the CLI: `deals create --name "…" [--owner-id] [--account-id] [--amount] [--stage-id | --stage-name] [--closed-date]`. `--name` is the only required flag; `--stage-name` resolves to an ID via the stage list (same helper as `deals search`), and passing both `--stage-id` and `--stage-name` is a validation error. Requires a master Apollo API key (non-master keys get a 403).

### Changed

- Require `qodev-apollo-api>=0.4.0` (adds `create_deal`, and ships the fixed `update_opportunity_roles` payload so `deals set-role` now works, plus `search_accounts` filter validation).

## [1.2.1] - 2026-07-08

Follow-ups from code review of the v1.2.0 changes.

### Fixed

- **`deals set-role` no longer sends an explicit `null` role type.** Adding a contact without `--role-type` omitted the `opportunity_contact_role_type_id` key entirely instead of posting `null`, which Apollo may reject.
- **`people search` no longer drops results.** When Apollo returns both `people` and `contacts` (matched CRM records), both are now shown — previously only the first non-empty list was kept.
- **Conversation detail view is robust to raw dicts.** The participants/deals/summary/transcript sections read fields via a dict-or-model helper, so they render whether `conversations get` returns models or plain dicts (previously the sections silently rendered empty for dicts).
- **`--stage-name` errors are bounded.** An unknown stage name lists at most 15 available names (`… (+N more)`) instead of dumping the entire list.

### Note

- `conversations search --query` maps to Apollo's universal `q_keywords` param. The conversations search endpoint is undocumented and keyword filtering hasn't been confirmed server-side; if a search returns everything unfiltered, that param is the thing to revisit.

## [1.2.0] - 2026-07-08

Usage-driven UX improvements — every item here closes a gap where users had been dropping to raw curl or doing extra lookups.

### Added

- **people search — company-domain filter.** `people search --organization-domains acme.com,globex.com` (alias `--domains`) finds people at specific companies — the single most common raw-curl workaround (`q_organization_domains_list`). Also adds `--seniorities`, and `people search` now respects the global `--limit`/`--page` (it previously ignored them). Results render as a table instead of a raw dict.
- **Filter deals/contacts by stage name.** `deals search --stage-name "Negotiation"` and `contacts search --stage-name "Customer"` resolve the name to an ID internally, removing the round-trip through `pipelines stages` / `contacts stages`. An unknown name fails loudly and lists the valid names.
- **`conversations transcript ID`** — prints just the transcript (no metadata/summary), for when you only want the words.
- **Deal contact roles.** `deals role-types` lists the available role types; `deals set-role DEAL_ID --contact-id C [--role-type "Decision Maker"] [--primary]` sets/updates a contact's role on a deal (read-modify-write; `--primary` makes them the sole primary contact). Previously only reachable via curl.
- **`custom-fields list [--modality]`** — lists custom field definitions across contacts/accounts/opportunities.

### Changed

- Requires `qodev-apollo-api>=0.3.0` (for `update_opportunity_roles` and `list_custom_fields`).

## [1.1.0] - 2026-07-08

### Added

- **conversations**: new command group exposing the recorded-conversation endpoints (Zoom/Teams/Meet). `conversations search [--query]` lists conversations; `conversations get ID` returns the full detail including transcript and AI call summary (outcome, pain points, objections, next steps). The underlying `qodev-apollo-api` client already supported `search_conversations`/`get_conversation` — only the CLI surface was missing. Note this is distinct from `calls`, which covers dialer/phone-call activity, not recorded meetings.

## [1.0.0] - 2026-07-01

### Added

- **notes**: `--opportunity-ids` on `create` and `--opportunity-id` filter on `search`. The underlying `qodev-apollo-api` client already supported opportunity attachment; only the CLI surface was missing. Enables attaching notes directly to deals/opportunities so they appear in the deal view (previously notes could only be attached to accounts/contacts, which don't surface on the opportunity UI).

### Changed

- **BREAKING — `contacts find-by-linkedin` is now `contacts upsert-by-linkedin`** with honest get-or-create semantics. It returns the full contact plus a `created` flag (not a bare `contact_id`), a missing contact is a normal result rather than an exit-1 `not_found` error, and `--name` is required to create. Before creating it name-searches to avoid duplicating a contact stored under a different URL. Read-only lookups now use `contacts search --linkedin-url`.
- **internal**: Extracted the inline comma-splitting logic (used in `contacts update --label-ids`, `people search --titles/--locations`, `tasks create --contact-ids`, and `notes create --contact-ids/--account-ids/--opportunity-ids`) into a shared `apollo_cli.util.parse_comma_list` helper. Behavior is now consistent across every comma-list flag.

### Removed

- **BREAKING — `contacts find-by-linkedin`** (and its `--create` flag). The read path is `contacts search --linkedin-url`; the write path is `contacts upsert-by-linkedin`.

### Fixed

- **comma-list flags — forgiving on typos, loud on garbage.** All comma-separated CLI arguments now drop embedded empty segments, whitespace-only tokens, and leading/trailing commas — so `--contact-ids "a,,b"` sends `["a", "b"]` instead of `["a", "", "b"]` (which Apollo rejects with a 400). Empty (`""`) or whitespace-only input maps to "flag not provided", but input like `",,,"` — where the user typed *something* that collapses to nothing — now surfaces as a validation error (exit code 83, `"validation"`) via the CLI's central error handler, instead of a raw Python traceback or a silent flag-omit. Affects every command that takes a comma-list flag.
- **notes docs**: `README.md` and `skills/SKILL.md` referenced a non-existent `--note` flag on `notes create`; the actual flag has always been `--content`. Also surfaced the already-implemented `--account-id`/`--account-ids` flags in both docs (previously only `--contact-id`/`--contact-ids` were documented). AI agents following `SKILL.md` would have hit `--note` errors.
- **`contacts search --linkedin-url` now matches reliably.** Apollo stores and exact-matches LinkedIn URLs as `http://www.linkedin.com/in/<slug>` (http, `www`, no trailing slash, lowercase); the filter was passed through verbatim, so a normal `https://.../in/slug/` URL silently returned zero results. Inputs are now canonicalized to Apollo's stored form before searching (new `apollo_cli.linkedin` module).

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
</content>
</invoke>