"""
NCBI E-utilities Python client.

A comprehensive Python client for accessing NCBI databases through the E-utilities API.
"""

from ncbi_client.core.base_client import NCBIClient
from ncbi_client.core.exceptions import NCBIError, AuthenticationError, RateLimitError, APIError
from ncbi_client.core.rate_limiter import RateLimiter

# E-utilities
from ncbi_client.eutils import (
    ESearch, EFetch, EPost, ESummary, ELink, 
    EInfo, EGQuery, ESpell, ECitMatch
)

# Parsers and converters
from ncbi_client.parsers import XMLParser, JSONParser, FASTAParser, GenBankParser
from ncbi_client.converters import FormatConverter, SequenceTools

# Additional APIs
from ncbi_client.datasets import DatasetsAPI, GenomeAssembly, Gene
from ncbi_client.pubchem import PubChemAPI, Compound, Assay

# Utilities
from ncbi_client.utils import (
    HistoryManager, CacheManager, SQLiteCache, MemoryCache,
    ValidationHelpers, FormatHelpers, XMLHelpers, URLHelpers, 
    DataHelpers, DateHelpers, ErrorHelpers
)

__version__ = "1.0.0"

__all__ = [
    # Core
    'NCBIClient', 'NCBIError', 'AuthenticationError', 'RateLimitError', 'APIError', 'RateLimiter',
    
    # E-utilities
    'ESearch', 'EFetch', 'EPost', 'ESummary', 'ELink', 'EInfo', 'EGQuery', 'ESpell', 'ECitMatch',
    
    # Parsers and converters
    'XMLParser', 'JSONParser', 'FASTAParser', 'GenBankParser', 'FormatConverter', 'SequenceTools',
    
    # Additional APIs
    'DatasetsAPI', 'GenomeAssembly', 'Gene', 'PubChemAPI', 'Compound', 'Assay',
    
    # Utilities
    'HistoryManager', 'CacheManager', 'SQLiteCache', 'MemoryCache',
    'ValidationHelpers', 'FormatHelpers', 'XMLHelpers', 'URLHelpers', 
    'DataHelpers', 'DateHelpers', 'ErrorHelpers'
]
