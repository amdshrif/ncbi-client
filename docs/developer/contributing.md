# Contributing to NCBI Client

Thank you for your interest in contributing to NCBI Client! This guide will help you get started with contributing code, documentation, examples, and more.

## 🚀 Quick Start for Contributors

### 1. Set Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/ncbi-client.git
cd ncbi-client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e .[dev,cli,data,bio,all]

# Install pre-commit hooks
pre-commit install
```

### 2. Verify Installation

```bash
# Run tests to ensure everything works
python -m pytest

# Check code style
black --check ncbi_client/
isort --check-only ncbi_client/
flake8 ncbi_client/
mypy ncbi_client/

# Test CLI functionality
python examples/simple_cli.py --help
```

## 📋 Types of Contributions

### 🐛 Bug Reports
- Use clear, descriptive titles
- Include steps to reproduce
- Provide system information
- Add relevant error messages

### ✨ Feature Requests
- Describe the problem you're solving
- Explain your proposed solution
- Consider backward compatibility
- Provide use cases

### 🔧 Code Contributions
- Follow coding standards
- Add tests for new features
- Update documentation
- Keep changes focused

### 📚 Documentation
- Fix typos and grammar
- Add examples and tutorials
- Improve API documentation
- Translate to other languages

### 🧪 Testing
- Add test cases
- Improve test coverage
- Test on different platforms
- Performance testing

## 🛠️ Development Workflow

### 1. Create a Branch

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/issue-description
```

### 2. Make Changes

```bash
# Write your code
# Add tests
# Update documentation

# Run tests frequently
python -m pytest tests/

# Check your changes
black ncbi_client/
isort ncbi_client/
flake8 ncbi_client/
```

### 3. Commit Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of what you added"
```

### 4. Submit Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Fill out the pull request template
# Link to related issues
```

## 📏 Coding Standards

### Code Style

We use:
- **Black** for code formatting (line length: 88)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black ncbi_client/
isort ncbi_client/

# Check style
flake8 ncbi_client/
mypy ncbi_client/
```

### Type Hints

All public functions should have type hints:

```python
from typing import Dict, List, Optional, Any

def search_database(
    db: str, 
    term: str, 
    retmax: int = 20
) -> Dict[str, Any]:
    """Search NCBI database."""
    # Implementation here
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def fetch_records(
    db: str, 
    id_list: List[str], 
    rettype: str = "docsum"
) -> str:
    """Fetch records from NCBI database.
    
    Args:
        db: Database name (e.g., 'pubmed', 'nucleotide')
        id_list: List of record IDs to fetch
        rettype: Retrieval type for the data
        
    Returns:
        Raw response data as string
        
    Raises:
        ValidationError: If parameters are invalid
        APIError: If NCBI API returns an error
        
    Example:
        >>> client = NCBIClient(email="test@example.com")
        >>> records = client.efetch.fetch(
        ...     db="pubmed", 
        ...     id_list=["12345"], 
        ...     rettype="abstract"
        ... )
    """
```

### Error Handling

Create specific exceptions and handle errors gracefully:

```python
from ncbi_client.core.exceptions import NCBIError, ValidationError

def validate_database(db: str) -> None:
    """Validate database name."""
    valid_dbs = ["pubmed", "nucleotide", "protein"]
    if db not in valid_dbs:
        raise ValidationError(f"Invalid database: {db}")

try:
    result = some_operation()
except requests.RequestException as e:
    raise NCBIError(f"Network error: {e}") from e
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration
├── test_core/               # Core functionality tests
│   ├── test_client.py
│   └── test_exceptions.py
├── test_eutils/             # E-utilities tests
│   ├── test_esearch.py
│   ├── test_efetch.py
│   └── test_esummary.py
├── test_parsers/            # Parser tests
├── test_cli/                # CLI tests
└── integration/             # Integration tests
```

### Writing Tests

Use pytest with fixtures:

```python
import pytest
from ncbi_client import NCBIClient
from ncbi_client.core.exceptions import ValidationError

@pytest.fixture
def client():
    """Create test client."""
    return NCBIClient(email="test@example.com")

def test_search_basic(client):
    """Test basic search functionality."""
    results = client.esearch.search(
        db="pubmed", 
        term="aspirin", 
        retmax=5
    )
    
    assert "count" in results
    assert "id_list" in results
    assert len(results["id_list"]) <= 5

def test_invalid_database(client):
    """Test error handling for invalid database."""
    with pytest.raises(ValidationError, match="Invalid database"):
        client.esearch.search(db="invalid_db", term="test")

@pytest.mark.integration
def test_large_search(client):
    """Integration test for large searches."""
    # Test with real API calls
    pass
```

### Test Categories

Use pytest markers:

```python
# Unit tests (fast, no network)
@pytest.mark.unit
def test_url_building():
    pass

# Integration tests (require network)
@pytest.mark.integration  
def test_api_integration():
    pass

# Slow tests
@pytest.mark.slow
def test_large_dataset():
    pass
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_esearch.py

# Run with coverage
python -m pytest --cov=ncbi_client --cov-report=html

# Run only unit tests
python -m pytest -m unit

# Run integration tests
python -m pytest -m integration
```

## 📖 Documentation Guidelines

### Documentation Structure

```
docs/
├── README.md                # Main documentation index
├── user-guide/              # User documentation
│   ├── installation.md
│   ├── quick-start.md
│   └── cli.md
├── api-reference/           # API documentation
├── tutorials/               # Step-by-step guides
├── examples/                # Code examples
└── developer/               # Developer documentation
```

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add cross-references
- Test all code examples
- Update table of contents

### Building Documentation

```bash
# Install documentation dependencies
pip install -e .[docs]

# Build HTML documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## 🔄 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Release Checklist

1. **Update Version**
   ```python
   # In ncbi_client/__init__.py
   __version__ = "1.2.3"
   ```

2. **Update Changelog**
   ```markdown
   # CHANGELOG.md
   ## [1.2.3] - 2024-01-15
   ### Added
   - New feature description
   ### Fixed
   - Bug fix description
   ```

3. **Run Full Test Suite**
   ```bash
   python -m pytest
   flake8 ncbi_client/
   mypy ncbi_client/
   ```

4. **Build Documentation**
   ```bash
   cd docs && make html
   ```

5. **Create Release**
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

6. **GitHub Actions will automatically:**
   - Run tests
   - Build packages
   - Publish to PyPI
   - Update documentation

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

### Communication

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions
- **Email**: Sensitive security issues

### Getting Help

1. **Search existing issues** first
2. **Check documentation** for answers
3. **Ask in discussions** for general questions
4. **Open an issue** for bugs or feature requests

## 📝 Pull Request Template

When submitting a pull request, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new features
- [ ] Updated documentation

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Meaningful commit messages
- [ ] Updated relevant documentation
```

## 🎯 Good First Issues

New contributors can start with:
- Documentation improvements
- Adding examples
- Writing tests
- Fixing typos
- Small feature additions

Look for issues labeled `good first issue` or `help wanted`.

## 🏆 Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Documentation credits
- GitHub contributor stats

## 📞 Contact

- **Maintainers**: Listed in MAINTAINERS.md
- **Security Issues**: security@example.com
- **General Questions**: GitHub Discussions

---

Thank you for contributing to NCBI Client! 🙏
