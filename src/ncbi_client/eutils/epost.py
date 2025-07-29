"""
EPost - Upload UIDs to the Entrez history server.

Based on NCBI E-utilities documentation:
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi
"""

import xml.etree.ElementTree as ET
from typing import List, Union, Optional, Dict, Any

from ncbi_client.core.exceptions import ValidationError, ParseError


class EPost:
    """
    Interface to NCBI EPost utility.
    
    EPost uploads lists of UIDs to the Entrez history server for use
    in subsequent E-utility calls.
    """
    
    def __init__(self, client):
        """Initialize with reference to main client."""
        self.client = client
    
    def post(
        self,
        db: str,
        id_list: List[Union[str, int]],
        webenv: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload UIDs to history server.
        
        Args:
            db: Database name
            id_list: List of UIDs to upload
            webenv: Existing web environment to add to
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing WebEnv and QueryKey
            
        Raises:
            ValidationError: If parameters are invalid
            ParseError: If response cannot be parsed
        """
        # Validate parameters
        self._validate_post_params(db, id_list)
        
        # Build parameters
        params = {
            'db': db,
            'id': ','.join(str(uid) for uid in id_list)
        }
        
        # Add existing web environment if provided
        if webenv:
            params['WebEnv'] = webenv
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Make request
        response = self.client.request('epost.fcgi', **params)
        
        # Parse response
        return self._parse_post_response(response)
    
    def post_from_file(
        self,
        db: str,
        file_path: str,
        webenv: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload UIDs from a file to history server.
        
        Args:
            db: Database name
            file_path: Path to file containing UIDs (one per line)
            webenv: Existing web environment to add to
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing WebEnv and QueryKey
        """
        # Read UIDs from file
        try:
            with open(file_path, 'r') as f:
                id_list = [line.strip() for line in f if line.strip()]
        except IOError as e:
            raise ValidationError(f"Cannot read file {file_path}: {str(e)}")
        
        return self.post(db=db, id_list=id_list, webenv=webenv, **kwargs)
    
    def post_batches(
        self,
        db: str,
        id_list: List[Union[str, int]],
        batch_size: int = 8000,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Upload large lists of UIDs in batches.
        
        NCBI recommends batches of ~8000 UIDs for EPost.
        
        Args:
            db: Database name
            id_list: List of UIDs to upload
            batch_size: Number of UIDs per batch
            **kwargs: Additional parameters
            
        Returns:
            List of dictionaries containing WebEnv and QueryKey for each batch
        """
        if not id_list:
            raise ValidationError("ID list cannot be empty")
        
        results = []
        webenv = None
        
        # Process in batches
        for i in range(0, len(id_list), batch_size):
            batch = id_list[i:i + batch_size]
            
            # Upload batch
            result = self.post(db=db, id_list=batch, webenv=webenv, **kwargs)
            results.append(result)
            
            # Use the returned WebEnv for subsequent batches
            webenv = result.get('webenv')
        
        return results
    
    def combine_with_existing(
        self,
        db: str,
        id_list: List[Union[str, int]],
        existing_webenv: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add UIDs to an existing web environment.
        
        Args:
            db: Database name
            id_list: List of UIDs to add
            existing_webenv: Existing WebEnv to add to
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing updated WebEnv and new QueryKey
        """
        return self.post(db=db, id_list=id_list, webenv=existing_webenv, **kwargs)
    
    def _validate_post_params(
        self,
        db: str,
        id_list: List[Union[str, int]]
    ) -> None:
        """Validate post parameters."""
        if not db:
            raise ValidationError("Database (db) parameter is required")
        
        if not id_list:
            raise ValidationError("ID list cannot be empty")
        
        if len(id_list) > 10000:
            raise ValidationError(
                "ID list too large. Consider using post_batches() for large lists."
            )
    
    def _parse_post_response(self, xml_text: str) -> Dict[str, Any]:
        """
        Parse EPost XML response.
        
        Args:
            xml_text: XML response text
            
        Returns:
            Parsed post results
            
        Raises:
            ParseError: If XML cannot be parsed
        """
        try:
            root = ET.fromstring(xml_text)
            
            # Check for errors
            error = root.find('ERROR')
            if error is not None:
                raise ParseError(f"EPost error: {error.text}")
            
            # Extract results
            result = {}
            
            webenv = root.findtext('WebEnv')
            query_key = root.findtext('QueryKey')
            
            if webenv:
                result['webenv'] = webenv
                # Store in client history
                self.client.history.webenv = webenv
            
            if query_key:
                result['query_key'] = int(query_key)
                # Store in client history
                self.client.history.query_key = int(query_key)
            
            return result
            
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse EPost response: {str(e)}")
        except (ValueError, TypeError) as e:
            raise ParseError(f"Invalid data in EPost response: {str(e)}")
