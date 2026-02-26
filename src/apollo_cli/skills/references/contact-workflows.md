# Contact Management Workflows

## Search and Filter

Search contacts with various filters:

```bash
# Keyword search
qodev-apollo-cli contacts search --query "engineer"

# Filter by stage
qodev-apollo-cli contacts search --stage-id <stage-id>

# Filter by LinkedIn URL
qodev-apollo-cli contacts search --linkedin-url "https://linkedin.com/in/..."

# Pagination
qodev-apollo-cli contacts search --query "engineer" --page 2 --limit 50
```

## LinkedIn Integration

Find or create contacts from LinkedIn profiles:

```bash
# Find existing contact by LinkedIn URL
qodev-apollo-cli contacts find-by-linkedin "https://linkedin.com/in/janesmith"

# Auto-create if not found
qodev-apollo-cli contacts find-by-linkedin "https://linkedin.com/in/janesmith" --create

# Specify name for fallback search
qodev-apollo-cli contacts find-by-linkedin "https://linkedin.com/in/janesmith" --name "Jane Smith"

# Assign to stage on creation
qodev-apollo-cli contacts find-by-linkedin "https://linkedin.com/in/janesmith" --create --stage-id <stage-id>
```

## Contact Creation

Create new contacts manually:

```bash
qodev-apollo-cli contacts create \
  --first-name Jane \
  --last-name Smith \
  --email jane@example.com \
  --title "VP Engineering" \
  --company "Acme Corp" \
  --linkedin-url "https://linkedin.com/in/janesmith"
```

## Update Contact Fields

```bash
# Update title
qodev-apollo-cli contacts update <contact-id> --title "CTO"

# Update labels
qodev-apollo-cli contacts update <contact-id> --label-ids "label1,label2,label3"
```

## View Contact Stages

List all available contact stages:

```bash
qodev-apollo-cli contacts stages
```

## JSON Output for Scripting

Extract specific fields using jq:

```bash
# Get contact emails
qodev-apollo-cli --json contacts search --query "engineer" | jq '.items[].email'

# Count total results
qodev-apollo-cli --json contacts search --query "engineer" | jq '.total'

# Extract contact IDs
qodev-apollo-cli --json contacts search --query "engineer" | jq '.items[].id'
```

## Bulk Operations

Process multiple contacts using JSON output:

```bash
# Search and process each contact
qodev-apollo-cli --json contacts search --query "VP" | \
  jq -r '.items[].id' | \
  while read id; do
    qodev-apollo-cli contacts get "$id"
  done
```

## Filtering by Stage

```bash
# List all stages to find IDs
qodev-apollo-cli contacts stages

# Search contacts in specific stage
qodev-apollo-cli contacts search --stage-id <stage-id>

# JSON output for stage filtering
qodev-apollo-cli --json contacts stages | jq '.items[] | select(.name=="Qualified Lead") | .id'
```
