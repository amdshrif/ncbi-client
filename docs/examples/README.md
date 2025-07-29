# Examples Index

Real-world examples and use cases for NCBI Client.

## Research Examples

### Literature Analysis
- [Publication Trend Analysis](research-examples.md#publication-trends)
- [Citation Network Analysis](research-examples.md#citation-networks)
- [Journal Impact Assessment](research-examples.md#journal-analysis)
- [Author Collaboration Networks](research-examples.md#author-networks)

### Sequence Analysis
- [Gene Family Analysis](research-examples.md#gene-families)
- [Phylogenetic Studies](research-examples.md#phylogenetics)
- [Comparative Genomics](research-examples.md#comparative-genomics)
- [Protein Structure Prediction](research-examples.md#protein-structure)

### Clinical Research
- [Clinical Trial Discovery](research-examples.md#clinical-trials)
- [Drug Target Identification](research-examples.md#drug-targets)
- [Disease Association Studies](research-examples.md#disease-associations)
- [Biomarker Research](research-examples.md#biomarkers)

## Web Applications

### Flask Applications
- [PubMed Search API](web-apps.md#flask-api)
- [Literature Dashboard](web-apps.md#dashboard)
- [Citation Manager](web-apps.md#citation-manager)

### Django Integration
- [Research Database](web-apps.md#django-database)
- [User Management](web-apps.md#user-system)
- [Data Visualization](web-apps.md#visualization)

### FastAPI Services
- [Microservices Architecture](web-apps.md#microservices)
- [Real-time Updates](web-apps.md#realtime)
- [API Gateway](web-apps.md#gateway)

## Data Analysis

### Jupyter Notebooks
- [Exploratory Data Analysis](data-analysis.md#eda)
- [Statistical Analysis](data-analysis.md#statistics)
- [Machine Learning](data-analysis.md#ml)
- [Visualization Techniques](data-analysis.md#visualization)

### Pandas Integration
- [Data Cleaning](data-analysis.md#cleaning)
- [Time Series Analysis](data-analysis.md#timeseries)
- [Correlation Studies](data-analysis.md#correlation)

### Scientific Computing
- [NumPy Integration](data-analysis.md#numpy)
- [SciPy Analysis](data-analysis.md#scipy)
- [Matplotlib Plotting](data-analysis.md#matplotlib)

## Workflow Automation

### Batch Processing
- [Large Dataset Processing](workflows.md#batch-processing)
- [Automated Updates](workflows.md#automation)
- [Data Pipeline](workflows.md#pipelines)

### CI/CD Integration
- [GitHub Actions](workflows.md#github-actions)
- [Docker Containers](workflows.md#docker)
- [Cloud Deployment](workflows.md#cloud)

### Monitoring & Alerts
- [Error Handling](workflows.md#error-handling)
- [Performance Monitoring](workflows.md#monitoring)
- [Alert Systems](workflows.md#alerts)

## Educational Use Cases

### Teaching Materials
- [Bioinformatics Courses](educational.md#bioinformatics)
- [Data Science Projects](educational.md#datascience)
- [Research Methods](educational.md#research-methods)

### Student Projects
- [Literature Reviews](educational.md#literature-reviews)
- [Database Queries](educational.md#database-queries)
- [Data Visualization](educational.md#visualization-projects)

## Integration Examples

### Other Libraries
- [BioPython Integration](integration.md#biopython)
- [Pandas Workflows](integration.md#pandas)
- [Matplotlib Visualization](integration.md#matplotlib)
- [Seaborn Plotting](integration.md#seaborn)

### External APIs
- [CrossRef Integration](integration.md#crossref)
- [ORCID Lookup](integration.md#orcid)
- [DOI Resolution](integration.md#doi)

### Database Systems
- [PostgreSQL Storage](integration.md#postgresql)
- [MongoDB Documents](integration.md#mongodb)
- [SQLite Local Storage](integration.md#sqlite)

## Performance Examples

### Optimization Techniques
- [Caching Strategies](performance.md#caching)
- [Batch Operations](performance.md#batching)
- [Memory Management](performance.md#memory)

### Parallel Processing
- [Multiprocessing](performance.md#multiprocessing)
- [Async/Await](performance.md#async)
- [Thread Pools](performance.md#threading)

## Quick Start Examples

### 5-Minute Examples
```python
# Literature search
from ncbi_client import NCBIClient
client = NCBIClient(email="your@email.com")
results = client.esearch.search(db="pubmed", term="COVID-19", retmax=10)
```

```python
# Sequence retrieval
sequences = client.efetch.fetch(
    db="nucleotide", 
    id_list=["NM_000518"], 
    rettype="fasta"
)
```

```python
# Chemical compounds
from ncbi_client import PubChemAPI
pubchem = PubChemAPI()
compounds = pubchem.search_compounds("aspirin", "name")
```

### Command Line Examples
```bash
# Quick search
python examples/simple_cli.py search pubmed "diabetes" --retmax 5

# Fetch abstracts
python examples/simple_cli.py fetch pubmed "12345,67890" --rettype abstract
```

## Browse by Category

| Category | Examples | Complexity |
|----------|----------|------------|
| **Beginner** | [Quick Start](../user-guide/quick-start.md) | ⭐ |
| **Literature** | [Literature Search](../tutorials/literature-search.md) | ⭐⭐ |
| **Sequences** | [Sequence Analysis](../tutorials/sequence-analysis.md) | ⭐⭐ |
| **Web Apps** | [Flask Integration](web-apps.md) | ⭐⭐⭐ |
| **Data Science** | [Analysis Examples](data-analysis.md) | ⭐⭐⭐ |
| **Advanced** | [Custom Workflows](workflows.md) | ⭐⭐⭐⭐ |

## Contributing Examples

Have a great example to share? See our [contribution guidelines](../developer/contributing.md) for how to add your examples to this collection.

---

**Need help?** Check the [API Reference](../api-reference/) or [User Guide](../user-guide/)
