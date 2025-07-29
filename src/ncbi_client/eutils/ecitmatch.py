"""
ECitMatch - Citation matching for PubMed.

Based on NCBI E-utilities documentation:
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/ecitmatch.cgi
"""

from typing import List, Dict, Any

from ncbi_client.core.exceptions import ValidationError


class ECitMatch:
    """
    Interface to NCBI ECitMatch utility.
    
    ECitMatch matches citation strings to PubMed IDs.
    """
    
    def __init__(self, client):
        """Initialize with reference to main client."""
        self.client = client
    
    def citation_match(
        self,
        citations: List[str],
        retmode: str = 'xml',
        **kwargs
    ) -> str:
        """
        Match citations to PubMed IDs.
        
        Args:
            citations: List of citation strings in format:
                      journal_title|year|volume|first_page|author_name|your_key|
            retmode: Return mode ('xml' or 'text')
            **kwargs: Additional parameters
            
        Returns:
            Response text containing matched citations with PMIDs
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate parameters
        if not citations:
            raise ValidationError("Citation list cannot be empty")
        
        # Validate citation format
        for i, citation in enumerate(citations):
            if citation.count('|') < 5:
                raise ValidationError(
                    f"Citation {i+1} has invalid format. "
                    "Expected: journal|year|volume|page|author|key|"
                )
        
        # Build parameters
        params = {
            'db': 'pubmed',
            'retmode': retmode,
            'bdata': '%0D'.join(citations)  # Join with carriage return
        }
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Make request
        response = self.client.request('ecitmatch.cgi', **params)
        return response
    
    def match_single_citation(
        self,
        journal: str,
        year: str,
        volume: str,
        page: str,
        author: str,
        key: str = "",
        retmode: str = 'xml'
    ) -> str:
        """
        Match a single citation to PubMed ID.
        
        Args:
            journal: Journal title
            year: Publication year
            volume: Volume number
            page: First page number
            author: Author name (last name, first initials)
            key: User-defined key for tracking
            retmode: Return mode
            
        Returns:
            Response text containing matched citation with PMID
        """
        citation = f"{journal}|{year}|{volume}|{page}|{author}|{key}|"
        return self.citation_match([citation], retmode=retmode)
    
    def parse_citation_results(self, result_text: str) -> List[Dict[str, str]]:
        """
        Parse citation matching results.
        
        Args:
            result_text: Raw result text from ECitMatch
            
        Returns:
            List of dictionaries containing citation data and PMIDs
        """
        results = []
        
        for line in result_text.strip().split('\n'):
            if line.strip():
                parts = line.split('|')
                if len(parts) >= 7:  # Should have 6 original parts + PMID
                    result = {
                        'journal': parts[0],
                        'year': parts[1],
                        'volume': parts[2],
                        'page': parts[3],
                        'author': parts[4],
                        'key': parts[5],
                        'pmid': parts[6] if parts[6] else None
                    }
                    results.append(result)
        
        return results
