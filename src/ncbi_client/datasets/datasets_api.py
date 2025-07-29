"""
NCBI Datasets API integration.

Provides access to the NCBI Datasets API for genome assemblies, 
gene annotations, and other genomic data.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Optional, Any
from ncbi_client.core.base_client import NCBIClient
from ncbi_client.core.exceptions import NCBIError, APIError


class DatasetsAPI:
    """
    Interface to NCBI Datasets API.
    """
    
    BASE_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha"
    
    def __init__(self, ncbi_client: Optional[NCBIClient] = None):
        """
        Initialize Datasets API client.
        
        Args:
            ncbi_client: Optional NCBI client for rate limiting
        """
        self.ncbi_client = ncbi_client
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make API request with error handling.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            APIError: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"
        
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except urllib.error.HTTPError as e:
            raise APIError(f"Datasets API request failed: HTTP {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            raise APIError(f"Datasets API request failed: {e.reason}")
        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response: {e}")
    
    def search_genomes(self, taxon: str, filters: Optional[Dict] = None, 
                      page_size: int = 20) -> Dict[str, Any]:
        """
        Search for genome assemblies.
        
        Args:
            taxon: Taxonomic name or ID
            filters: Additional search filters
            page_size: Number of results per page
            
        Returns:
            Search results with genome assemblies
        """
        params = {
            'taxon': taxon,
            'page_size': page_size
        }
        
        if filters:
            params.update(filters)
        
        return self._make_request("genome", params)
    
    def get_genome_summary(self, accessions: List[str]) -> Dict[str, Any]:
        """
        Get summary information for genome assemblies.
        
        Args:
            accessions: List of assembly accessions
            
        Returns:
            Genome summary data
        """
        accession_list = ','.join(accessions)
        return self._make_request(f"genome/accession/{accession_list}")
    
    def download_genome(self, accessions: List[str], include_annotation: bool = False,
                       format_type: str = "fasta") -> Dict[str, Any]:
        """
        Get download package for genome assemblies.
        
        Args:
            accessions: List of assembly accessions
            include_annotation: Whether to include gene annotations
            format_type: Download format (fasta, gbff, etc.)
            
        Returns:
            Download package information
        """
        accession_list = ','.join(accessions)
        params = {
            'include_annotation_type': 'GENOME_GFF' if include_annotation else '',
            'filename': f"ncbi_dataset.{format_type}.zip"
        }
        
        return self._make_request(f"genome/accession/{accession_list}/download", params)
    
    def search_genes(self, gene_symbols: List[str], taxon: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for genes by symbol.
        
        Args:
            gene_symbols: List of gene symbols
            taxon: Optional taxonomic filter
            
        Returns:
            Gene search results
        """
        params = {
            'gene.symbol': ','.join(gene_symbols)
        }
        
        if taxon:
            params['taxon'] = taxon
        
        return self._make_request("gene", params)
    
    def get_gene_details(self, gene_ids: List[int]) -> Dict[str, Any]:
        """
        Get detailed information for genes.
        
        Args:
            gene_ids: List of Gene IDs
            
        Returns:
            Detailed gene information
        """
        gene_list = ','.join(map(str, gene_ids))
        return self._make_request(f"gene/id/{gene_list}")
    
    def search_virus_genomes(self, virus_name: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Search for viral genome assemblies.
        
        Args:
            virus_name: Virus name or taxon
            filters: Additional search filters
            
        Returns:
            Viral genome search results
        """
        params = {
            'taxon': virus_name,
            'filters.assembly_source': 'RefSeq'
        }
        
        if filters:
            params.update(filters)
        
        return self._make_request("virus/genome", params)
    
    def get_taxonomy_tree(self, taxon: str) -> Dict[str, Any]:
        """
        Get taxonomic hierarchy for organism.
        
        Args:
            taxon: Taxonomic name or ID
            
        Returns:
            Taxonomy tree data
        """
        params = {'taxon': taxon}
        return self._make_request("taxonomy", params)
    
    def get_assembly_reports(self, accessions: List[str]) -> Dict[str, Any]:
        """
        Get assembly reports for genomes.
        
        Args:
            accessions: List of assembly accessions
            
        Returns:
            Assembly report data
        """
        accession_list = ','.join(accessions)
        return self._make_request(f"genome/accession/{accession_list}/dataset_report")
    
    def search_protein_clusters(self, protein_name: str, taxon: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for protein clusters.
        
        Args:
            protein_name: Protein name or description
            taxon: Optional taxonomic filter
            
        Returns:
            Protein cluster search results
        """
        params = {'q': protein_name}
        
        if taxon:
            params['taxon'] = taxon
        
        return self._make_request("protein", params)


class GenomeAssembly:
    """
    Represents a genome assembly from NCBI Datasets.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize from API response data.
        
        Args:
            data: Assembly data from API
        """
        self.data = data
        self.accession = data.get('accession')
        self.organism = data.get('organism', {})
        self.assembly_info = data.get('assembly_info', {})
        self.assembly_stats = data.get('assembly_stats', {})
    
    @property
    def name(self) -> str:
        """Get assembly name."""
        return self.assembly_info.get('assembly_name', '')
    
    @property
    def level(self) -> str:
        """Get assembly level."""
        return self.assembly_info.get('assembly_level', '')
    
    @property
    def organism_name(self) -> str:
        """Get organism name."""
        return self.organism.get('organism_name', '')
    
    @property
    def tax_id(self) -> Optional[int]:
        """Get taxonomic ID."""
        return self.organism.get('tax_id')
    
    @property
    def total_sequence_length(self) -> Optional[int]:
        """Get total sequence length."""
        return self.assembly_stats.get('total_sequence_length')
    
    @property
    def contig_count(self) -> Optional[int]:
        """Get number of contigs."""
        return self.assembly_stats.get('number_of_contigs')
    
    @property
    def scaffold_count(self) -> Optional[int]:
        """Get number of scaffolds."""
        return self.assembly_stats.get('number_of_scaffolds')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'accession': self.accession,
            'name': self.name,
            'level': self.level,
            'organism_name': self.organism_name,
            'tax_id': self.tax_id,
            'total_length': self.total_sequence_length,
            'contig_count': self.contig_count,
            'scaffold_count': self.scaffold_count
        }


class Gene:
    """
    Represents a gene from NCBI Datasets.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize from API response data.
        
        Args:
            data: Gene data from API
        """
        self.data = data
        self.gene_id = data.get('gene_id')
        self.gene_info = data.get('gene', {})
        self.genomic_regions = data.get('genomic_regions', [])
    
    @property
    def symbol(self) -> str:
        """Get gene symbol."""
        return self.gene_info.get('symbol', '')
    
    @property
    def description(self) -> str:
        """Get gene description."""
        return self.gene_info.get('description', '')
    
    @property
    def type(self) -> str:
        """Get gene type."""
        return self.gene_info.get('type', '')
    
    @property
    def tax_id(self) -> Optional[int]:
        """Get taxonomic ID."""
        return self.gene_info.get('tax_id')
    
    @property
    def chromosomes(self) -> List[str]:
        """Get chromosomes where gene is located."""
        return [region.get('chromosome', '') for region in self.genomic_regions]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'gene_id': self.gene_id,
            'symbol': self.symbol,
            'description': self.description,
            'type': self.type,
            'tax_id': self.tax_id,
            'chromosomes': self.chromosomes
        }
