# Account Enrichment Patterns

## Overview

Apollo provides two types of enrichment:
- **Organization enrichment** (FREE - no credits used)
- **Person enrichment** (1 credit per lookup)

## Organization Enrichment (FREE)

Enrich company data by domain without using credits:

```bash
# Basic enrichment
qodev-apollo-cli enrich org acme.com

# JSON output for scripting
qodev-apollo-cli --json enrich org acme.com

# Extract specific fields
qodev-apollo-cli --json enrich org acme.com | jq '{name, industry, employees: .estimated_num_employees}'
```

### What you get (FREE):
- Company name
- Industry classification
- Employee count estimate
- Company size category
- Website URL
- Social media profiles
- Founded year
- Revenue estimates
- Technologies used

## Account Search

Search for companies in Apollo's database:

```bash
# Search by name
qodev-apollo-cli accounts search --query "technology"

# Search by domain
qodev-apollo-cli accounts search --domain "acme.com"

# Pagination
qodev-apollo-cli accounts search --query "software" --page 2 --limit 50
```

## Account Details

```bash
# Get full account details
qodev-apollo-cli accounts get <account-id>

# Extract specific data
qodev-apollo-cli --json accounts get <account-id> | \
  jq '{name, domain, industry, employees: .estimated_num_employees}'
```

## Bulk Enrichment

Enrich multiple organizations:

```bash
# From a list of domains
cat domains.txt | while read domain; do
  echo "Enriching $domain..."
  qodev-apollo-cli --json enrich org "$domain" > "data/${domain}.json"
  sleep 1  # Rate limiting
done

# Extract key fields
for file in data/*.json; do
  jq '{domain: .domain, name: .name, industry: .industry, employees: .estimated_num_employees}' "$file"
done | jq -s '.'
```

## Person Enrichment (1 credit)

Enrich person data by email:

```bash
# Basic enrichment
qodev-apollo-cli enrich person jane@example.com

# JSON output
qodev-apollo-cli --json enrich person jane@example.com

# Extract contact details
qodev-apollo-cli --json enrich person jane@example.com | \
  jq '{name, title, company: .organization_name, linkedin: .linkedin_url}'
```

### What you get (1 credit):
- Full name
- Job title
- Company
- Email verification
- Phone numbers (if available)
- LinkedIn profile
- Work history
- Education

## Rate Limits and Usage

Check your API usage:

```bash
# View usage stats
qodev-apollo-cli usage

# JSON output for monitoring
qodev-apollo-cli --json usage | jq '{credits_available, requests_used, request_limit}'
```

## Enrichment Workflows

### Pre-meeting research

```bash
# Enrich company (free)
qodev-apollo-cli enrich org acme.com > company_info.txt

# Search for contacts at company
qodev-apollo-cli --json accounts search --domain "acme.com" | \
  jq -r '.items[0].id' | \
  xargs -I {} qodev-apollo-cli contacts search --account-id {}
```

### Lead qualification

```bash
# Enrich organization to check company size
company_size=$(qodev-apollo-cli --json enrich org "$domain" | \
  jq -r '.estimated_num_employees')

if [ "$company_size" -gt 100 ]; then
  echo "Qualified: Enterprise ($company_size employees)"
else
  echo "Not qualified: SMB ($company_size employees)"
fi
```

### Data enrichment pipeline

```bash
#!/bin/bash
# Enrich contacts from CSV

while IFS=, read -r email domain; do
  # Free org enrichment
  org_data=$(qodev-apollo-cli --json enrich org "$domain")

  # Paid person enrichment (1 credit)
  person_data=$(qodev-apollo-cli --json enrich person "$email")

  # Combine and save
  echo "{\"organization\": $org_data, \"person\": $person_data}" >> enriched_data.jsonl

  sleep 1  # Rate limiting
done < contacts.csv
```

## JSON Output Examples

### Organization Enrichment

```json
{
  "domain": "acme.com",
  "name": "Acme Corp",
  "industry": "Technology",
  "estimated_num_employees": 500,
  "website_url": "https://acme.com",
  "founded_year": 2010,
  "technologies": ["AWS", "React", "Python"]
}
```

### Person Enrichment

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "title": "VP Engineering",
  "organization_name": "Acme Corp",
  "linkedin_url": "https://linkedin.com/in/janesmith",
  "phone_numbers": [
    {"number": "+1-555-0100", "type": "mobile"}
  ]
}
```

## Best Practices

1. **Use free enrichment first**: Always enrich organizations (free) before enriching people (1 credit)
2. **Batch operations**: Process enrichment requests in batches with rate limiting
3. **Cache results**: Save enriched data to avoid duplicate lookups
4. **Monitor usage**: Check `qodev-apollo-cli usage` regularly to track credit consumption
5. **Validate domains**: Ensure domains are correctly formatted before enrichment
