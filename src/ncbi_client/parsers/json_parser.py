"""
JSON parsing utilities for NCBI responses.

Handles JSON format responses from NCBI APIs.
"""

import json
from typing import Dict, Any, List, Optional, Union

from ncbi_client.core.exceptions import ParseError


class JSONParser:
    """
    Enhanced JSON parser for NCBI API responses.
    
    Provides convenient methods for parsing and extracting data
    from JSON responses.
    """
    
    @staticmethod
    def parse(json_content: str) -> Union[Dict[str, Any], List[Any]]:
        """
        Parse JSON content with error handling.
        
        Args:
            json_content: JSON string to parse
            
        Returns:
            Parsed JSON data
            
        Raises:
            ParseError: If JSON parsing fails
        """
        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ParseError(f"Failed to parse JSON: {str(e)}")
        except Exception as e:
            raise ParseError(f"Unexpected error parsing JSON: {str(e)}")
    
    @staticmethod
    def parse_esummary_result(json_content: str) -> Dict[str, Any]:
        """
        Parse ESummary JSON response.
        
        Args:
            json_content: ESummary JSON response
            
        Returns:
            Parsed summary results
        """
        data = JSONParser.parse(json_content)
        
        # Handle ESummary result structure
        if 'result' in data:
            result_data = data['result']
            
            # Extract UIDs and metadata
            uids = result_data.get('uids', [])
            
            # Build structured result
            result = {
                'docsums': [],
                'version': '2.0'  # JSON typically indicates v2.0
            }
            
            for uid in uids:
                if uid in result_data:
                    docsum = result_data[uid]
                    docsum['uid'] = uid
                    result['docsums'].append(docsum)
            
            return result
        
        return {'docsums': [], 'version': 'unknown'}
    
    @staticmethod
    def parse_datasets_response(json_content: str) -> Dict[str, Any]:
        """
        Parse NCBI Datasets API JSON response.
        
        Args:
            json_content: Datasets API JSON response
            
        Returns:
            Parsed datasets results
        """
        data = JSONParser.parse(json_content)
        
        # Extract common fields from datasets response
        result = {
            'total_count': data.get('total_count', 0),
            'datasets': data.get('datasets', []),
            'warnings': data.get('warnings', []),
            'errors': data.get('errors', [])
        }
        
        return result
    
    @staticmethod
    def parse_pubchem_response(json_content: str) -> Dict[str, Any]:
        """
        Parse PubChem PUG-REST JSON response.
        
        Args:
            json_content: PubChem JSON response
            
        Returns:
            Parsed PubChem results
        """
        data = JSONParser.parse(json_content)
        
        # Handle various PubChem response formats
        if 'InformationList' in data:
            # Information response
            info_list = data['InformationList']
            result = {
                'information': info_list.get('Information', []),
                'total_count': len(info_list.get('Information', []))
            }
        elif 'PropertyTable' in data:
            # Property response
            prop_table = data['PropertyTable']
            result = {
                'properties': prop_table.get('Properties', []),
                'total_count': len(prop_table.get('Properties', []))
            }
        elif 'IdentifierList' in data:
            # Identifier response
            id_list = data['IdentifierList']
            result = {
                'cids': id_list.get('CID', []),
                'total_count': len(id_list.get('CID', []))
            }
        else:
            # Generic response
            result = data
        
        return result
    
    @staticmethod
    def extract_error_info(json_content: str) -> List[str]:
        """
        Extract error information from JSON response.
        
        Args:
            json_content: JSON content that may contain errors
            
        Returns:
            List of error messages
        """
        try:
            data = JSONParser.parse(json_content)
            errors = []
            
            # Check for various error formats
            if 'error' in data:
                if isinstance(data['error'], str):
                    errors.append(data['error'])
                elif isinstance(data['error'], dict):
                    message = data['error'].get('message', str(data['error']))
                    errors.append(message)
            
            if 'errors' in data and isinstance(data['errors'], list):
                errors.extend(data['errors'])
            
            if 'warnings' in data and isinstance(data['warnings'], list):
                errors.extend([f"Warning: {w}" for w in data['warnings']])
            
            return errors
        except ParseError:
            return []
    
    @staticmethod
    def pretty_print(data: Union[Dict[str, Any], List[Any]], indent: int = 2) -> str:
        """
        Pretty print JSON data.
        
        Args:
            data: Data to format
            indent: Indentation level
            
        Returns:
            Formatted JSON string
        """
        return json.dumps(data, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def flatten_nested_dict(data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
        """
        Flatten nested dictionary structure.
        
        Args:
            data: Nested dictionary to flatten
            separator: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        def _flatten(obj: Any, parent_key: str = '') -> Dict[str, Any]:
            items = []
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    items.extend(_flatten(value, new_key).items())
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                    items.extend(_flatten(value, new_key).items())
            else:
                return {parent_key: obj}
            
            return dict(items)
        
        return _flatten(data)
