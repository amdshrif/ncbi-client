# NCBI Client Documentation

Welcome to the comprehensive documentation for NCBI Client - a modern Python library for accessing NCBI databases and services.

## 📚 Documentation Structure

### 🚀 [Getting Started](user-guide/installation.md)
- [Installation Guide](user-guide/installation.md)
- [Quick Start](user-guide/quick-start.md)
- [Configuration](user-guide/configuration.md)

### 📖 [User Guide](user-guide/)
- [Basic Usage](user-guide/basic-usage.md)
- [E-utilities Overview](user-guide/eutils-overview.md)
- [Command Line Interface](user-guide/cli.md)
- [Data Processing](user-guide/data-processing.md)
- [Caching & Performance](user-guide/performance.md)
- [Error Handling](user-guide/error-handling.md)
- [SSL & Security](user-guide/ssl-security.md)

### 🎯 [Tutorials](tutorials/)
- [Literature Search](tutorials/literature-search.md)
- [Sequence Analysis](tutorials/sequence-analysis.md)
- [Chemical Compounds](tutorials/chemical-compounds.md)
- [Batch Processing](tutorials/batch-processing.md)
- [Integration Examples](tutorials/integration.md)

### 📝 [API Reference](api-reference/)
- [Core Client](api-reference/core.md)
- [E-utilities](api-reference/eutils.md)
- [Extended APIs](api-reference/extended-apis.md)
- [Parsers & Converters](api-reference/parsers.md)
- [Utilities](api-reference/utilities.md)
- [Exceptions](api-reference/exceptions.md)

### 💡 [Examples](examples/)
- [Research Use Cases](examples/research-examples.md)
- [Web Applications](examples/web-apps.md)
- [Data Analysis](examples/data-analysis.md)
- [Custom Workflows](examples/workflows.md)

### 🛠️ [Developer Guide](developer/)
- [Contributing](developer/contributing.md)
- [Testing](developer/testing.md)
- [Building Documentation](developer/documentation.md)
- [Release Process](developer/releases.md)

## 🔗 Quick Links

| Resource | Description |
|----------|-------------|
| [Installation](user-guide/installation.md) | Get up and running quickly |
| [Quick Start](user-guide/quick-start.md) | Basic usage in 5 minutes |
| [CLI Guide](user-guide/cli.md) | Command-line interface |
| [API Reference](api-reference/) | Complete API documentation |
| [Examples](examples/) | Real-world usage examples |
| [Troubleshooting](user-guide/error-handling.md) | Common issues and solutions |

## 🌟 Features Overview

### Core E-utilities
- ✅ **Complete E-utilities Support**: All 9 NCBI E-utilities
- ✅ **Rate Limiting**: Automatic rate limiting with API key support
- ✅ **History Server**: Efficient large dataset handling
- ✅ **Multiple Formats**: XML, JSON, FASTA, GenBank, and more

### Extended APIs
- ✅ **NCBI Datasets**: Genome assemblies and annotations
- ✅ **PubChem**: Chemical compound data
- ✅ **Advanced Parsers**: Data extraction and conversion tools

### Developer Experience
- ✅ **Type Hints**: Full type annotation support
- ✅ **CLI Tools**: Both full-featured and zero-dependency options
- ✅ **Caching**: SQLite and memory-based caching
- ✅ **SSL Support**: Corporate firewall compatibility

## 🎯 Common Tasks

### Search Literature
```python
from ncbi_client import NCBIClient

client = NCBIClient(email="your@email.com")
results = client.esearch.search(
    db="pubmed",
    term="COVID-19 vaccine",
    retmax=100
)
```

### Fetch Sequences
```python
sequences = client.efetch.fetch(
    db="nucleotide",
    id_list=["NM_000518"],
    rettype="fasta",
    retmode="text"
)
```

### Use Command Line
```bash
# Search PubMed
python examples/simple_cli.py search pubmed "diabetes" --retmax 20

# Fetch abstracts
python examples/simple_cli.py fetch pubmed "123,456" --rettype abstract
```

## 📊 Supported Databases

| Category | Databases |
|----------|-----------|
| **Literature** | pubmed, pmc, books |
| **Sequences** | nucleotide, protein, genome |
| **Structures** | structure, pccompound |
| **Genes** | gene, homologene, snp |
| **Clinical** | clinvar, medgen, omim |

## 🆘 Need Help?

- 📖 **Documentation**: Browse the guides and tutorials
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/ncbi-client/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/ncbi-client/discussions)
- 📧 **Email**: Contact maintainers for sensitive issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Last Updated**: July 28, 2025  
**Version**: 1.0.0
