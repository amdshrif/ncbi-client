"""
ESearch - Search and retrieval of UIDs from NCBI databases.

Based on NCBI E-utilities documentation:
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union, Any

from ncbi_client.core.exceptions import ValidationError, ParseError


class ESearch:
    """
    Interface to NCBI ESearch utility.
    
    ESearch provides basic search functionality for NCBI databases,
    returning lists of UIDs that match the search criteria.
    """
    
    def __init__(self, client):
        """Initialize with reference to main client."""
        self.client = client
    
    def search(
        self,
        db: str,
        term: str,
        retmax: int = 20,
        retstart: int = 0,
        sort: Optional[str] = None,
        field: Optional[str] = None,
        reldate: Optional[int] = None,
        mindate: Optional[str] = None,
        maxdate: Optional[str] = None,
        datetype: str = "pdat",
        usehistory: bool = False,
        webenv: Optional[str] = None,
        query_key: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search an NCBI database.
        
        Args:
            db: Database to search (e.g., 'pubmed', 'protein', 'nucleotide')
            term: Search query
            retmax: Maximum number of UIDs to return (default 20, max 100000)
            retstart: Starting index for returned UIDs (default 0)
            sort: Sort order ('relevance', 'pub_date', 'author', etc.)
            field: Search field to limit search
            reldate: Number of days back to search
            mindate: Start date (YYYY/MM/DD format)
            maxdate: End date (YYYY/MM/DD format)
            datetype: Date type ('pdat', 'edat', 'mdat')
            usehistory: Store results on history server
            webenv: Web environment string from previous search
            query_key: Query key from previous search
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing search results
            
        Raises:
            ValidationError: If parameters are invalid
            ParseError: If response cannot be parsed
        """
        # Validate parameters
        self._validate_search_params(db, term, retmax, retstart)
        
        # Build parameters
        params = {
            'db': db,
            'term': term,
            'retmax': retmax,
            'retstart': retstart,
            'retmode': 'xml'
        }
        
        # Add optional parameters
        if sort:
            params['sort'] = sort
        if field:
            params['field'] = field
        if reldate:
            params['reldate'] = reldate
        if mindate:
            params['mindate'] = mindate
        if maxdate:
            params['maxdate'] = maxdate
        if datetype != 'pdat':
            params['datetype'] = datetype
        if usehistory:
            params['usehistory'] = 'y'
        if webenv:
            params['WebEnv'] = webenv
        if query_key:
            params['query_key'] = query_key
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Make request
        response = self.client.request('esearch.fcgi', **params)
        
        # Parse response
        return self._parse_search_response(response)
    
    def search_with_history(
        self,
        db: str,
        term: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search and store results on history server.
        
        This is a convenience method that sets usehistory=True.
        
        Args:
            db: Database to search
            term: Search query
            **kwargs: Additional search parameters
            
        Returns:
            Dictionary containing search results with WebEnv and QueryKey
        """
        return self.search(db=db, term=term, usehistory=True, **kwargs)
    
    def combine_searches(
        self,
        webenv: str,
        query_keys: List[int],
        operator: str = "AND"
    ) -> Dict[str, Any]:
        """
        Combine multiple search results using boolean operators.
        
        Args:
            webenv: Web environment containing the searches
            query_keys: List of query keys to combine
            operator: Boolean operator ("AND", "OR", "NOT")
            
        Returns:
            Dictionary containing combined search results
        """
        if len(query_keys) < 2:
            raise ValidationError("Need at least 2 query keys to combine")
        
        # Build combination query
        terms = [f"#{key}" for key in query_keys]
        combined_term = f" {operator} ".join(terms)
        
        return self.search(
            db="pubmed",  # Database doesn't matter for history combinations
            term=combined_term,
            webenv=webenv,
            usehistory=True
        )
    
    def _validate_search_params(
        self,
        db: str,
        term: str,
        retmax: int,
        retstart: int
    ) -> None:
        """Validate search parameters."""
        if not db:
            raise ValidationError("Database (db) parameter is required")
        if not term:
            raise ValidationError("Search term is required")
        if retmax < 1 or retmax > 100000:
            raise ValidationError("retmax must be between 1 and 100000")
        if retstart < 0:
            raise ValidationError("retstart must be >= 0")
    
    def _parse_search_response(self, xml_text: str) -> Dict[str, Any]:
        """
        Parse ESearch XML response.
        
        Args:
            xml_text: XML response text
            
        Returns:
            Parsed search results
            
        Raises:
            ParseError: If XML cannot be parsed
        """
        try:
            root = ET.fromstring(xml_text)
            
            # Check for errors
            error_list = root.find('ErrorList')
            if error_list is not None:
                errors = [error.text for error in error_list.findall('PhraseNotFound')]
                if errors:
                    raise ParseError(f"Search errors: {'; '.join(errors)}")
            
            # Extract basic information
            result = {
                'count': int(root.findtext('Count', '0')),
                'retmax': int(root.findtext('RetMax', '0')),
                'retstart': int(root.findtext('RetStart', '0')),
                'id_list': []
            }
            
            # Extract ID list
            id_list = root.find('IdList')
            if id_list is not None:
                result['id_list'] = [id_elem.text for id_elem in id_list.findall('Id')]
            
            # Extract history information if present
            webenv = root.findtext('WebEnv')
            query_key = root.findtext('QueryKey')
            if webenv:
                result['webenv'] = webenv
                self.client.history.webenv = webenv
            if query_key:
                result['query_key'] = int(query_key)
                self.client.history.query_key = int(query_key)
            
            # Extract translation set
            translation_set = root.find('TranslationSet')
            if translation_set is not None:
                translations = []
                for trans in translation_set.findall('Translation'):
                    translations.append({
                        'from': trans.findtext('From'),
                        'to': trans.findtext('To')
                    })
                result['translations'] = translations
            
            return result
            
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse ESearch response: {str(e)}")
        except (ValueError, TypeError) as e:
            raise ParseError(f"Invalid data in ESearch response: {str(e)}")
