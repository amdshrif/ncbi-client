# Command Line Interface

The NCBI Client provides powerful command-line interfaces for accessing NCBI databases without writing Python code.

## CLI Options

### 1. Simple CLI (Zero Dependencies)
Perfect for quick tasks and environments where you can't install additional packages.

### 2. Full CLI (With Click)
Feature-rich interface with advanced options and better user experience.

## Simple CLI Usage

### Basic Commands

The simple CLI provides all core functionality using only Python standard library:

```bash
# Get help
python examples/simple_cli.py --help

# Available commands:
# - search: Search NCBI databases
# - fetch: Retrieve records
# - summary: Get document summaries
# - link: Find related data
# - info: Database information
# - global-search: Search across all databases
```

### Search Commands

```bash
# Basic search
python examples/simple_cli.py search pubmed "COVID-19" --retmax 10

# Search with different formats
python examples/simple_cli.py search pubmed "diabetes" --format ids --output pmids.txt
python examples/simple_cli.py search pubmed "cancer" --format count
python examples/simple_cli.py search protein "insulin" --format json

# Advanced search options
python examples/simple_cli.py search pubmed "machine learning AND genomics" --retmax 50 --sort pub_date
python examples/simple_cli.py search nucleotide "BRCA1[Gene Name]" --retstart 10 --retmax 20
```

### Fetch Commands

```bash
# Fetch abstracts
python examples/simple_cli.py fetch pubmed "33946458,33940777" --rettype abstract

# Fetch sequences
python examples/simple_cli.py fetch nucleotide "NM_000518" --rettype fasta --retmode text

# Fetch with output to file
python examples/simple_cli.py fetch protein "P01308" --rettype fasta --output insulin.fasta

# Different retrieval types
python examples/simple_cli.py fetch pubmed "12345" --rettype medline
python examples/simple_cli.py fetch gene "7157" --rettype gene_table
```

### Summary Commands

```bash
# Get document summaries
python examples/simple_cli.py summary pubmed "33946458,33940777"

# Use different versions
python examples/simple_cli.py summary protein "P01308" --version 2.0
python examples/simple_cli.py summary gene "7157" --version 1.0

# Output to file
python examples/simple_cli.py summary pubmed "12345,67890" --output summaries.json
```

### Link Commands

```bash
# Find related data
python examples/simple_cli.py link gene protein "7157"
python examples/simple_cli.py link pubmed pubmed "33946458" 
python examples/simple_cli.py link nucleotide protein "NM_000518"

# Output to file
python examples/simple_cli.py link gene pubmed "7157" --output gene_papers.json
```

### Info Commands

```bash
# List all databases
python examples/simple_cli.py info --list-only

# Get database information
python examples/simple_cli.py info pubmed
python examples/simple_cli.py info protein
python examples/simple_cli.py info nucleotide
```

### Global Search

```bash
# Search across all databases
python examples/simple_cli.py global-search "CRISPR"
python examples/simple_cli.py global-search "COVID-19" --output global_results.json
```

## Full CLI Usage (With Click)

### Installation

First install the CLI dependencies:

```bash
pip install -e .[cli]
```

### Core Commands

```bash
# The full CLI provides the same functionality with better UX
ncbi-client --help

# Available commands:
ncbi-client search
ncbi-client fetch  
ncbi-client summary
ncbi-client link
ncbi-client info
ncbi-client global-search
```

### Global Options

All commands support these global options:

```bash
--api-key TEXT          # NCBI API key (or set NCBI_API_KEY env var)
--email TEXT            # Email for identification (or set NCBI_EMAIL env var)
--tool TEXT             # Tool name (default: ncbi-client-cli)
--no-ssl-verify         # Disable SSL certificate verification
--verbose, -v           # Enable verbose output
--help                  # Show help
```

### Search Command

```bash
# Basic usage
ncbi-client search <database> <query> [OPTIONS]

# Options:
--retmax INTEGER        # Maximum results (default: 20)
--retstart INTEGER      # Starting index (default: 0)
--sort TEXT             # Sort order (pub_date, author, etc.)
--format [json|ids|count] # Output format (default: json)
--output, -o FILE       # Output file (default: stdout)

# Examples:
ncbi-client search pubmed "COVID-19 vaccine" --retmax 100 --sort pub_date
ncbi-client search gene "BRCA1" --format ids --output brca1_ids.txt
ncbi-client --api-key YOUR_KEY search protein "insulin" --retmax 50
```

### Fetch Command

```bash
# Basic usage
ncbi-client fetch <database> <ids> [OPTIONS]

# Options:
--rettype TEXT          # Retrieval type (abstract, fasta, gb, etc.)
--retmode TEXT          # Retrieval mode (xml, text, json)
--output, -o FILE       # Output file (default: stdout)

# Examples:
ncbi-client fetch pubmed "33946458,33940777" --rettype abstract --retmode xml
ncbi-client fetch nucleotide "NM_000518" --rettype fasta --output sequence.fasta
ncbi-client fetch protein "P01308" --rettype gb --retmode text
```

### Summary Command

```bash
# Basic usage
ncbi-client summary <database> <ids> [OPTIONS]

# Options:
--version [1.0|2.0]     # ESummary version (default: 1.0)
--output, -o FILE       # Output file (default: stdout)

# Examples:
ncbi-client summary pubmed "33946458,33940777" --version 2.0
ncbi-client summary gene "7157" --output gene_summary.json
```

### Link Command

```bash
# Basic usage
ncbi-client link <dbfrom> <dbto> <ids> [OPTIONS]

# Options:
--cmd TEXT              # Link command (default: neighbor)
--output, -o FILE       # Output file (default: stdout)

# Examples:
ncbi-client link gene protein "7157"
ncbi-client link pubmed pubmed "33946458" --cmd neighbor_history
ncbi-client link nucleotide protein "NM_000518" --output links.json
```

### Info Command

```bash
# Basic usage
ncbi-client info [database] [OPTIONS]

# Options:
--list-only             # List databases only

# Examples:
ncbi-client info --list-only
ncbi-client info pubmed
ncbi-client info protein
```

### Global Search Command

```bash
# Basic usage
ncbi-client global-search <query> [OPTIONS]

# Options:
--output, -o FILE       # Output file (default: stdout)

# Examples:
ncbi-client global-search "CRISPR"
ncbi-client global-search "Alzheimer disease" --output alzheimer_global.json
```

## SSL Certificate Handling

Both CLIs support SSL certificate issues common in corporate environments:

### Simple CLI
```bash
python examples/simple_cli.py --no-ssl-verify search pubmed "query"
python examples/simple_cli.py --no-ssl-verify fetch pubmed "12345" --rettype abstract
```

### Full CLI
```bash
ncbi-client --no-ssl-verify search pubmed "query"
ncbi-client --no-ssl-verify fetch pubmed "12345" --rettype abstract
```

## Environment Variables

Set these to avoid repeating credentials:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export NCBI_API_KEY="your_api_key_here"
export NCBI_EMAIL="your.email@example.com"
export NCBI_TOOL="your_tool_name"
```

Then use commands without specifying credentials:

```bash
# Simple CLI automatically uses environment variables
python examples/simple_cli.py search pubmed "diabetes"

# Full CLI also uses environment variables
ncbi-client search pubmed "diabetes"
```

## Output Formats

### JSON Output (Default)
```bash
python examples/simple_cli.py search pubmed "aspirin" --format json
```

### ID Lists Only
```bash
python examples/simple_cli.py search pubmed "aspirin" --format ids
# Output: one ID per line
```

### Count Only
```bash
python examples/simple_cli.py search pubmed "aspirin" --format count
# Output: just the number
```

### File Output
```bash
# Save to file
python examples/simple_cli.py search pubmed "diabetes" --output results.json
python examples/simple_cli.py fetch pubmed "12345" --rettype abstract --output abstract.xml
```

## Common Workflows

### Literature Review Pipeline

```bash
#!/bin/bash
# Literature review script

QUERY="CRISPR AND gene editing"
OUTPUT_DIR="literature_review"

mkdir -p $OUTPUT_DIR

# 1. Search for papers
python examples/simple_cli.py search pubmed "$QUERY" --retmax 100 --format ids --output $OUTPUT_DIR/pmids.txt

# 2. Fetch abstracts
python examples/simple_cli.py fetch pubmed "$(cat $OUTPUT_DIR/pmids.txt | head -20 | tr '\n' ',')" --rettype abstract --output $OUTPUT_DIR/abstracts.xml

# 3. Get summaries
python examples/simple_cli.py summary pubmed "$(cat $OUTPUT_DIR/pmids.txt | head -20 | tr '\n' ',')" --output $OUTPUT_DIR/summaries.json

echo "Literature review data saved to $OUTPUT_DIR/"
```

### Sequence Analysis Pipeline

```bash
#!/bin/bash
# Sequence analysis script

GENE="BRCA1"
OUTPUT_DIR="sequence_analysis"

mkdir -p $OUTPUT_DIR

# 1. Find gene
python examples/simple_cli.py search gene "$GENE[Gene Name] AND Homo sapiens[Organism]" --format ids --output $OUTPUT_DIR/gene_ids.txt

# 2. Get gene info
GENE_ID=$(head -1 $OUTPUT_DIR/gene_ids.txt)
python examples/simple_cli.py summary gene "$GENE_ID" --output $OUTPUT_DIR/gene_info.json

# 3. Find protein sequences
python examples/simple_cli.py link gene protein "$GENE_ID" --output $OUTPUT_DIR/protein_links.json

# 4. Fetch sequences (extract IDs from JSON first with jq)
# python examples/simple_cli.py fetch protein "PROTEIN_IDS" --rettype fasta --output $OUTPUT_DIR/proteins.fasta

echo "Sequence analysis data saved to $OUTPUT_DIR/"
```

### Batch Processing

```bash
#!/bin/bash
# Process multiple queries

QUERIES=("diabetes" "cancer" "COVID-19" "CRISPR")

for query in "${QUERIES[@]}"; do
    echo "Processing: $query"
    
    # Create output directory
    mkdir -p "batch_results/$query"
    
    # Search and save results
    python examples/simple_cli.py search pubmed "$query" --retmax 50 --output "batch_results/$query/search_results.json"
    
    # Get top 10 abstracts
    python examples/simple_cli.py search pubmed "$query" --retmax 10 --format ids | \
    xargs -I {} python examples/simple_cli.py fetch pubmed {} --rettype abstract --output "batch_results/$query/abstracts.xml"
    
    echo "Completed: $query"
done

echo "Batch processing complete!"
```

## Performance Tips

### Use API Keys
```bash
# Much faster with API key
export NCBI_API_KEY="your_key"
python examples/simple_cli.py search pubmed "large query" --retmax 1000
```

### Batch Operations
```bash
# Instead of multiple single requests:
# python examples/simple_cli.py fetch pubmed "123" --rettype abstract
# python examples/simple_cli.py fetch pubmed "456" --rettype abstract

# Use batch requests:
python examples/simple_cli.py fetch pubmed "123,456,789" --rettype abstract
```

### Cache Results
```bash
# Save intermediate results to avoid re-querying
python examples/simple_cli.py search pubmed "complex query" --output search_cache.json

# Later, use the cached IDs
cat search_cache.json | jq -r '.id_list[]' | head -10 | tr '\n' ',' | \
python examples/simple_cli.py fetch pubmed /dev/stdin --rettype abstract
```

## Troubleshooting

### Common Issues

#### Command Not Found
```bash
# If ncbi-client command not found:
pip install -e .[cli]
# Or use the simple CLI:
python examples/simple_cli.py --help
```

#### SSL Errors
```bash
# Use --no-ssl-verify flag
python examples/simple_cli.py --no-ssl-verify search pubmed "query"
```

#### Rate Limiting
```bash
# Get an API key and set it:
export NCBI_API_KEY="your_key"
```

#### Large Results
```bash
# Use smaller batch sizes and retstart for pagination
python examples/simple_cli.py search pubmed "query" --retmax 100 --retstart 0
python examples/simple_cli.py search pubmed "query" --retmax 100 --retstart 100
```

---

**Next:** Learn about [Data Processing](data-processing.md) or explore [API Reference](../api-reference/)
