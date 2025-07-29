# Documentation Build Configuration

This directory contains the complete documentation for NCBI Client.

## Building Documentation

### Prerequisites

```bash
# Install documentation dependencies
pip install -e .[docs]

# Or install manually
pip install sphinx sphinx-rtd-theme myst-parser
```

### Build HTML Documentation

```bash
# From the docs directory
cd docs
make html

# Or using sphinx directly
sphinx-build -b html . _build/html
```

### Build PDF Documentation

```bash
# Install LaTeX dependencies first
# On Ubuntu: sudo apt-get install texlive-latex-recommended texlive-fonts-recommended
# On macOS: brew install mactex

# Build PDF
make latexpdf
```

### Live Development Server

```bash
# Install sphinx-autobuild
pip install sphinx-autobuild

# Start live server
sphinx-autobuild . _build/html --open-browser
```

## Documentation Structure

```
docs/
├── conf.py                  # Sphinx configuration
├── index.rst               # Main index (generated from README.md)
├── Makefile                 # Build commands
├── requirements.txt         # Documentation dependencies
├── _static/                 # Static files (CSS, images)
├── _templates/              # Custom templates
├── user-guide/             # User documentation
├── api-reference/          # API documentation  
├── tutorials/              # Step-by-step guides
├── examples/               # Code examples
└── developer/              # Developer documentation
```

## Writing Documentation

### Markdown Files

Most documentation is written in Markdown and converted using MyST parser:

```markdown
# Page Title

## Section

Content here with [links](other-page.md) and `code`.

```python
# Code blocks with syntax highlighting
from ncbi_client import NCBIClient
client = NCBIClient(email="test@example.com")
```

### Cross-References

Link between documentation pages:

```markdown
# Link to other pages
See the [installation guide](user-guide/installation.md)

# Link to specific sections
Check the [API reference](api-reference/core.md#ncbiclient)
```

### Code Examples

Include working code examples:

```markdown
```python
# Always test your code examples
from ncbi_client import NCBIClient

client = NCBIClient(email="your@email.com")
results = client.esearch.search(db="pubmed", term="test")
print(f"Found {results['count']} results")
```

### Admonitions

Use note boxes for important information:

```markdown
```{note}
This is important information for users.
```

```{warning}
This warns about potential issues.
```

```{tip}
This provides helpful tips.
```

## API Documentation

### Auto-Generated Documentation

API documentation is generated from docstrings:

```python
def search(self, db: str, term: str, **kwargs) -> Dict[str, Any]:
    """Search NCBI database for records.
    
    Args:
        db: Database name (e.g., 'pubmed', 'nucleotide')
        term: Search query string
        **kwargs: Additional search parameters
        
    Returns:
        Dictionary containing search results with keys:
        - count: Total number of matches
        - id_list: List of matching record IDs
        - query_translation: How NCBI interpreted the query
        
    Raises:
        ValidationError: If database name is invalid
        APIError: If NCBI API returns an error
        
    Example:
        >>> client = NCBIClient(email="test@example.com")
        >>> results = client.esearch.search("pubmed", "cancer")
        >>> print(f"Found {results['count']} articles")
    """
```

### Manual API Pages

Create detailed API pages in `api-reference/`:

```markdown
# ESearch API

## Overview

The ESearch service searches for records in NCBI databases.

## Methods

### search(db, term, **kwargs)

Search for records matching a query.

**Parameters:**
- `db` (str): Database name
- `term` (str): Search query

**Example:**
```python
results = client.esearch.search("pubmed", "COVID-19")
```
```

## Testing Documentation

### Test Code Examples

All code examples should be tested:

```python
# tests/test_docs.py
import doctest
import importlib.util

def test_documentation_examples():
    """Test code examples in documentation."""
    # Test code blocks in markdown files
    pass

def test_docstring_examples():
    """Test examples in docstrings."""
    import ncbi_client
    doctest.testmod(ncbi_client)
```

### Link Checking

Check for broken links:

```bash
# Install linkchecker
pip install linkchecker

# Check documentation links
linkchecker _build/html/
```

## Deployment

### GitHub Pages

Documentation is automatically deployed to GitHub Pages:

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -e .[docs]
      
      - name: Build documentation
        run: |
          cd docs
          make html
      
      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/_build/html
```

### ReadTheDocs

Alternative deployment to ReadTheDocs:

```yaml
# .readthedocs.yml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.9"

python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs

sphinx:
  configuration: docs/conf.py
```

## Maintenance

### Regular Tasks

1. **Update examples** when API changes
2. **Check links** for broken references  
3. **Review user feedback** and improve clarity
4. **Update screenshots** when UI changes
5. **Add new features** to documentation

### Version Updates

When releasing new versions:

1. Update version numbers in examples
2. Add new features to API reference
3. Update changelog
4. Review and update getting started guide

### Community Contributions

Encourage community contributions:

1. Mark documentation issues as `good first issue`
2. Provide templates for new documentation
3. Review and merge documentation PRs quickly
4. Thank contributors in release notes

---

**Questions?** Check the [contributing guide](developer/contributing.md) or open an issue.
