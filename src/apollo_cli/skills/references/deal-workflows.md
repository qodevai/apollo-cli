# Deal Pipeline Workflows

## Understanding Pipelines

Apollo.io uses pipelines to organize sales opportunities. Each pipeline has multiple stages representing the sales process.

## List Pipelines

```bash
# View all pipelines
qodev-apollo-cli pipelines list

# Get details of specific pipeline
qodev-apollo-cli pipelines get <pipeline-id>

# View as JSON
qodev-apollo-cli --json pipelines list | jq '.items[].name'
```

## Pipeline Stages

```bash
# List stages in a pipeline
qodev-apollo-cli pipelines stages <pipeline-id>

# Get stage details
qodev-apollo-cli stages get <stage-id>

# Extract stage IDs with jq
qodev-apollo-cli --json pipelines stages <pipeline-id> | jq '.items[] | {name, id}'
```

## Searching Deals

```bash
# Search all deals
qodev-apollo-cli deals search

# Search by deal name (--query matches the deal name, not free keywords)
qodev-apollo-cli deals search --query "enterprise"

# Filter by stage
qodev-apollo-cli deals search --stage-id <stage-id>

# Pagination
qodev-apollo-cli deals search --page 2 --limit 50
```

## Deal Details

```bash
# Get deal details
qodev-apollo-cli deals get <deal-id>

# Extract specific fields with jq
qodev-apollo-cli --json deals get <deal-id> | jq '{name, amount, stage_name, is_won}'
```

## Pipeline Analysis

Analyze deals across stages:

```bash
# Count deals per stage
qodev-apollo-cli --json deals search --stage-id <stage-id> | jq '.total'

# List all won deals
qodev-apollo-cli --json deals search | jq '.items[] | select(.is_won==true)'

# Calculate total deal value
qodev-apollo-cli --json deals search | jq '[.items[].amount] | add'
```

## Stage Movement Tracking

Track deals as they move through stages:

```bash
# Get current stage distribution
for stage_id in $(qodev-apollo-cli --json pipelines stages <pipeline-id> | jq -r '.items[].id'); do
  count=$(qodev-apollo-cli --json deals search --stage-id "$stage_id" | jq '.total')
  stage_name=$(qodev-apollo-cli --json stages get "$stage_id" | jq -r '.name')
  echo "$stage_name: $count deals"
done
```

## JSON Output Examples

### Pipeline List

```json
{
  "items": [
    {
      "id": "pipeline-123",
      "name": "Sales Pipeline",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Deal Search

```json
{
  "items": [
    {
      "id": "deal-789",
      "name": "Enterprise Deal",
      "amount": 50000,
      "stage_name": "Negotiation",
      "is_won": false,
      "owner_id": "owner-123"
    }
  ],
  "total": 25,
  "page": 1,
  "limit": 25
}
```

## Common Scenarios

### Find deals in final stage

```bash
# Get final stage ID
final_stage=$(qodev-apollo-cli --json pipelines stages <pipeline-id> | \
  jq -r '.items[-1].id')

# Search deals in final stage
qodev-apollo-cli deals search --stage-id "$final_stage"
```

### Track deal progression

```bash
# Monitor specific deal
watch -n 60 'qodev-apollo-cli deals get <deal-id> | grep -E "(stage_name|is_won)"'
```
