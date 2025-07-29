# Quick Start Guide

Get up and running with NCBI Client in 5 minutes!

## Basic Setup

```python
from ncbi_client import NCBIClient

# Initialize the client
client = NCBIClient(email="your.email@example.com")

# With API key (recommended for higher rate limits)
client = NCBIClient(
    api_key="your_api_key",
    email="your.email@example.com"
)
```

## Your First Search

### Search PubMed for Articles

```python
# Search for COVID-19 vaccine papers
results = client.esearch.search(
    db="pubmed",
    term="COVID-19 vaccine",
    retmax=10
)

print(f"Found {results['count']} articles")
print(f"First 10 PMIDs: {results['id_list']}")
```

### Get Article Details

```python
# Fetch abstracts for the first 5 articles
abstracts = client.efetch.fetch(
    db="pubmed",
    id_list=results['id_list'][:5],
    rettype="abstract",
    retmode="xml"
)

print("Abstracts retrieved:", len(abstracts))
```

### Get Article Summaries

```python
# Get structured summaries
summaries = client.esummary.summary(
    db="pubmed",
    id_list=results['id_list'][:5]
)

for summary in summaries['docsums']:
    print(f"Title: {summary['Title']}")
    print(f"Authors: {', '.join(summary['AuthorList'])}")
    print(f"Journal: {summary['Source']}")
    print("---")
```

## Sequence Data

### Search for Gene Sequences

```python
# Search for insulin gene sequences
gene_results = client.esearch.search(
    db="gene",
    term="insulin[Gene Name] AND Homo sapiens[Organism]",
    retmax=5
)

print(f"Found {gene_results['count']} insulin genes")
```

### Fetch DNA Sequences

```python
# Find related nucleotide sequences
nucleotide_links = client.elink.link(
    dbfrom="gene",
    db="nucleotide", 
    id_list=gene_results['id_list'][:1]
)

if nucleotide_links['linked_ids']:
    # Fetch sequences in FASTA format
    sequences = client.efetch.fetch(
        db="nucleotide",
        id_list=nucleotide_links['linked_ids'][:3],
        rettype="fasta",
        retmode="text"
    )
    
    print("FASTA sequences:")
    print(sequences[:500] + "...")  # First 500 characters
```

## Command Line Usage

### Simple CLI (No Dependencies)

```bash
# Search PubMed
python examples/simple_cli.py search pubmed "diabetes" --retmax 5

# Fetch abstracts
python examples/simple_cli.py fetch pubmed "12345,67890" --rettype abstract

# Get summaries
python examples/simple_cli.py summary pubmed "12345" --version 2.0
```

### Full CLI (With Click)

```bash
# Install CLI dependencies first
pip install -e .[cli]

# Use the full CLI
ncbi-client search pubmed "cancer therapy" --retmax 20 --sort pub_date
ncbi-client fetch nucleotide "NM_000518" --rettype fasta --output sequences.fasta
ncbi-client info pubmed  # Get database information
```

## Chemical Compounds

### Search PubChem

```python
from ncbi_client import PubChemAPI

# Initialize PubChem client
pubchem = PubChemAPI()

# Search for aspirin
compounds = pubchem.search_compounds(
    query="aspirin",
    search_type="name"
)

print(f"Found {len(compounds['cids'])} compounds")

# Get molecular properties
if compounds['cids']:
    properties = pubchem.get_compound_properties(
        cid=compounds['cids'][0],
        properties=["MolecularFormula", "MolecularWeight"]
    )
    print(f"Aspirin formula: {properties['MolecularFormula']}")
    print(f"Molecular weight: {properties['MolecularWeight']}")
```

## Data Processing

### Parse Results

```python
from ncbi_client import XMLParser, FASTAParser

# Parse XML responses
xml_parser = XMLParser()
parsed_data = xml_parser.parse_esearch_response(xml_response)

# Parse FASTA sequences
fasta_parser = FASTAParser()
sequences = fasta_parser.parse_sequences(fasta_text)

for seq in sequences:
    print(f"ID: {seq['id']}")
    print(f"Description: {seq['description']}")
    print(f"Length: {len(seq['sequence'])}")
```

### Convert Formats

```python
from ncbi_client import FormatConverter

converter = FormatConverter()

# Convert XML to JSON
json_data = converter.xml_to_json(xml_data)

# Convert GenBank to FASTA
fasta_data = converter.genbank_to_fasta(genbank_data)
```

## Error Handling

```python
from ncbi_client import NCBIError, RateLimitError, ValidationError

try:
    results = client.esearch.search(
        db="pubmed",
        term="machine learning",
        retmax=100
    )
except RateLimitError:
    print("Rate limit exceeded - please wait or use an API key")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except NCBIError as e:
    print(f"NCBI API error: {e}")
```

## Caching for Performance

```python
from ncbi_client import SQLiteCache

# Use persistent caching
cache = SQLiteCache("ncbi_cache.db", ttl=3600)  # 1 hour TTL
client = NCBIClient(
    email="your@email.com",
    cache=cache
)

# First call hits the API
results1 = client.esearch.search(db="pubmed", term="diabetes")

# Second call uses cache
results2 = client.esearch.search(db="pubmed", term="diabetes")  # Faster!
```

## Large Datasets

### Using History Server

```python
# For large searches, use history server
large_search = client.esearch.search_with_history(
    db="pubmed",
    term="cancer",
    retmax=0  # Just get count and history
)

print(f"Total results: {large_search['count']}")

# Fetch in batches
batch_size = 500
for start in range(0, min(large_search['count'], 5000), batch_size):
    batch = client.efetch.fetch_from_history(
        db="pubmed",
        webenv=large_search['webenv'],
        query_key=large_search['query_key'],
        retstart=start,
        retmax=batch_size,
        rettype="abstract"
    )
    print(f"Processed batch starting at {start}")
    # Process your batch here
```

## Configuration

### Environment Variables

```bash
# Set these in your shell profile
export NCBI_API_KEY="your_api_key_here"
export NCBI_EMAIL="your.email@example.com"
export NCBI_TOOL="your_tool_name"
```

### SSL Issues (Corporate Networks)

```python
# Disable SSL verification if needed
client = NCBIClient(
    email="your@email.com",
    verify_ssl=False  # Only use in corporate environments
)
```

```bash
# CLI with SSL bypass
python examples/simple_cli.py --no-ssl-verify search pubmed "query"
```

## Next Steps

Now that you've got the basics:

1. **Explore [Tutorials](../tutorials/)** for specific use cases
2. **Read the [User Guide](basic-usage.md)** for detailed explanations
3. **Check [API Reference](../api-reference/)** for complete documentation
4. **Browse [Examples](../examples/)** for real-world applications
5. **Learn about [Performance](performance.md)** optimization

## Common Patterns

### Literature Review Workflow

```python
# 1. Search for papers
papers = client.esearch.search(
    db="pubmed",
    term="CRISPR AND gene editing",
    retmax=100,
    sort="pub_date"
)

# 2. Get abstracts
abstracts = client.efetch.fetch(
    db="pubmed",
    id_list=papers['id_list'][:20],
    rettype="abstract"
)

# 3. Find related papers
related = client.elink.link(
    dbfrom="pubmed",
    db="pubmed",
    id_list=papers['id_list'][:5]
)

print(f"Found {len(related['linked_ids'])} related papers")
```

### Sequence Analysis Pipeline

```python
# 1. Search for genes
genes = client.esearch.search(
    db="gene",
    term="BRCA1[Gene Name] AND Homo sapiens[Organism]"
)

# 2. Get gene information
gene_info = client.esummary.summary(
    db="gene",
    id_list=genes['id_list'][:1]
)

# 3. Find protein sequences
proteins = client.elink.link(
    dbfrom="gene",
    db="protein",
    id_list=genes['id_list'][:1]
)

# 4. Fetch protein sequences
if proteins['linked_ids']:
    sequences = client.efetch.fetch(
        db="protein",
        id_list=proteins['linked_ids'][:5],
        rettype="fasta"
    )
    print("Retrieved protein sequences")
```

---

**Ready to dive deeper?** Check out our [detailed tutorials](../tutorials/) or [API reference](../api-reference/)!
