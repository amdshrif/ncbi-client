"""
ESummary - Retrieve document summaries from NCBI databases.

Based on NCBI E-utilities documentation:
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi
"""

import xml.etree.ElementTree as ET
from typing import List, Union, Optional, Dict, Any

from ncbi_client.core.exceptions import ValidationError, ParseError


class ESummary:
    """
    Interface to NCBI ESummary utility.
    
    ESummary retrieves document summaries (DocSums) for UIDs in NCBI databases.
    """
    
    def __init__(self, client):
        """Initialize with reference to main client."""
        self.client = client
    
    def summary(
        self,
        db: str,
        id_list: Optional[List[Union[str, int]]] = None,
        retstart: int = 0,
        retmax: Optional[int] = None,
        webenv: Optional[str] = None,
        query_key: Optional[int] = None,
        version: str = "1.0",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Retrieve document summaries.
        
        Args:
            db: Database name
            id_list: List of UIDs to get summaries for
            retstart: Starting record index
            retmax: Maximum number of summaries to retrieve
            webenv: Web environment from previous search
            query_key: Query key from previous search
            version: ESummary version ("1.0" or "2.0")
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing parsed document summaries
            
        Raises:
            ValidationError: If parameters are invalid
            ParseError: If response cannot be parsed
        """
        # Validate parameters
        self._validate_summary_params(db, id_list, webenv, query_key, version)
        
        # Build parameters
        params = {
            'db': db,
            'retmode': 'xml'
        }
        
        # Add version parameter if 2.0
        if version == "2.0":
            params['version'] = "2.0"
        
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
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Make request
        response = self.client.request('esummary.fcgi', **params)
        
        # Parse response based on version
        if version == "2.0":
            return self._parse_summary_v2_response(response)
        else:
            return self._parse_summary_v1_response(response)
    
    def summary_by_ids(
        self,
        db: str,
        ids: List[Union[str, int]],
        version: str = "1.0",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get summaries by ID list.
        
        Args:
            db: Database name
            ids: List of UIDs
            version: ESummary version
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing document summaries
        """
        return self.summary(db=db, id_list=ids, version=version, **kwargs)
    
    def summary_from_history(
        self,
        db: str,
        webenv: str,
        query_key: int,
        version: str = "1.0",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get summaries from history server.
        
        Args:
            db: Database name
            webenv: Web environment
            query_key: Query key
            version: ESummary version
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing document summaries
        """
        return self.summary(
            db=db,
            webenv=webenv,
            query_key=query_key,
            version=version,
            **kwargs
        )
    
    def summary_large_dataset(
        self,
        db: str,
        webenv: str,
        query_key: int,
        batch_size: int = 500,
        version: str = "1.0",
        max_records: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get summaries for large dataset in batches.
        
        Args:
            db: Database name
            webenv: Web environment
            query_key: Query key
            batch_size: Number of summaries per batch
            version: ESummary version
            max_records: Maximum total records to fetch
            
        Returns:
            List of summary dictionaries (one per batch)
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
            
            batch_result = self.summary(
                db=db,
                webenv=webenv,
                query_key=query_key,
                retstart=start,
                retmax=batch_max,
                version=version
            )
            
            results.append(batch_result)
        
        return results
    
    def _validate_summary_params(
        self,
        db: str,
        id_list: Optional[List],
        webenv: Optional[str],
        query_key: Optional[int],
        version: str
    ) -> None:
        """Validate summary parameters."""
        if not db:
            raise ValidationError("Database (db) parameter is required")
        
        # Must have either ID list or history parameters
        if not id_list and not (webenv and query_key is not None):
            raise ValidationError("Must provide either id_list or webenv/query_key")
        
        if version not in ["1.0", "2.0"]:
            raise ValidationError("Version must be '1.0' or '2.0'")
    
    def _parse_summary_v1_response(self, xml_text: str) -> Dict[str, Any]:
        """
        Parse ESummary version 1.0 XML response.
        
        Args:
            xml_text: XML response text
            
        Returns:
            Parsed summary results
            
        Raises:
            ParseError: If XML cannot be parsed
        """
        try:
            root = ET.fromstring(xml_text)
            
            # Check for errors
            error_list = root.find('ERROR')
            if error_list is not None:
                raise ParseError(f"ESummary error: {error_list.text}")
            
            # Parse document summaries
            result = {
                'docsums': [],
                'version': '1.0'
            }
            
            for docsum in root.findall('DocSum'):
                doc_data = {'uid': docsum.findtext('Id')}
                
                # Extract items
                for item in docsum.findall('Item'):
                    name = item.get('Name')
                    item_type = item.get('Type')
                    
                    if item_type == 'List':
                        # Handle list items
                        list_items = []
                        for list_item in item.findall('Item'):
                            list_items.append(list_item.text)
                        doc_data[name] = list_items
                    else:
                        doc_data[name] = item.text
                
                result['docsums'].append(doc_data)
            
            return result
            
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse ESummary v1.0 response: {str(e)}")
        except (ValueError, TypeError) as e:
            raise ParseError(f"Invalid data in ESummary v1.0 response: {str(e)}")
    
    def _parse_summary_v2_response(self, xml_text: str) -> Dict[str, Any]:
        """
        Parse ESummary version 2.0 XML response.
        
        Args:
            xml_text: XML response text
            
        Returns:
            Parsed summary results
            
        Raises:
            ParseError: If XML cannot be parsed
        """
        try:
            root = ET.fromstring(xml_text)
            
            # Check for errors
            error_list = root.find('ERROR')
            if error_list is not None:
                raise ParseError(f"ESummary error: {error_list.text}")
            
            # Parse document summaries (v2.0 format is more structured)
            result = {
                'docsums': [],
                'version': '2.0'
            }
            
            for docsum in root.findall('DocumentSummary'):
                doc_data = {'uid': docsum.get('uid')}
                
                # Extract all child elements
                for element in docsum:
                    self._extract_element_v2(element, doc_data)
                
                result['docsums'].append(doc_data)
            
            return result
            
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse ESummary v2.0 response: {str(e)}")
        except (ValueError, TypeError) as e:
            raise ParseError(f"Invalid data in ESummary v2.0 response: {str(e)}")
    
    def _extract_element_v2(self, element: ET.Element, doc_data: Dict[str, Any]) -> None:
        """
        Recursively extract data from ESummary v2.0 elements.
        
        Args:
            element: XML element to extract from
            doc_data: Dictionary to store extracted data
        """
        tag = element.tag
        
        # Handle elements with children
        if len(element) > 0:
            if tag not in doc_data:
                doc_data[tag] = []
            
            child_data = {}
            for child in element:
                self._extract_element_v2(child, child_data)
            
            if child_data:
                doc_data[tag].append(child_data)
            else:
                # No child data, use element text
                doc_data[tag] = element.text
        else:
            # Leaf element
            doc_data[tag] = element.text
