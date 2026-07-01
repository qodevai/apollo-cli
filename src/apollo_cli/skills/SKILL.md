# qodev-apollo-cli

Agent-friendly CLI for the Apollo.io API. Designed for AI coding agents with structured JSON output and predictable exit codes.

## Setup

```bash
pip install qodev-apollo-cli
export APOLLO_API_KEY="your_api_key"

# Install skill files into the current workspace
qodev-apollo-cli install --skills
```

Get your API key from [Apollo.io Settings → API](https://app.apollo.io/#/settings/integrations/api).

## Global Options

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON (default: rich Markdown) |
| `--api-key` | Apollo API key (overrides APOLLO_API_KEY) |
| `--limit` | Results per page (default: 25) |
| `--page` | Page number (default: 1) |

## Command Reference

### contacts

| Command | Description |
|---------|-------------|
| `contacts search [--query Q] [--stage-id ID] [--linkedin-url URL]` | Search contacts |
| `contacts get ID` | Get contact details |
| `contacts create --first-name F --last-name L [--email E] [--title T] [--company C] [--linkedin-url URL]` | Create contact |
| `contacts update ID [--title T] [--label-ids IDS]` | Update contact |
| `contacts find-by-linkedin URL [--create] [--name N] [--stage-id ID]` | Find contact by LinkedIn URL |
| `contacts stages` | List all contact stages |

### accounts

| Command | Description |
|---------|-------------|
| `accounts search [--query Q] [--domain D]` | Search companies/accounts |
| `accounts get ID` | Get account details |

### deals

| Command | Description |
|---------|-------------|
| `deals search [--query Q] [--stage-id ID]` | Search opportunities/deals |
| `deals get ID` | Get deal details |

### pipelines

| Command | Description |
|---------|-------------|
| `pipelines list` | List all deal pipelines |
| `pipelines get ID` | Get pipeline details |
| `pipelines stages ID` | List stages in a pipeline |

### stages

| Command | Description |
|---------|-------------|
| `stages list` | List all contact stages |
| `stages get ID` | Get stage details |

### enrich

| Command | Description |
|---------|-------------|
| `enrich org DOMAIN` | Enrich organization by domain (FREE - no credits used) |
| `enrich person EMAIL` | Enrich person by email (1 credit per lookup) |

### people

| Command | Description |
|---------|-------------|
| `people search [--person-titles TITLES] [--q-organization-domains DOMAINS]` | Search people database |

### notes

| Command | Description |
|---------|-------------|
| `notes search [--contact-id ID] [--account-id ID] [--opportunity-id ID]` | Search notes |
| `notes create --content TEXT [--contact-ids IDS] [--account-ids IDS] [--opportunity-ids IDS]` | Create a note (attach to any combination of contacts/accounts/opportunities) |

### tasks

| Command | Description |
|---------|-------------|
| `tasks search [--type TYPE] [--status STATUS]` | Search tasks |
| `tasks create --contact-ids IDS --note TEXT [--due-at DATE]` | Create a task |

### calls

| Command | Description |
|---------|-------------|
| `calls search` | Search call activities |

### emails

| Command | Description |
|---------|-------------|
| `emails search` | Search email activities |

### news

| Command | Description |
|---------|-------------|
| `news search [--categories CATS]` | Search news |

### jobs

| Command | Description |
|---------|-------------|
| `jobs search [--job-titles TITLES] [--company-domains DOMAINS]` | Search job postings |

### usage

| Command | Description |
|---------|-------------|
| `usage` | Show API usage stats and rate limits |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 80 | Authentication error (invalid API key) |
| 81 | Rate limit exceeded |
| 82 | API error (server error, invalid request) |
| 83 | Validation error (missing required fields) |

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

## Common Patterns

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
# Find contact by LinkedIn URL
qodev-apollo-cli contacts find-by-linkedin "https://linkedin.com/in/janesmith"

# Auto-create if not found
qodev-apollo-cli contacts find-by-linkedin "https://linkedin.com/in/janesmith" --create

# Assign to stage on creation
qodev-apollo-cli contacts find-by-linkedin "https://linkedin.com/in/janesmith" \
  --create --stage-id <stage-id>
```

## References

- [Contact Management Workflows](references/contact-workflows.md)
- [Deal Pipeline Workflows](references/deal-workflows.md)
- [Account Enrichment Patterns](references/account-workflows.md)
