"""
Datasets package for NCBI Datasets API integration.
"""

from ncbi_client.datasets.datasets_api import DatasetsAPI, GenomeAssembly, Gene

__all__ = ['DatasetsAPI', 'GenomeAssembly', 'Gene']
