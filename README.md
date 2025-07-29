# NCBI Client

A comprehensive Python client for NCBI E-utilities and APIs, providing a modern, Pythonic interface to access biomedical data from the National Center for Biotechnology Information.

## Features

### Core E-utilities
- **Complete E-utilities Support**: All 9 E-utilities (ESearch, EFetch, EPost, ESummary, ELink, EInfo, EGQuery, ESpell, ECitMatch)
- **Rate Limiting**: Automatic rate limiting (3 req/sec without API key, 10 req/sec with API key)
- **History Server Management**: Efficient handling of large datasets using NCBI's history server
- **Authentication**: API key support for increased rate limits
- **SSL Certificate Handling**: Custom SSL context support and verification bypass for corporate environments

### Data Processing & Formats
- **Format Support**: Multiple output formats (XML, JSON, text, FASTA, GenBank, MEDLINE, etc.)
- **Advanced Parsers**: XML, JSON, FASTA, and GenBank parsers with data extraction
- **Format Converters**: Convert between different biological data formats
- **Sequence Tools**: Utilities for working with biological sequences

### Extended APIs
- **NCBI Datasets API**: Access genome assemblies, gene annotations, and genomic data
- **PubChem API**: Search and retrieve chemical compound information
- **Data Utilities**: Caching, history management, and batch processing tools

### Command Line Interface
- **Full-Featured CLI**: Complete command-line interface with click
- **Simple CLI**: Zero-dependency CLI using only Python standard library
- **SSL Support**: CLI options for handling SSL certificate issues

### Developer Features
- **Type Hints**: Full type annotation support for better IDE integration
- **Error Handling**: Comprehensive error handling and validation
- **Caching**: SQLite and memory-based caching systems
- **Testing**: Comprehensive test suite with examples

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ncbi-client.git
cd ncbi-client

# Install in development mode
pip install -e .
```

### Optional Dependencies

Install additional features based on your needs:

```bash
# For full CLI tools (requires click)
pip install -e .[cli]

# For data analysis features (pandas, numpy)  
pip install -e .[data]

# For bioinformatics tools (biopython)
pip install -e .[bio]

# For development (testing, linting)
pip install -e .[dev]

# All features
pip install -e .[all]
```

### Dependency-Free Usage

The core library and simple CLI work without any external dependencies:

```bash
# Core library only
pip install -e .

# Use the simple CLI (no click required)
python examples/simple_cli.py --help
```

## Quick Start

```python
from ncbi_client import NCBIClient

# Initialize client
client = NCBIClient(api_key="your_api_key", email="your@email.com")

# Search PubMed
results = client.esearch.search(
    db="pubmed",
    term="COVID-19 vaccine",
    retmax=100
)

print(f"Found {results['count']} articles")
print(f"First 10 PMIDs: {results['id_list'][:10]}")

# Fetch article abstracts
abstracts = client.efetch.fetch(
    db="pubmed", 
    id_list=results['id_list'][:5],
    rettype="abstract",
    retmode="xml"
)

# Get article summaries
summaries = client.esummary.summary(
    db="pubmed",
    id_list=results['id_list'][:5]
)

# Find related articles
related = client.elink.link(
    dbfrom="pubmed",
    db="pubmed", 
    id_list=results['id_list'][:3]
)
```

## E-utilities Overview

### ESearch - Search databases
```python
# Basic search
results = client.esearch.search(db="pubmed", term="cancer therapy")

# Search with history (for large datasets)
results = client.esearch.search_with_history(
    db="protein", 
    term="insulin human"
)
```

### EFetch - Retrieve records
```python
# Fetch in different formats
fasta = client.efetch.fetch(
    db="nucleotide",
    id_list=["34577062", "24475906"],
    rettype="fasta",
    retmode="text"
)

# Fetch from history server
records = client.efetch.fetch_from_history(
    db="pubmed",
    webenv=results['webenv'],
    query_key=results['query_key'],
    rettype="abstract"
)
```

### EPost - Upload ID lists
```python
# Upload IDs to history server
post_result = client.epost.post(
    db="gene",
    id_list=["7173", "22018", "54314"]
)

# Use posted IDs in subsequent calls
summaries = client.esummary.summary_from_history(
    db="gene",
    webenv=post_result['webenv'],
    query_key=post_result['query_key']
)
```

### ESummary - Get document summaries
```python
# Get summaries by IDs
summaries = client.esummary.summary(
    db="protein",
    id_list=["6678417", "9507199"]
)

# Use version 2.0 for richer data
summaries_v2 = client.esummary.summary(
    db="protein",
    id_list=["6678417", "9507199"],
    version="2.0"
)
```

### ELink - Find related data
```python
# Find related records
links = client.elink.link(
    dbfrom="nucleotide",
    db="protein",
    id_list=["34577062"]
)

# Find links with filtering
filtered_links = client.elink.link(
    dbfrom="pubmed",
    db="pubmed",
    id_list=["25359968"],
    term="review[filter]"
)
```

### EInfo - Database information
```python
# Get all databases
databases = client.einfo.get_databases()

# Get database details
db_info = client.einfo.get_database_info("pubmed")

# Get search fields
fields = client.einfo.get_search_fields("pubmed")
```

### EGQuery - Global search
```python
# Search across all databases
global_results = client.egquery.global_search("breast cancer")

for db_result in global_results['databases']:
    print(f"{db_result['dbname']}: {db_result['count']} hits")
```

### ESpell - Spelling suggestions
```python
# Get spelling suggestions
suggestions = client.espell.spell_check(
    db="pubmed",
    term="aasthma"  # misspelled "asthma"
)

print(f"Did you mean: {suggestions['corrected_query']}")
```

### ECitMatch - Citation matching
```python
# Match citations to PMIDs
citations = [
    "proc natl acad sci u s a|1991|88|3248|mann bj|Art1|",
    "science|1987|235|182|palmenberg ac|Art2|"
]

matches = client.ecitmatch.citation_match(citations)
```

## Extended APIs

### NCBI Datasets API

Access genome assemblies, gene annotations, and genomic data:

```python
from ncbi_client import DatasetsAPI

# Initialize Datasets API
datasets = DatasetsAPI()

# Search for genome assemblies
assemblies = datasets.search_assemblies(
    taxon="Homo sapiens",
    assembly_level="complete"
)

# Get assembly metadata
assembly_data = datasets.get_assembly_metadata("GCF_000001405.40")

# Download genome data
genome_files = datasets.download_assembly(
    accession="GCF_000001405.40",
    file_types=["genomic_fasta", "gff3"]
)
```

### PubChem API

Search and retrieve chemical compound information:

```python
from ncbi_client import PubChemAPI

# Initialize PubChem API
pubchem = PubChemAPI()

# Search for compounds by name
compounds = pubchem.search_compounds(
    query="aspirin",
    search_type="name"
)

# Get compound properties
properties = pubchem.get_compound_properties(
    cid=2244,  # Aspirin CID
    properties=["MolecularFormula", "MolecularWeight", "CanonicalSMILES"]
)

# Search for bioactivity data
assays = pubchem.search_assays(
    query="COVID-19",
    activity_type="IC50"
)
```

## Data Processing & Parsing

### Parsers

```python
from ncbi_client import XMLParser, JSONParser, FASTAParser, GenBankParser

# Parse XML responses
xml_parser = XMLParser()
parsed_data = xml_parser.parse_esearch_response(xml_response)

# Parse FASTA sequences
fasta_parser = FASTAParser()
sequences = fasta_parser.parse_sequences(fasta_text)

# Parse GenBank records
genbank_parser = GenBankParser()
records = genbank_parser.parse_records(genbank_text)

# Extract specific data from JSON
json_parser = JSONParser()
pmids = json_parser.extract_pmids(json_response)
```

### Format Converters

```python
from ncbi_client import FormatConverter, SequenceTools

# Convert between formats
converter = FormatConverter()
genbank_to_fasta = converter.genbank_to_fasta(genbank_data)
xml_to_json = converter.xml_to_json(xml_data)

# Sequence manipulation
seq_tools = SequenceTools()
reverse_complement = seq_tools.reverse_complement("ATCG")
translated = seq_tools.translate("ATGAAATAG")
gc_content = seq_tools.calculate_gc_content("ATCGATCG")
```

## Utilities & Helpers

### Caching System

```python
from ncbi_client import CacheManager, SQLiteCache, MemoryCache

# Use SQLite cache for persistent storage
cache = SQLiteCache("ncbi_cache.db")
client = NCBIClient(cache=cache)

# Use memory cache for temporary storage
memory_cache = MemoryCache(max_size=1000)
client = NCBIClient(cache=memory_cache)

# Manual cache operations
cache_manager = CacheManager(cache)
cache_manager.set("key", "value", ttl=3600)
value = cache_manager.get("key")
```

### History Management

```python
from ncbi_client import HistoryManager

# Manage search history
history = HistoryManager(client)

# Store search results
webenv, query_key = history.store_search_results(search_results)

# Retrieve from history
results = history.fetch_from_history(
    db="pubmed",
    webenv=webenv,
    query_key=query_key,
    retstart=0,
    retmax=100
)

# Combine multiple searches
combined = history.combine_searches([search1, search2])
```

### Helper Functions

```python
from ncbi_client.utils import (
    ValidationHelpers, FormatHelpers, XMLHelpers, 
    URLHelpers, DataHelpers, DateHelpers
)

# Validate inputs
ValidationHelpers.validate_database("pubmed")
ValidationHelpers.validate_ids(["123", "456"])

# Format data
formatted_ids = FormatHelpers.format_id_list([1, 2, 3])
clean_term = FormatHelpers.clean_search_term("term with spaces")

# XML utilities
XMLHelpers.extract_text(xml_element, "//title")
XMLHelpers.xml_to_dict(xml_string)

# URL building
url = URLHelpers.build_url("base", {"param": "value"})
encoded = URLHelpers.encode_params({"term": "COVID-19"})

# Data processing
DataHelpers.flatten_dict(nested_dict)
DataHelpers.chunk_list(large_list, chunk_size=100)

# Date handling
DateHelpers.format_date("2023-01-01")
DateHelpers.parse_pubmed_date("2023 Jan 15")
```

## Authentication

To use an API key for increased rate limits:

1. Get an API key from [NCBI](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)
2. Set it in your environment: `export NCBI_API_KEY=your_key_here`
3. Or pass it directly: `NCBIClient(api_key="your_key")`

## Error Handling

```python
from ncbi_client import NCBIError, RateLimitError, ValidationError

try:
    results = client.esearch.search(db="invalid_db", term="test")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except NCBIError as e:
    print(f"NCBI error: {e}")
```

### SSL Certificate Issues

If you encounter SSL certificate verification errors (common in corporate environments):

```python
# Disable SSL verification (not recommended for production)
client = NCBIClient(email="your@email.com", verify_ssl=False)

# Or use a custom SSL context
import ssl
context = ssl.create_default_context()
# Configure your context as needed
client = NCBIClient(email="your@email.com", ssl_context=context)
```

**CLI Usage:**
```bash
# Using the simple CLI
python simple_cli.py --no-ssl-verify search pubmed "COVID-19" --retmax 10

# Using the full CLI (if click is installed)
ncbi-client --no-ssl-verify search pubmed "COVID-19" --retmax 10
```

## Large Dataset Handling

```python
# For large datasets, use history server
search_result = client.esearch.search_with_history(
    db="pubmed",
    term="cancer",
    retmax=0  # Just get count and history
)

# Fetch in batches
batch_size = 500
total = search_result['count']

for start in range(0, min(total, 10000), batch_size):
    batch = client.efetch.fetch_from_history(
        db="pubmed",
        webenv=search_result['webenv'],
        query_key=search_result['query_key'],
        retstart=start,
        retmax=batch_size,
        rettype="abstract"
    )
    # Process batch...
```

## Command Line Interface

The NCBI Client provides multiple CLI options to suit different needs and environments.

### Full-Featured CLI (with click)

Install the CLI dependencies for the complete interface:

```bash
pip install -e .[cli]
```

#### Available Commands

**Core Commands:**
```bash
# Search databases
ncbi-client search <database> <query> [options]

# Fetch records  
ncbi-client fetch <database> <ids> [options]

# Get summaries
ncbi-client summary <database> <ids> [options]

# Link between databases
ncbi-client link <dbfrom> <dbto> <ids> [options]

# Database information
ncbi-client info [database] [options]

# Global search across all databases
ncbi-client global-search <query> [options]
```

#### Global CLI Options

```bash
--api-key TEXT          NCBI API key (or set NCBI_API_KEY env var)
--email TEXT            Email for identification (or set NCBI_EMAIL env var)
--tool TEXT             Tool name for identification (default: ncbi-client-cli)
--no-ssl-verify         Disable SSL certificate verification
--verbose, -v           Enable verbose output
--help                  Show help and exit
```

#### Command-Specific Options

**Search Options:**
```bash
--retmax INTEGER        Maximum number of results (default: 20)
--retstart INTEGER      Starting index (default: 0)  
--sort TEXT             Sort order (relevance, pub_date, author, etc.)
--format [json|ids|count]  Output format (default: json)
--output, -o FILE       Output file (default: stdout)
```

**Fetch Options:**
```bash
--rettype TEXT          Retrieval type (abstract, fasta, gb, etc.)
--retmode TEXT          Retrieval mode (xml, text, json)
--output, -o FILE       Output file (default: stdout)
```

**Summary Options:**
```bash
--version [1.0|2.0]     ESummary version (default: 1.0)
--output, -o FILE       Output file (default: stdout)
```

**Link Options:**
```bash
--cmd TEXT              Link command (default: neighbor)
--output, -o FILE       Output file (default: stdout)
```

**Info Options:**
```bash
--list-only             List available databases only
```

#### CLI Examples

```bash
# Search for recent COVID-19 papers
ncbi-client search pubmed "COVID-19" --retmax 10 --sort pub_date

# Get abstracts for specific PMIDs
ncbi-client fetch pubmed "33946458,33940777" --rettype abstract --retmode xml

# Find protein sequences related to a gene
ncbi-client link gene protein "1579" --output gene_proteins.json

# Get detailed information about PubMed database
ncbi-client info pubmed

# Search across all databases
ncbi-client global-search "BRCA1" --output brca1_global.json

# Handle SSL certificate issues (corporate environments)
ncbi-client --no-ssl-verify search pubmed "COVID-19" --retmax 5

# Use environment variables for credentials
export NCBI_API_KEY="your_key_here"
export NCBI_EMAIL="your.email@example.com"
ncbi-client search pubmed "diabetes" --retmax 20
```

### Simple CLI (Zero Dependencies)

For environments where you can't or don't want to install click:

```bash
# Using the simple CLI (no external dependencies required)
cd ncbi-client
python examples/simple_cli.py --help
```

#### Simple CLI Commands

```bash
# Search examples
python examples/simple_cli.py search pubmed "COVID-19" --retmax 10
python examples/simple_cli.py search protein "insulin" --format ids

# Fetch examples  
python examples/simple_cli.py fetch pubmed "33946458,33940777" --rettype abstract
python examples/simple_cli.py fetch nucleotide "NM_000518" --rettype fasta --retmode text

# Summary examples
python examples/simple_cli.py summary protein "1579325,1579326" --version 2.0

# Database info
python examples/simple_cli.py info --list-only
python examples/simple_cli.py info pubmed

# Global search
python examples/simple_cli.py global-search "CRISPR"

# SSL handling
python examples/simple_cli.py --no-ssl-verify search pubmed "COVID-19" --retmax 5
```

### Advanced CLI Scripts

The `examples/` directory contains specialized CLI scripts:

#### fetch_abstracts.py
Advanced script for fetching and processing abstracts:

```bash
# Fetch abstracts for recent CRISPR papers
python examples/fetch_abstracts.py "CRISPR" --max-results 20 --output crispr_abstracts.json

# Fetch COVID-19 vaccine abstracts as XML  
python examples/fetch_abstracts.py "COVID-19 vaccine" --max-results 50 --output covid_abstracts.xml
```

#### comprehensive_example.py
Demonstrates advanced features:

```bash
# Run comprehensive example with different datasets
python examples/comprehensive_example.py
```

### Environment Variables

Set these to avoid passing credentials with each command:

```bash
export NCBI_API_KEY="your_api_key_here"
export NCBI_EMAIL="your.email@example.com" 
export NCBI_TOOL="your_tool_name"
```

### Creating Custom CLI Scripts

Build your own simple scripts without external dependencies:

```python
#!/usr/bin/env python3
"""Custom NCBI search script."""

import sys
from ncbi_client import NCBIClient

def main():
    if len(sys.argv) < 3:
        print("Usage: python search.py <database> <query>")
        sys.exit(1)
    
    client = NCBIClient(email="your.email@example.com")
    
    database = sys.argv[1]
    query = " ".join(sys.argv[2:])
    
    results = client.esearch.search(db=database, term=query, retmax=10)
    
    print(f"Found {results['count']} results")
    for pmid in results['id_list']:
        print(pmid)

if __name__ == "__main__":
    main()
```

# Search examples
python examples/simple_cli.py search pubmed "COVID-19" --retmax 10
python examples/simple_cli.py search protein "insulin" --format ids

# Fetch examples  
python examples/simple_cli.py fetch pubmed "33946458,33940777" --rettype abstract
python examples/simple_cli.py fetch nucleotide "NM_000518" --rettype fasta --retmode text

# Summary examples
python examples/simple_cli.py summary protein "1579325,1579326" --version 2.0

# Database info
python examples/simple_cli.py info --list-only
python examples/simple_cli.py info pubmed
```

Or create your own simple scripts:

```python
#!/usr/bin/env python3
"""Simple search script without external dependencies."""

import sys
from ncbi_client import NCBIClient

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python search.py <database> <query>")
        sys.exit(1)
    
    client = NCBIClient(email="your.email@example.com")
    
    database = sys.argv[1]
    query = " ".join(sys.argv[2:])
    
    results = client.esearch.search(db=database, term=query, retmax=10)
    
    print(f"Found {results['count']} results")
    for pmid in results['id_list']:
        print(pmid)
```

### Advanced Example Scripts

The `examples/` directory contains more sophisticated CLI scripts:

**Fetch abstracts script:**
```bash
# Fetch abstracts for recent CRISPR papers
python examples/fetch_abstracts.py "CRISPR" --max-results 20 --output crispr_abstracts.json

# Fetch COVID-19 vaccine abstracts as XML
python examples/fetch_abstracts.py "COVID-19 vaccine" --max-results 50 --output covid_abstracts.xml
```

**Simple CLI script:**
```bash
# Full-featured CLI without external dependencies  
python examples/simple_cli.py search protein "insulin" --format ids
python examples/simple_cli.py fetch nucleotide "NM_000518" --rettype fasta
```

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## Examples & Use Cases

### Common Research Tasks

#### Literature Review
```python
# Search for papers on a topic
results = client.esearch.search(
    db="pubmed",
    term="machine learning AND genomics",
    retmax=100,
    sort="pub_date"
)

# Get detailed abstracts
abstracts = client.efetch.fetch(
    db="pubmed",
    id_list=results['id_list'][:20],
    rettype="abstract",
    retmode="xml"
)

# Extract key information
for abstract in parsed_abstracts:
    print(f"Title: {abstract['title']}")
    print(f"Authors: {', '.join(abstract['authors'])}")
    print(f"Journal: {abstract['journal']}")
    print(f"DOI: {abstract['doi']}")
    print("---")
```

#### Sequence Analysis Pipeline
```python
# Search for gene sequences
gene_search = client.esearch.search(
    db="gene",
    term="BRCA1[Gene Name] AND Homo sapiens[Organism]"
)

# Get gene information
gene_summary = client.esummary.summary(
    db="gene",
    id_list=gene_search['id_list'][:5]
)

# Find associated nucleotide sequences
nucleotide_links = client.elink.link(
    dbfrom="gene",
    db="nucleotide",
    id_list=gene_search['id_list'][:1]
)

# Fetch sequences in FASTA format
sequences = client.efetch.fetch(
    db="nucleotide",
    id_list=nucleotide_links['linked_ids'],
    rettype="fasta",
    retmode="text"
)

# Parse and analyze sequences
fasta_parser = FASTAParser()
parsed_sequences = fasta_parser.parse_sequences(sequences)

seq_tools = SequenceTools()
for seq in parsed_sequences:
    gc_content = seq_tools.calculate_gc_content(seq['sequence'])
    print(f"Sequence: {seq['id']}")
    print(f"GC Content: {gc_content:.2f}%")
```

#### Chemical Compound Research
```python
# Search PubChem for drug compounds
pubchem = PubChemAPI()

# Find compounds by name
aspirin = pubchem.search_compounds(
    query="aspirin",
    search_type="name"
)

# Get molecular properties
properties = pubchem.get_compound_properties(
    cid=aspirin['cids'][0],
    properties=[
        "MolecularFormula",
        "MolecularWeight", 
        "CanonicalSMILES",
        "LogP"
    ]
)

# Find bioactivity data
bioactivity = pubchem.search_assays(
    query="aspirin",
    activity_type="IC50"
)
```

#### Genomic Data Analysis
```python
# Access genome assemblies via Datasets API
datasets = DatasetsAPI()

# Search for human genome assemblies
assemblies = datasets.search_assemblies(
    taxon="9606",  # Human taxonomy ID
    assembly_level="complete"
)

# Get assembly metadata
assembly_metadata = datasets.get_assembly_metadata(
    "GCF_000001405.40"  # Human reference genome
)

# Download specific chromosome
chromosome_data = datasets.download_assembly(
    accession="GCF_000001405.40",
    chromosomes=["1", "2"],
    file_types=["genomic_fasta"]
)
```

### Batch Processing Examples

#### Processing Large ID Lists
```python
# Handle large lists of PMIDs
large_pmid_list = ["12345", "67890", ...]  # thousands of IDs

# Use history server for efficiency
post_result = client.epost.post(
    db="pubmed",
    id_list=large_pmid_list
)

# Fetch in batches
batch_size = 500
total_batches = len(large_pmid_list) // batch_size + 1

for batch_num in range(total_batches):
    start = batch_num * batch_size
    
    batch_abstracts = client.efetch.fetch_from_history(
        db="pubmed",
        webenv=post_result['webenv'],
        query_key=post_result['query_key'],
        retstart=start,
        retmax=batch_size,
        rettype="abstract"
    )
    
    # Process batch
    process_abstracts(batch_abstracts)
```

#### Multi-Database Search Pipeline
```python
# Search across multiple databases
search_term = "COVID-19"

databases = ["pubmed", "pmc", "gene", "protein", "nucleotide"]
all_results = {}

for db in databases:
    try:
        results = client.esearch.search(
            db=db,
            term=search_term,
            retmax=100
        )
        all_results[db] = results
        print(f"{db}: {results['count']} results")
    except NCBIError as e:
        print(f"Error searching {db}: {e}")

# Cross-reference results
gene_ids = all_results['gene']['id_list'][:10]
if gene_ids:
    # Find associated proteins
    protein_links = client.elink.link(
        dbfrom="gene",
        db="protein",
        id_list=gene_ids
    )
```

### Advanced Error Handling
```python
import time
from ncbi_client import NCBIError, RateLimitError, APIError

def robust_search(client, db, term, max_retries=3):
    """Robust search with retry logic."""
    
    for attempt in range(max_retries):
        try:
            results = client.esearch.search(
                db=db,
                term=term,
                retmax=100
            )
            return results
            
        except RateLimitError:
            # Wait and retry for rate limits
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited, waiting {wait_time} seconds...")
            time.sleep(wait_time)
            
        except APIError as e:
            if "Invalid database" in str(e):
                print(f"Invalid database: {db}")
                return None
            else:
                print(f"API error: {e}")
                
        except NCBIError as e:
            print(f"NCBI error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
    
    return None

# Usage
results = robust_search(client, "pubmed", "cancer therapy")
```

### Data Export and Analysis
```python
import json
import csv

# Export search results to different formats
def export_search_results(results, format_type="json", filename="results"):
    """Export results in various formats."""
    
    if format_type == "json":
        with open(f"{filename}.json", "w") as f:
            json.dump(results, f, indent=2)
            
    elif format_type == "csv":
        with open(f"{filename}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["PMID", "Title", "Authors", "Journal"])
            
            for article in results:
                writer.writerow([
                    article.get("pmid", ""),
                    article.get("title", ""),
                    "; ".join(article.get("authors", [])),
                    article.get("journal", "")
                ])
                
    elif format_type == "txt":
        with open(f"{filename}.txt", "w") as f:
            for pmid in results['id_list']:
                f.write(f"{pmid}\n")

# Generate reports
def generate_summary_report(search_results):
    """Generate a summary report from search results."""
    
    total_results = search_results['count']
    retrieved_ids = len(search_results['id_list'])
    
    report = f"""
    Search Results Summary
    =====================
    Total Results: {total_results}
    Retrieved IDs: {retrieved_ids}
    Search Term: {search_results.get('term', 'Unknown')}
    Database: {search_results.get('db', 'Unknown')}
    
    Top PMIDs:
    {chr(10).join(search_results['id_list'][:10])}
    """
    
    return report
```

### Integration Examples

#### Web Application Integration
```python
from flask import Flask, request, jsonify
from ncbi_client import NCBIClient

app = Flask(__name__)
client = NCBIClient(api_key="your_key", email="your@email.com")

@app.route('/search')
def search_endpoint():
    """API endpoint for PubMed search."""
    query = request.args.get('q')
    database = request.args.get('db', 'pubmed')
    max_results = int(request.args.get('max', 20))
    
    try:
        results = client.esearch.search(
            db=database,
            term=query,
            retmax=max_results
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch/<pmid>')
def fetch_abstract(pmid):
    """Fetch article abstract by PMID."""
    try:
        abstract = client.efetch.fetch(
            db="pubmed",
            id_list=[pmid],
            rettype="abstract",
            retmode="xml"
        )
        return abstract
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

#### Jupyter Notebook Integration
```python
# For Jupyter notebooks
import pandas as pd
import matplotlib.pyplot as plt

def analyze_publication_trends(search_term, years=5):
    """Analyze publication trends over time."""
    
    yearly_counts = {}
    current_year = 2024
    
    for year in range(current_year - years, current_year + 1):
        query = f"{search_term} AND {year}[PDAT]"
        results = client.esearch.search(
            db="pubmed",
            term=query,
            retmax=0  # Just get count
        )
        yearly_counts[year] = results['count']
    
    # Create DataFrame for analysis
    df = pd.DataFrame(list(yearly_counts.items()), 
                     columns=['Year', 'Publications'])
    
    # Plot trends
    plt.figure(figsize=(10, 6))
    plt.plot(df['Year'], df['Publications'], marker='o')
    plt.title(f'Publication Trends: {search_term}')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.grid(True)
    plt.show()
    
    return df

# Usage in notebook
## Performance & Best Practices

### Optimization Tips

#### 1. Use API Keys
```python
# Without API key: 3 requests/second
client = NCBIClient(email="your@email.com")

# With API key: 10 requests/second  
client = NCBIClient(
    api_key="your_api_key",
    email="your@email.com"
)
```

#### 2. Leverage History Server
```python
# Efficient for large datasets
search_result = client.esearch.search_with_history(
    db="pubmed",
    term="cancer",
    retmax=0  # Just get count and history
)

# Fetch in manageable batches
for start in range(0, min(search_result['count'], 10000), 500):
    batch = client.efetch.fetch_from_history(
        db="pubmed",
        webenv=search_result['webenv'],
        query_key=search_result['query_key'],
        retstart=start,
        retmax=500
    )
    process_batch(batch)
```

#### 3. Choose Appropriate Formats
```python
# For IDs only - fastest
ids_only = client.esearch.search(db="pubmed", term="query", retmax=1000)

# For metadata - medium speed
summaries = client.esummary.summary(db="pubmed", id_list=ids)

# For full content - slowest
abstracts = client.efetch.fetch(
    db="pubmed", 
    id_list=ids, 
    rettype="abstract"
)
```

#### 4. Implement Caching
```python
# Use SQLite cache for persistent storage
cache = SQLiteCache("ncbi_cache.db", ttl=86400)  # 24 hour TTL
client = NCBIClient(cache=cache)

# Results are automatically cached
results1 = client.esearch.search(db="pubmed", term="diabetes")
results2 = client.esearch.search(db="pubmed", term="diabetes")  # From cache
```

#### 5. Batch Operations
```python
# Instead of multiple single requests
for pmid in pmid_list:
    summary = client.esummary.summary(db="pubmed", id_list=[pmid])  # Slow

# Batch multiple IDs together
batch_summaries = client.esummary.summary(
    db="pubmed", 
    id_list=pmid_list[:200]  # Process in batches of 200
)
```

### Performance Monitoring

```python
import time
from ncbi_client import NCBIClient

class PerformanceClient(NCBIClient):
    """Client with performance monitoring."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_count = 0
        self.total_time = 0
    
    def _make_request(self, *args, **kwargs):
        start_time = time.time()
        result = super()._make_request(*args, **kwargs)
        end_time = time.time()
        
        self.request_count += 1
        self.total_time += (end_time - start_time)
        
        return result
    
    def get_stats(self):
        avg_time = self.total_time / self.request_count if self.request_count > 0 else 0
        return {
            "requests": self.request_count,
            "total_time": self.total_time,
            "average_time": avg_time
        }

# Usage
client = PerformanceClient(api_key="your_key")
# ... perform operations ...
stats = client.get_stats()
print(f"Made {stats['requests']} requests in {stats['total_time']:.2f}s")
```

## Troubleshooting

### Common Issues and Solutions

#### SSL Certificate Errors
```python
# Problem: SSL certificate verification failed
# Solution 1: Disable SSL verification (not recommended for production)
client = NCBIClient(email="your@email.com", verify_ssl=False)

# Solution 2: Use custom SSL context
import ssl
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
client = NCBIClient(email="your@email.com", ssl_context=context)

# CLI usage
python examples/simple_cli.py --no-ssl-verify search pubmed "query"
```

#### Rate Limiting Issues
```python
# Problem: Rate limit exceeded
# Solution: Implement retry with backoff
import time
from ncbi_client import RateLimitError

def search_with_retry(client, **kwargs):
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            return client.esearch.search(**kwargs)
        except RateLimitError:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"Rate limited, waiting {delay}s...")
                time.sleep(delay)
            else:
                raise
```

#### Memory Issues with Large Datasets
```python
# Problem: Memory consumption with large result sets
# Solution: Use generators and streaming

def fetch_large_dataset(client, db, term, batch_size=500):
    """Generator for processing large datasets."""
    
    # Get total count
    search_result = client.esearch.search_with_history(
        db=db, term=term, retmax=0
    )
    
    total = search_result['count']
    webenv = search_result['webenv']
    query_key = search_result['query_key']
    
    # Yield results in batches
    for start in range(0, total, batch_size):
        batch = client.efetch.fetch_from_history(
            db=db,
            webenv=webenv,
            query_key=query_key,
            retstart=start,
            retmax=batch_size
        )
        yield batch

# Usage
for batch in fetch_large_dataset(client, "pubmed", "cancer", batch_size=100):
    process_batch(batch)  # Process one batch at a time
```

#### Authentication Problems
```python
# Problem: API key not working
# Debugging steps:

# 1. Verify API key format
api_key = "your_key_here"
assert len(api_key) == 36, "API key should be 36 characters"

# 2. Check environment variables
import os
print("NCBI_API_KEY:", os.getenv('NCBI_API_KEY'))
print("NCBI_EMAIL:", os.getenv('NCBI_EMAIL'))

# 3. Test with minimal request
client = NCBIClient(api_key=api_key, email="your@email.com")
try:
    result = client.esearch.search(db="pubmed", term="test", retmax=1)
    print("API key working:", result['count'] >= 0)
except Exception as e:
    print("API key issue:", e)
```

#### Database and Query Issues
```python
# Problem: Invalid database or search terms
# Solution: Validate inputs

from ncbi_client.utils import ValidationHelpers

# Check valid databases
valid_dbs = client.einfo.get_databases()
print("Valid databases:", valid_dbs)

# Validate database name
try:
    ValidationHelpers.validate_database("pubmed")  # Valid
    ValidationHelpers.validate_database("invalid_db")  # Raises error
except ValueError as e:
    print("Database validation error:", e)

# Check search fields for a database
fields = client.einfo.get_search_fields("pubmed")
print("Available search fields:", [f['name'] for f in fields])
```

#### Network and Timeout Issues
```python
# Problem: Network timeouts or connection issues
# Solution: Configure timeout and retry settings

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Custom session with retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Use custom session (if supported by client)
# client = NCBIClient(session=session)
```

### Debugging Tips

#### Enable Verbose Logging
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ncbi_client')

# Log all requests
client = NCBIClient(email="your@email.com", debug=True)
```

#### Inspect Raw Responses
```python
# Get raw XML response for debugging
raw_response = client.efetch.fetch(
    db="pubmed",
    id_list=["12345"],
    rettype="abstract",
    retmode="xml"
)

print("Raw response:")
print(raw_response[:1000])  # First 1000 characters
```

#### Test with Known Working Examples
```python
# Test basic functionality
def test_basic_functionality():
    """Test basic client functionality."""
    
    client = NCBIClient(email="test@example.com")
    
    try:
        # Test search
        results = client.esearch.search(db="pubmed", term="aspirin", retmax=1)
        assert results['count'] > 0, "Search should return results"
        
        # Test fetch
        if results['id_list']:
            abstract = client.efetch.fetch(
                db="pubmed",
                id_list=results['id_list'][:1],
                rettype="abstract"
            )
            assert len(abstract) > 0, "Fetch should return data"
        
        print("Basic functionality test: PASSED")
        
    except Exception as e:
        print(f"Basic functionality test: FAILED - {e}")

test_basic_functionality()
```

### When to Use CLI vs Python API

**Use the CLI when:**
- Performing one-off searches or data retrieval
- Creating shell scripts or automation workflows
- Quick exploration of NCBI databases
- Batch processing with Unix tools
- Working in environments where Python scripting is limited

**Use the Python API when:**
- Integrating with larger Python applications
- Need complex data processing or analysis
- Building web applications or services  
- Require custom error handling or retry logic
## API Reference

### Core Classes

#### NCBIClient
Main client class for accessing NCBI services.

```python
NCBIClient(
    api_key: Optional[str] = None,
    email: Optional[str] = None,
    tool: str = "ncbi-client",
    verify_ssl: bool = True,
    ssl_context: Optional[ssl.SSLContext] = None,
    cache: Optional[CacheManager] = None,
    rate_limiter: Optional[RateLimiter] = None
)
```

**Parameters:**
- `api_key`: NCBI API key for increased rate limits
- `email`: Email address for identification (required)
- `tool`: Tool name for identification
- `verify_ssl`: Enable/disable SSL certificate verification
- `ssl_context`: Custom SSL context
- `cache`: Custom cache implementation
- `rate_limiter`: Custom rate limiter

### E-utilities Classes

#### ESearch
Search NCBI databases.

```python
esearch.search(
    db: str,
    term: str,
    retmax: int = 20,
    retstart: int = 0,
    sort: Optional[str] = None,
    field: Optional[str] = None,
    datetype: Optional[str] = None,
    reldate: Optional[int] = None,
    mindate: Optional[str] = None,
    maxdate: Optional[str] = None
) -> Dict[str, Any]
```

#### EFetch  
Retrieve records from databases.

```python
efetch.fetch(
    db: str,
    id_list: List[str],
    rettype: str = "docsum",
    retmode: str = "xml",
    retstart: int = 0,
    retmax: Optional[int] = None,
    strand: Optional[int] = None,
    seq_start: Optional[int] = None,
    seq_stop: Optional[int] = None
) -> str
```

#### ESummary
Get document summaries.

```python
esummary.summary(
    db: str,
    id_list: List[str],
    version: str = "1.0"
) -> Dict[str, Any]
```

#### ELink
Find related data.

```python
elink.link(
    dbfrom: str,
    db: str,
    id_list: List[str],
    cmd: str = "neighbor",
    term: Optional[str] = None,
    holding: Optional[str] = None
) -> Dict[str, Any]
```

#### EInfo
Database information.

```python
einfo.get_databases() -> List[str]
einfo.get_database_info(db: str) -> Dict[str, Any]
einfo.get_search_fields(db: str) -> List[Dict[str, Any]]
```

#### EGQuery
Global search across databases.

```python
egquery.global_search(term: str) -> Dict[str, Any]
```

#### ESpell
Spelling suggestions.

```python
espell.spell_check(
    db: str,
    term: str
) -> Dict[str, Any]
```

#### ECitMatch
Citation matching.

```python
ecitmatch.citation_match(
    citations: List[str]
) -> Dict[str, Any]
```

### Extended APIs

#### DatasetsAPI
Access NCBI Datasets.

```python
datasets = DatasetsAPI()

datasets.search_assemblies(
    taxon: str,
    assembly_level: Optional[str] = None,
    annotation_status: Optional[str] = None
) -> Dict[str, Any]

datasets.get_assembly_metadata(
    accession: str
) -> Dict[str, Any]
```

#### PubChemAPI
Access PubChem database.

```python
pubchem = PubChemAPI()

pubchem.search_compounds(
    query: str,
    search_type: str = "name"
) -> Dict[str, Any]

pubchem.get_compound_properties(
    cid: int,
    properties: List[str]
) -> Dict[str, Any]
```

### Parsers

#### XMLParser
```python
xml_parser = XMLParser()
parsed = xml_parser.parse_esearch_response(xml_string)
```

#### FASTAParser
```python
fasta_parser = FASTAParser()
sequences = fasta_parser.parse_sequences(fasta_text)
```

#### GenBankParser
```python
genbank_parser = GenBankParser()
records = genbank_parser.parse_records(genbank_text)
```

### Utilities

#### CacheManager
```python
# SQLite cache
cache = SQLiteCache("cache.db", ttl=3600)

# Memory cache
cache = MemoryCache(max_size=1000, ttl=3600)

# Cache operations
cache.get(key)
cache.set(key, value, ttl=3600)
cache.delete(key)
cache.clear()
```

#### HistoryManager
```python
history = HistoryManager(client)
webenv, query_key = history.store_search_results(results)
combined = history.combine_searches([search1, search2])
```

#### SequenceTools
```python
seq_tools = SequenceTools()
gc_content = seq_tools.calculate_gc_content("ATCGATCG")
reverse_comp = seq_tools.reverse_complement("ATCG")
translated = seq_tools.translate("ATGAAATAG")
```

### Exception Classes

```python
from ncbi_client import (
    NCBIError,           # Base exception
    APIError,            # API-related errors
    RateLimitError,      # Rate limiting errors
    AuthenticationError, # Authentication errors
    ValidationError      # Input validation errors
)
```

### Supported Databases

**Literature:**
- `pubmed` - PubMed citations
- `pmc` - PubMed Central full-text articles
- `books` - NCBI Bookshelf

**Sequences:**
- `nucleotide` - GenBank nucleotide sequences
- `protein` - GenBank protein sequences
- `genome` - Genome assemblies
- `popset` - Population study datasets

**Structures:**
- `structure` - 3D protein structures
- `pccompound` - PubChem compounds
- `pcsubstance` - PubChem substances

**Genes & Expression:**
- `gene` - Gene database
- `homologene` - HomoloGene homology groups
- `snp` - Single nucleotide polymorphisms
- `dbvar` - Database of genomic structural variation

**Clinical:**
- `clinvar` - Clinical variants
- `medgen` - Medical genetics
- `omim` - Online Mendelian Inheritance in Man

**Taxonomy & Phylogeny:**
- `taxonomy` - NCBI Taxonomy
- `bioproject` - BioProject database
- `biosample` - BioSample database

### Supported Formats

**Retrieval Types (rettype):**

*PubMed:*
- `abstract` - Abstract with metadata
- `citation` - Citation format
- `medline` - MEDLINE format

*Sequences:*
- `fasta` - FASTA sequences
- `gb` - GenBank format
- `gp` - GenPept format
- `native` - Native format

*Structures:*
- `mmdb` - MMDB format
- `pdb` - PDB format

**Retrieval Modes (retmode):**
- `xml` - XML format (default for most)
- `json` - JSON format
- `text` - Plain text
- `html` - HTML format
- `asn1` - ASN.1 format

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ncbi-client.git
cd ncbi-client

# Install in development mode with all dependencies
pip install -e .[dev,cli,data,bio]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=ncbi_client

# Run specific test file
python -m pytest tests/test_esearch.py
```

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black ncbi_client/
isort ncbi_client/

# Check linting
flake8 ncbi_client/
mypy ncbi_client/
```

### Adding Features

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Add tests** for your feature
4. **Update documentation** if needed
5. **Submit a pull request**

### Documentation

Documentation is built with Sphinx:

```bash
# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

### Release Process

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create release tag
4. GitHub Actions will handle PyPI publishing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 NCBI Client Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Citation

If you use this software in your research, please cite:

```bibtex
@software{ncbi_client,
  author = {NCBI Client Contributors},
  title = {NCBI Client: A Python library for accessing NCBI E-utilities},
  url = {https://github.com/yourusername/ncbi-client},
  version = {1.0.0},
  year = {2024}
}
```

## Acknowledgments

- **NCBI Team** for providing comprehensive APIs and documentation
- **BioPython** project for inspiration and best practices
- **All contributors** who have helped improve this project

### Built With

- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) - Core API
- [NCBI Datasets](https://www.ncbi.nlm.nih.gov/datasets/) - Genome data API  
- [PubChem PUG-REST](https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest) - Chemical data API
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Requests](https://docs.python-requests.org/) - HTTP library

## Support

- **Documentation**: [Full documentation](https://github.com/yourusername/ncbi-client/docs)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ncbi-client/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ncbi-client/discussions)
- **Email**: For sensitive issues, contact maintainers directly

## Changelog

### Version 1.0.0 (2024-07-28)

**Features:**
- Complete E-utilities implementation (all 9 tools)
- NCBI Datasets API integration
- PubChem API integration  
- Advanced parsers and format converters
- Comprehensive CLI with SSL support
- Caching system (SQLite and memory)
- Rate limiting and error handling
- Type hints and documentation

**Breaking Changes:**
- Initial release

**Bug Fixes:**
- SSL certificate handling for corporate environments
- Rate limiting edge cases
- Error message improvements

**Documentation:**
- Complete API reference
- Usage examples and tutorials
- Troubleshooting guide
- Performance optimization tips

## Acknowledgments

- Built according to [NCBI E-utilities documentation](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- Inspired by BioPython's Entrez module
- Thanks to NCBI for providing comprehensive APIs
