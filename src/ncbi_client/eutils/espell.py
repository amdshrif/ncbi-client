"""
ESpell - Spelling suggestions for NCBI search terms.

Based on NCBI E-utilities documentation:
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/espell.fcgi
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, List

from ncbi_client.core.exceptions import ValidationError, ParseError


class ESpell:
    """
    Interface to NCBI ESpell utility.
    
    ESpell provides spelling suggestions for search terms.
    """
    
    def __init__(self, client):
        """Initialize with reference to main client."""
        self.client = client
    
    def spell_check(
        self,
        db: str,
        term: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get spelling suggestions for a search term.
        
        Args:
            db: Database to check against
            term: Search term to check
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing spelling suggestions
            
        Raises:
            ValidationError: If parameters are invalid
            ParseError: If response cannot be parsed
        """
        # Validate parameters
        if not db:
            raise ValidationError("Database (db) parameter is required")
        if not term:
            raise ValidationError("Search term is required")
        
        # Build parameters
        params = {
            'db': db,
            'term': term,
            'retmode': 'xml'
        }
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Make request
        response = self.client.request('espell.fcgi', **params)
        
        # Parse response
        return self._parse_spell_response(response)
    
    def _parse_spell_response(self, xml_text: str) -> Dict[str, Any]:
        """
        Parse ESpell XML response.
        
        Args:
            xml_text: XML response text
            
        Returns:
            Parsed spelling suggestions
            
        Raises:
            ParseError: If XML cannot be parsed
        """
        try:
            root = ET.fromstring(xml_text)
            
            # Check for errors
            error = root.find('ERROR')
            if error is not None and error.text:
                raise ParseError(f"ESpell error: {error.text}")
            
            result = {
                'database': root.findtext('Database'),
                'query': root.findtext('Query'),
                'corrected_query': root.findtext('CorrectedQuery'),
                'replaced_list': []
            }
            
            # Parse spelling corrections
            for replaced in root.findall('Replaced'):
                correction = {
                    'original': replaced.text,
                    'suggestions': []
                }
                
                # Get suggestions
                for suggestion in replaced.findall('Suggestion'):
                    correction['suggestions'].append(suggestion.text)
                
                result['replaced_list'].append(correction)
            
            return result
            
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse ESpell response: {str(e)}")
        except (ValueError, TypeError) as e:
            raise ParseError(f"Invalid data in ESpell response: {str(e)}")
