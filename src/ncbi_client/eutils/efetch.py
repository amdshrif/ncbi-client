"""
EFetch - Retrieve full records from NCBI databases.

Based on NCBI E-utilities documentation:
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
"""

from typing import List, Optional, Union, Dict, Any

from ncbi_client.core.exceptions import ValidationError


class EFetch:
    """
    Interface to NCBI EFetch utility.
    
    EFetch retrieves full records from NCBI databases in various formats.
    """
    
    # Database-specific format mappings from NCBI documentation
    VALID_FORMATS = {
        'pubmed': {
            'rettypes': ['abstract', 'citation', 'docsum', 'full', 'medline', 'uilist'],
            'retmodes': ['xml', 'text', 'asn.1']
        },
        'protein': {
            'rettypes': ['fasta', 'seqid', 'acc', 'gb', 'gp', 'docsum', 'uilist'],
            'retmodes': ['xml', 'text', 'asn.1']
        },
        'nucleotide': {
            'rettypes': ['fasta', 'seqid', 'acc', 'gb', 'docsum', 'uilist'],
            'retmodes': ['xml', 'text', 'asn.1']
        },
        'nuccore': {
            'rettypes': ['fasta', 'seqid', 'acc', 'gb', 'docsum', 'uilist'],
            'retmodes': ['xml', 'text', 'asn.1']
        },
        'gene': {
            'rettypes': ['gene_table', 'docsum', 'uilist'],
            'retmodes': ['xml', 'text', 'asn.1']
        }
    }
    
    def __init__(self, client):
        """Initialize with reference to main client."""
        self.client = client
    
    def fetch(
        self,
        db: str,
        id_list: Optional[List[Union[str, int]]] = None,
        rettype: str = 'docsum',
        retmode: str = 'xml',
        retstart: int = 0,
        retmax: Optional[int] = None,
        webenv: Optional[str] = None,
        query_key: Optional[int] = None,
        strand: Optional[int] = None,
        seq_start: Optional[int] = None,
        seq_stop: Optional[int] = None,
        complexity: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Fetch records from NCBI database.
        
        Args:
            db: Database name
            id_list: List of UIDs to fetch
            rettype: Retrieval type (format)
            retmode: Retrieval mode (xml, text, asn.1)
            retstart: Starting record index
            retmax: Maximum number of records to fetch
            webenv: Web environment from previous search
            query_key: Query key from previous search
            strand: DNA strand (1=plus, 2=minus)
            seq_start: Starting sequence position
            seq_stop: Ending sequence position
            complexity: Sequence complexity level
            **kwargs: Additional parameters
            
        Returns:
            Response text in requested format
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate parameters
        self._validate_fetch_params(db, id_list, webenv, query_key, rettype, retmode)
        
        # Build parameters
        params = {
            'db': db,
            'rettype': rettype,
            'retmode': retmode
        }
        
        # Add ID list or history parameters
        if id_list:
            if isinstance(id_list, (list, tuple)):
                params['id'] = ','.join(str(uid) for uid in id_list)
            else:
                params['id'] = str(id_list)
        
        if webenv:
            params['WebEnv'] = webenv
        if query_key is not None:
            params['query_key'] = query_key
        
        # Add pagination parameters
        if retstart > 0:
            params['retstart'] = retstart
        if retmax is not None:
            params['retmax'] = retmax
        
        # Add sequence-specific parameters
        if strand is not None:
            params['strand'] = strand
        if seq_start is not None:
            params['seq_start'] = seq_start
        if seq_stop is not None:
            params['seq_stop'] = seq_stop
        if complexity is not None:
            params['complexity'] = complexity
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Make request
        response = self.client.request('efetch.fcgi', **params)
        return response
    
    def fetch_by_ids(
        self,
        db: str,
        ids: List[Union[str, int]],
        rettype: str = 'docsum',
        retmode: str = 'xml',
        **kwargs
    ) -> str:
        """
        Fetch records by ID list.
        
        Args:
            db: Database name
            ids: List of UIDs
            rettype: Retrieval type
            retmode: Retrieval mode
            **kwargs: Additional parameters
            
        Returns:
            Response text in requested format
        """
        return self.fetch(db=db, id_list=ids, rettype=rettype, retmode=retmode, **kwargs)
    
    def fetch_from_history(
        self,
        db: str,
        webenv: str,
        query_key: int,
        rettype: str = 'docsum',
        retmode: str = 'xml',
        **kwargs
    ) -> str:
        """
        Fetch records from history server.
        
        Args:
            db: Database name
            webenv: Web environment
            query_key: Query key
            rettype: Retrieval type
            retmode: Retrieval mode
            **kwargs: Additional parameters
            
        Returns:
            Response text in requested format
        """
        return self.fetch(
            db=db,
            webenv=webenv,
            query_key=query_key,
            rettype=rettype,
            retmode=retmode,
            **kwargs
        )
    
    def fetch_large_dataset(
        self,
        db: str,
        webenv: str,
        query_key: int,
        batch_size: int = 500,
        rettype: str = 'docsum',
        retmode: str = 'xml',
        max_records: Optional[int] = None
    ) -> List[str]:
        """
        Fetch large dataset in batches.
        
        Args:
            db: Database name
            webenv: Web environment
            query_key: Query key
            batch_size: Number of records per batch
            rettype: Retrieval type
            retmode: Retrieval mode
            max_records: Maximum total records to fetch
            
        Returns:
            List of response texts (one per batch)
        """
        # First, get the total count
        search_result = self.client.esearch.search(
            db=db,
            term="#" + str(query_key),
            webenv=webenv,
            retmax=0  # Just get count
        )
        
        total_count = search_result['count']
        if max_records:
            total_count = min(total_count, max_records)
        
        # Fetch in batches
        results = []
        for start in range(0, total_count, batch_size):
            batch_max = min(batch_size, total_count - start)
            
            batch_result = self.fetch(
                db=db,
                webenv=webenv,
                query_key=query_key,
                retstart=start,
                retmax=batch_max,
                rettype=rettype,
                retmode=retmode
            )
            
            results.append(batch_result)
        
        return results
    
    def _validate_fetch_params(
        self,
        db: str,
        id_list: Optional[List],
        webenv: Optional[str],
        query_key: Optional[int],
        rettype: str,
        retmode: str
    ) -> None:
        """Validate fetch parameters."""
        if not db:
            raise ValidationError("Database (db) parameter is required")
        
        # Must have either ID list or history parameters
        if not id_list and not (webenv and query_key is not None):
            raise ValidationError("Must provide either id_list or webenv/query_key")
        
        # Validate format if known
        if db in self.VALID_FORMATS:
            db_formats = self.VALID_FORMATS[db]
            if rettype not in db_formats['rettypes']:
                raise ValidationError(
                    f"Invalid rettype '{rettype}' for database '{db}'. "
                    f"Valid options: {', '.join(db_formats['rettypes'])}"
                )
            if retmode not in db_formats['retmodes']:
                raise ValidationError(
                    f"Invalid retmode '{retmode}' for database '{db}'. "
                    f"Valid options: {', '.join(db_formats['retmodes'])}"
                )
