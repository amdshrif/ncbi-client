# NCBI Client Examples

This directory contains example scripts demonstrating different ways to use the NCBI Client.

## Basic Examples

### `basic_usage.py`
Demonstrates basic usage of the NCBI Client library with simple search and fetch operations.

```bash
python basic_usage.py
```

### `comprehensive_example.py`
Shows advanced features including history server usage, batch processing, and error handling.

```bash
python comprehensive_example.py
```

## Command Line Interface Examples

### `simple_cli.py`
A complete CLI implementation using only Python standard library (no external dependencies).

```bash
# Get help
python simple_cli.py --help

# Search examples
python simple_cli.py search pubmed "COVID-19" --retmax 10
python simple_cli.py search protein "insulin" --format ids

# Fetch examples
python simple_cli.py fetch pubmed "33946458,33940777" --rettype abstract
python simple_cli.py fetch nucleotide "NM_000518" --rettype fasta --retmode text

# Summary examples
python simple_cli.py summary protein "1579325,1579326" --version 2.0

# Database info
python simple_cli.py info --list-only
python simple_cli.py info pubmed
```

### `fetch_abstracts.py`
Advanced example that searches PubMed, fetches abstracts, and saves results in multiple formats.

```bash
# Basic usage
python fetch_abstracts.py "CRISPR" --max-results 20

# Save as JSON
python fetch_abstracts.py "machine learning" --output ml_abstracts.json

# Save as XML
python fetch_abstracts.py "COVID-19 vaccine" --max-results 50 --output covid_abstracts.xml

# With API key for higher rate limits
python fetch_abstracts.py "cancer treatment" --api-key YOUR_KEY --max-results 100
```

## Running Examples

To run these examples, make sure the NCBI Client is installed or available in your Python path:

```bash
# Option 1: Install in development mode
pip install -e .

# Option 2: Add to Python path
export PYTHONPATH=/path/to/ncbi-client:$PYTHONPATH

# Option 3: Run from the package directory
cd ncbi-client
PYTHONPATH=. python examples/simple_cli.py --help
```

## Environment Variables

Set these environment variables to avoid passing credentials with each command:

```bash
export NCBI_API_KEY="your_api_key_here"
export NCBI_EMAIL="your.email@example.com"
```

## Creating Your Own Scripts

Use these examples as templates for your own scripts. Key patterns:

1. **Import the client**: `from ncbi_client import NCBIClient`
2. **Initialize with credentials**: `client = NCBIClient(api_key=api_key, email=email)`
3. **Handle errors**: Use try/except blocks for robust error handling
4. **Use appropriate formats**: Choose the right rettype/retmode for your needs
5. **Save results**: Write to files for further processing

## Common Use Cases

- **Literature search**: Search PubMed for articles on specific topics
- **Sequence retrieval**: Fetch DNA/protein sequences in FASTA format  
- **Database exploration**: List available databases and search fields
- **Data integration**: Combine results from multiple NCBI databases
- **Batch processing**: Process large lists of IDs or search terms
