# Installation Guide

## System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, Linux
- **Memory**: 512MB RAM minimum (more for large datasets)
- **Network**: Internet connection for API access

## Installation Methods

### Standard Installation

Clone the repository and install in development mode:

```bash
# Clone the repository
git clone https://github.com/yourusername/ncbi-client.git
cd ncbi-client

# Install in development mode
pip install -e .
```

### Feature-Specific Installation

Install only the features you need:

```bash
# Core functionality only (no external dependencies)
pip install -e .

# With command-line interface
pip install -e .[cli]

# With data analysis tools
pip install -e .[data]

# With bioinformatics tools
pip install -e .[bio]

# With development tools
pip install -e .[dev]

# All features
pip install -e .[all]
```

### Virtual Environment (Recommended)

Use a virtual environment to avoid conflicts:

```bash
# Create virtual environment
python -m venv ncbi-env

# Activate virtual environment
# On Windows:
ncbi-env\Scripts\activate
# On macOS/Linux:
source ncbi-env/bin/activate

# Install NCBI Client
pip install -e .[all]
```

### Docker Installation

Use Docker for containerized deployment:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install -e .[all]

CMD ["python", "examples/simple_cli.py", "--help"]
```

```bash
# Build and run
docker build -t ncbi-client .
docker run ncbi-client
```

## Dependency Details

### Core Dependencies (Required)
- **Python 3.7+**: Core language requirement
- **Standard Library**: urllib, json, xml, ssl, etc.

### Optional Dependencies

#### CLI Features (`[cli]`)
- **click >= 8.0**: Full-featured command-line interface
- **colorama**: Cross-platform colored terminal output

#### Data Analysis (`[data]`)
- **pandas >= 1.0**: Data manipulation and analysis
- **numpy >= 1.18**: Numerical computing
- **matplotlib >= 3.0**: Data visualization
- **scipy**: Scientific computing

#### Bioinformatics (`[bio]`)
- **biopython >= 1.78**: Biological data processing
- **pyfaidx**: FASTA file indexing
- **bioservices**: Additional bioinformatics services

#### Development (`[dev]`)
- **pytest >= 6.0**: Testing framework
- **pytest-cov**: Coverage reporting
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code linting
- **mypy**: Type checking
- **pre-commit**: Git hooks

## Verification

Verify your installation works correctly:

```python
# Test basic functionality
python -c "
import ncbi_client
client = ncbi_client.NCBIClient(email='test@example.com')
print('NCBI Client installed successfully!')
print(f'Version: {ncbi_client.__version__}')
"
```

```bash
# Test CLI functionality
python examples/simple_cli.py --help

# Test a simple search (with internet connection)
python examples/simple_cli.py search pubmed "aspirin" --retmax 1
```

## API Key Setup (Optional but Recommended)

### Get an API Key

1. Visit [NCBI API Key Registration](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)
2. Follow the registration process
3. Save your API key securely

### Configure API Key

#### Method 1: Environment Variables (Recommended)
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export NCBI_API_KEY="your_api_key_here"
export NCBI_EMAIL="your.email@example.com"
export NCBI_TOOL="your_tool_name"

# Reload your shell or run:
source ~/.bashrc  # or ~/.zshrc
```

#### Method 2: Configuration File
```python
# Create ~/.ncbi_config.py
NCBI_API_KEY = "your_api_key_here"
NCBI_EMAIL = "your.email@example.com"
NCBI_TOOL = "your_tool_name"
```

#### Method 3: Direct in Code
```python
from ncbi_client import NCBIClient

client = NCBIClient(
    api_key="your_api_key_here",
    email="your.email@example.com",
    tool="your_tool_name"
)
```

## Corporate/Firewall Setup

### SSL Certificate Issues

If you encounter SSL certificate verification errors:

```python
# Disable SSL verification (not recommended for production)
client = NCBIClient(
    email="your@email.com",
    verify_ssl=False
)
```

```bash
# CLI usage with SSL bypass
python examples/simple_cli.py --no-ssl-verify search pubmed "query"
```

### Proxy Configuration

For corporate proxies:

```python
import os

# Set proxy environment variables
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'https://proxy.company.com:8080'

# Use the client normally
client = NCBIClient(email="your@email.com")
```

## Troubleshooting

### Common Issues

#### Import Error
```
ImportError: No module named 'ncbi_client'
```
**Solution**: Ensure you're in the correct virtual environment and have installed the package:
```bash
pip install -e .
```

#### SSL Certificate Error
```
SSL: CERTIFICATE_VERIFY_FAILED
```
**Solution**: Use the `--no-ssl-verify` flag or disable SSL verification in code.

#### Rate Limiting
```
RateLimitError: Request rate exceeded
```
**Solution**: Get an API key or wait before retrying.

#### Network Timeouts
```
TimeoutError: Request timed out
```
**Solution**: Check internet connection or increase timeout settings.

### Getting Help

1. **Check Documentation**: Browse the [user guide](../user-guide/)
2. **Search Issues**: Look through [GitHub issues](https://github.com/yourusername/ncbi-client/issues)
3. **Ask Questions**: Use [GitHub discussions](https://github.com/yourusername/ncbi-client/discussions)
4. **Contact Support**: Email maintainers for sensitive issues

## Next Steps

After installation:

1. **Read the [Quick Start Guide](quick-start.md)** for basic usage
2. **Explore [Examples](../examples/)** for real-world use cases
3. **Check [CLI Guide](cli.md)** for command-line usage
4. **Review [API Reference](../api-reference/)** for detailed documentation

---

**Need help?** Check our [troubleshooting guide](error-handling.md) or [open an issue](https://github.com/yourusername/ncbi-client/issues).
