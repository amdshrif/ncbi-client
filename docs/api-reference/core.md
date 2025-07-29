# API Reference

Complete reference for all NCBI Client classes and methods.

## Core Client

### NCBIClient

The main client class providing access to all NCBI services.

```python
from ncbi_client import NCBIClient

client = NCBIClient(
    api_key="your_api_key",
    email="your.email@example.com", 
    tool="your_tool_name",
    verify_ssl=True,
    ssl_context=None,
    cache=None,
    rate_limiter=None
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | `None` | NCBI API key for higher rate limits |
| `email` | `str` | **Required** | Email address for identification |
| `tool` | `str` | `"ncbi-client"` | Tool name for identification |
| `verify_ssl` | `bool` | `True` | Enable SSL certificate verification |
| `ssl_context` | `ssl.SSLContext` | `None` | Custom SSL context |
| `cache` | `Cache` | `None` | Cache instance for response caching |
| `rate_limiter` | `RateLimiter` | `None` | Custom rate limiter |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `esearch` | `ESearch` | Search interface |
| `efetch` | `EFetch` | Fetch interface |
| `epost` | `EPost` | Post interface |
| `esummary` | `ESummary` | Summary interface |
| `elink` | `ELink` | Link interface |
| `einfo` | `EInfo` | Info interface |
| `egquery` | `EGQuery` | Global query interface |
| `espell` | `ESpell` | Spell check interface |
| `ecitmatch` | `ECitMatch` | Citation match interface |

#### Examples

```python
# Basic usage
client = NCBIClient(email="user@example.com")

# With API key for better performance
client = NCBIClient(
    api_key="your_key",
    email="user@example.com"
)

# With custom SSL context
import ssl
context = ssl.create_default_context()
client = NCBIClient(
    email="user@example.com",
    ssl_context=context
)

# With caching
from ncbi_client import SQLiteCache
cache = SQLiteCache("ncbi_cache.db")
client = NCBIClient(
    email="user@example.com",
    cache=cache
)
```

## E-utilities

### ESearch

Search NCBI databases for records matching a query.

#### Methods

##### `search(db, term, **kwargs)`

Search for records in a database.

```python
results = client.esearch.search(
    db="pubmed",
    term="COVID-19 vaccine",
    retmax=100,
    sort="pub_date"
)
```

**Parameters:**
- `db` (str): Database name
- `term` (str): Search query  
- `retmax` (int, optional): Maximum results (default: 20)
- `retstart` (int, optional): Starting index (default: 0)
- `sort` (str, optional): Sort order
- `field` (str, optional): Search field
- `datetype` (str, optional): Date type for filtering
- `reldate` (int, optional): Relative date in days
- `mindate` (str, optional): Minimum date (YYYY/MM/DD)
- `maxdate` (str, optional): Maximum date (YYYY/MM/DD)

**Returns:** `Dict[str, Any]`
```python
{
    "count": 1234,
    "id_list": ["12345", "67890", ...],
    "translation_set": [...],
    "query_translation": "...",
    "retmax": 20,
    "retstart": 0
}
```

##### `search_with_history(db, term, **kwargs)`

Search with history server for large datasets.

```python
results = client.esearch.search_with_history(
    db="pubmed", 
    term="cancer",
    retmax=0  # Just get count and history
)
```

**Additional Returns:**
```python
{
    # ... standard search results ...
    "webenv": "MCID_...",
    "query_key": "1"
}
```

### EFetch

Retrieve full records from NCBI databases.

#### Methods

##### `fetch(db, id_list, **kwargs)`

Fetch records by ID list.

```python
records = client.efetch.fetch(
    db="pubmed",
    id_list=["12345", "67890"],
    rettype="abstract",
    retmode="xml"
)
```

**Parameters:**
- `db` (str): Database name
- `id_list` (List[str]): List of record IDs
- `rettype` (str, optional): Retrieval type (default: "docsum")
- `retmode` (str, optional): Retrieval mode (default: "xml")
- `retstart` (int, optional): Starting index
- `retmax` (int, optional): Maximum records
- `strand` (int, optional): DNA strand (1 or 2)
- `seq_start` (int, optional): Sequence start position
- `seq_stop` (int, optional): Sequence stop position
- `complexity` (int, optional): Data complexity level

**Returns:** `str` - Raw response data

##### `fetch_from_history(db, webenv, query_key, **kwargs)`

Fetch records from history server.

```python
records = client.efetch.fetch_from_history(
    db="pubmed",
    webenv=search_result['webenv'],
    query_key=search_result['query_key'],
    retstart=0,
    retmax=500
)
```

### ESummary

Get document summaries with key metadata.

#### Methods

##### `summary(db, id_list, **kwargs)`

Get summaries for ID list.

```python
summaries = client.esummary.summary(
    db="pubmed",
    id_list=["12345", "67890"],
    version="2.0"
)
```

**Parameters:**
- `db` (str): Database name
- `id_list` (List[str]): List of record IDs
- `version` (str, optional): ESummary version ("1.0" or "2.0")
- `retstart` (int, optional): Starting index
- `retmax` (int, optional): Maximum records

**Returns:** `Dict[str, Any]`
```python
{
    "docsums": [
        {
            "uid": "12345",
            "title": "Article Title",
            "authors": ["Author1", "Author2"],
            "source": "Journal Name",
            "pubdate": "2023",
            "doi": "10.1234/example",
            # ... more fields
        }
    ],
    "version": "2.0"
}
```

##### `summary_from_history(db, webenv, query_key, **kwargs)`

Get summaries from history server.

### EPost

Upload ID lists to NCBI history server.

#### Methods

##### `post(db, id_list, **kwargs)`

Upload IDs to history server.

```python
result = client.epost.post(
    db="gene",
    id_list=["7173", "22018", "54314"]
)
```

**Returns:** `Dict[str, str]`
```python
{
    "webenv": "MCID_...",
    "query_key": "1"
}
```

### ELink

Find related records across databases.

#### Methods

##### `link(dbfrom, db, id_list, **kwargs)`

Find linked records.

```python
links = client.elink.link(
    dbfrom="gene",
    db="protein", 
    id_list=["7173"],
    cmd="neighbor"
)
```

**Parameters:**
- `dbfrom` (str): Source database
- `db` (str): Target database  
- `id_list` (List[str]): Source record IDs
- `cmd` (str, optional): Link command (default: "neighbor")
- `linkname` (str, optional): Specific link type
- `term` (str, optional): Filter term
- `holding` (str, optional): Holding library

**Returns:** `Dict[str, Any]`
```python
{
    "linked_ids": ["456", "789"],
    "linksets": [...],
    "cmd": "neighbor"
}
```

### EInfo

Get database and field information.

#### Methods

##### `get_databases()`

Get list of all available databases.

```python
databases = client.einfo.get_databases()
# Returns: ["pubmed", "protein", "nucleotide", ...]
```

##### `get_database_info(db)`

Get detailed information about a database.

```python
info = client.einfo.get_database_info("pubmed")
```

**Returns:** `Dict[str, Any]`
```python
{
    "dbname": "pubmed",
    "description": "PubMed citations and abstracts",
    "count": "35000000",
    "lastupdate": "2023/12/31",
    "fields": [...],
    "links": [...]
}
```

##### `get_search_fields(db)`

Get available search fields for a database.

```python
fields = client.einfo.get_search_fields("pubmed")
```

**Returns:** `List[Dict[str, str]]`
```python
[
    {
        "name": "ALL",
        "fullname": "All Fields",
        "description": "All terms from all searchable fields"
    },
    # ... more fields
]
```

### EGQuery

Search across all NCBI databases simultaneously.

#### Methods

##### `global_search(term)`

Search term across all databases.

```python
results = client.egquery.global_search("BRCA1")
```

**Returns:** `Dict[str, Any]`
```python
{
    "term": "BRCA1",
    "databases": [
        {
            "dbname": "pubmed",
            "count": "12345",
            "status": "Ok"
        },
        # ... more databases
    ]
}
```

### ESpell

Get spelling suggestions for search terms.

#### Methods

##### `spell_check(db, term)`

Get spelling suggestions.

```python
suggestions = client.espell.spell_check(
    db="pubmed",
    term="aasthma"  # misspelled "asthma"
)
```

**Returns:** `Dict[str, str]`
```python
{
    "original_query": "aasthma",
    "corrected_query": "asthma",
    "suggestions": ["asthma"]
}
```

### ECitMatch

Match citations to PubMed IDs.

#### Methods

##### `citation_match(citations)`

Match citation strings to PMIDs.

```python
citations = [
    "proc natl acad sci u s a|1991|88|3248|mann bj|Art1|",
    "science|1987|235|182|palmenberg ac|Art2|"
]
matches = client.ecitmatch.citation_match(citations)
```

**Returns:** `List[Dict[str, str]]`
```python
[
    {
        "citation": "proc natl acad sci u s a|1991|88|3248|mann bj|Art1|",
        "pmid": "2014182"
    },
    # ... more matches
]
```

## Supported Databases

| Database | Name | Description |
|----------|------|-------------|
| `pubmed` | PubMed | Citations and abstracts |
| `pmc` | PMC | Full-text articles |
| `books` | Books | NCBI Bookshelf |
| `nucleotide` | GenBank | Nucleotide sequences |
| `protein` | GenBank | Protein sequences |
| `genome` | Genome | Complete genomes |
| `structure` | Structure | 3D structures |
| `gene` | Gene | Gene database |
| `homologene` | HomoloGene | Homology groups |
| `snp` | dbSNP | SNP database |
| `clinvar` | ClinVar | Clinical variants |
| `pccompound` | PubChem | Chemical compounds |
| `taxonomy` | Taxonomy | Organism classification |
| `bioproject` | BioProject | Research projects |
| `biosample` | BioSample | Sample metadata |

## Retrieval Types by Database

### PubMed (`pubmed`)
- `abstract` - Abstract and metadata (XML)
- `medline` - MEDLINE format
- `uilist` - Simple ID list
- `docsum` - Document summary

### Nucleotide (`nucleotide`)
- `fasta` - FASTA format sequences
- `gb` - GenBank flat file format
- `gbwithparts` - GenBank with assembly
- `acc` - Accession numbers only
- `seqid` - Sequence identifiers
- `ft` - Feature table

### Protein (`protein`)
- `fasta` - FASTA format sequences  
- `gp` - GenPept flat file format
- `ipg` - Identical protein groups
- `acc` - Accession numbers

### Gene (`gene`)
- `gene_table` - Gene table format
- `asn.1` - ASN.1 format
- `xml` - XML format

### Structure (`structure`)
- `pdb` - PDB format
- `mmdb` - MMDB ASN.1
- `docsum` - Document summary

## Retrieval Modes

| Mode | Description | Use With |
|------|-------------|----------|
| `xml` | XML format (default) | Most databases |
| `json` | JSON format | Limited databases |
| `text` | Plain text | FASTA, flat files |
| `html` | HTML format | Web display |
| `asn.1` | ASN.1 binary | Structured data |

---

**Next:** [Extended APIs](extended-apis.md) | [Parsers & Converters](parsers.md)
