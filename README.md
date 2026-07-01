[![CI](https://github.com/qodevai/apollo-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/qodevai/apollo-cli/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/qodev-apollo-cli)](https://pypi.org/project/qodev-apollo-cli/)

# qodev-apollo-cli

Agent-friendly CLI for the Apollo.io API. Designed for both human and AI-agent workflows, with structured JSON output, consistent flags, and predictable error codes.

## Why this CLI?

- **Agent-friendly** — `--json` on every command, consistent flags, predictable exit codes
- **Built for AI agent workflows** — works seamlessly with Claude Code, scripts, and automation pipelines
- **Comprehensive** — Access contacts, accounts, deals, enrichment, tasks, notes, and more
- **Dual output modes** — Beautiful markdown tables for humans, structured JSON for agents

## Installation

```bash
pip install qodev-apollo-cli
```

Or run directly without installing:

```bash
uvx qodev-apollo-cli
```

## Quick Start

```bash
# Set your Apollo API key
export APOLLO_API_KEY="your_api_key_here"
```

```bash
# Install AI agent skill files (for Claude Code, etc.)
$ qodev-apollo-cli install --skills

# Search contacts
$ qodev-apollo-cli contacts search --query "engineer" --limit 5
Jane Smith     VP Engineering     Acme Corp     jane@acme.com

# Get contact details as JSON (for scripts/agents)
$ qodev-apollo-cli --json contacts get <contact-id>
{"id": "...", "name": "Jane Smith", "title": "VP Engineering", ...}

# Enrich a company (free)
$ qodev-apollo-cli enrich org acme.com

# Search deals in a specific stage
$ qodev-apollo-cli deals search --stage-id <stage-id>

# Check API usage
$ qodev-apollo-cli usage
```

## Commands

| Group | Subcommand | Description |
|---|---|---|
| **contacts** | `search` | Search contacts (`--query`, `--stage-id`, `--linkedin-url`) |
| | `get` | Get contact details by ID |
| | `create` | Create a new contact (`--first-name`, `--last-name`, `--email`, etc.) |
| | `update` | Update contact (`--title`, `--label-ids`) |
| | `upsert-by-linkedin` | Get or create a contact by LinkedIn URL (`--name`, `--title`, `--stage-id`) |
| | `stages` | List all contact stages |
| **accounts** | `search` | Search companies/accounts (`--query`, `--domain`) |
| | `get` | Get account details by ID |
| **deals** | `search` | Search opportunities/deals (`--query`, `--stage-id`) |
| | `get` | Get deal details by ID |
| **pipelines** | `list` | List all deal pipelines |
| | `get` | Get pipeline details |
| | `stages` | List stages in a pipeline |
| **stages** | `list` | List all contact stages |
| | `get` | Get stage details |
| **enrich** | `org` | Enrich organization by domain (FREE - no credits) |
| | `person` | Enrich person by email (1 credit per lookup) |
| **people** | `search` | Search people database (`--person-titles`, `--q-organization-domains`) |
| **notes** | `search` | Search notes (`--contact-id`, `--account-id`, `--opportunity-id`) |
| | `create` | Create a note (`--contact-ids`, `--account-ids`, `--opportunity-ids`, `--content`) |
| **tasks** | `search` | Search tasks (`--type`, `--status`) |
| | `create` | Create a task (`--contact-ids`, `--note`, `--due-at`) |
| **calls** | `search` | Search call activities |
| **emails** | `search` | Search email activities |
| **news** | `search` | Search news (`--categories`) |
| **jobs** | `search` | Search job postings (`--job-titles`, `--company-domains`) |
| **usage** | (default) | Show API usage stats and rate limits |
| **install** | `--skills` | Install AI agent skill files to `.claude/skills/apollo/` |

## Configuration

### Authentication

Set the `APOLLO_API_KEY` environment variable, or pass `--api-key` on each invocation:

```bash
export APOLLO_API_KEY="your_api_key_here"
```

Get your API key from [Apollo.io Settings → API](https://app.apollo.io/#/settings/integrations/api).

### Global Options

| Flag | Description | Default |
|---|---|---|
| `--json` | Output as JSON (for scripting / agents) | `false` |
| `--api-key` | Apollo API key (overrides `APOLLO_API_KEY`) | |
| `--limit` | Results per page | `25` |
| `--page` | Page number | `1` |

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `80` | Authentication error (invalid API key) |
| `81` | Rate limit exceeded |
| `82` | API error (server error, invalid request) |
| `83` | Validation error (missing required fields) |

## JSON Output

All commands support `--json` for structured output:

```bash
qodev-apollo-cli --json contacts search --query "engineer" | jq '.items[0].name'
```

Paginated responses include:

```json
{
  "items": [...],
  "total": 142,
  "page": 1,
  "limit": 25
}
```

## Common Workflows

### Find and enrich a contact

```bash
# Search by keyword
qodev-apollo-cli contacts search --query "jane smith"

# Get full details
qodev-apollo-cli contacts get <contact-id>

# Enrich person data (1 credit)
qodev-apollo-cli enrich person jane@example.com
```

### Pipeline management

```bash
# List all pipelines
qodev-apollo-cli pipelines list

# Get stages in a pipeline
qodev-apollo-cli pipelines stages <pipeline-id>

# Search deals in specific stage
qodev-apollo-cli deals search --stage-id <stage-id>
```

### LinkedIn integration

```bash
# Read-only lookup by LinkedIn URL (returns 0..n contacts, never writes)
qodev-apollo-cli contacts search --linkedin-url "https://linkedin.com/in/janesmith"

# Get or create a contact by LinkedIn URL (upsert); --name is required to create
qodev-apollo-cli contacts upsert-by-linkedin "https://linkedin.com/in/janesmith" --name "Jane Smith"

# Set title / stage when creating
qodev-apollo-cli contacts upsert-by-linkedin "https://linkedin.com/in/janesmith" \
  --name "Jane Smith" --title "VP Engineering" --stage-id <stage-id>
```

### Company enrichment (FREE)

```bash
# Enrich by domain (no credits used)
qodev-apollo-cli enrich org acme.com

# View as JSON
qodev-apollo-cli --json enrich org acme.com | jq '.industry'
```

## License

MIT -- see [LICENSE](LICENSE) for details.
