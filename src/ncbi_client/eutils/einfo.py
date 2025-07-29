"""
EInfo - Retrieve database information and search fields.

Based on NCBI E-utilities documentation:
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi
"""

import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any

from ncbi_client.core.exceptions import ValidationError, ParseError


class EInfo:
    """
    Interface to NCBI EInfo utility.
    
    EInfo provides database statistics and available search fields.
    """
    
    def __init__(self, client):
        """Initialize with reference to main client."""
        self.client = client
    
    def info(
        self,
        db: Optional[str] = None,
        version: str = "1.0",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get database information.
        
        Args:
            db: Database name (if None, returns list of all databases)
            version: EInfo version ("1.0" or "2.0")
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing database information
            
        Raises:
            ValidationError: If parameters are invalid
            ParseError: If response cannot be parsed
        """
        # Build parameters
        params = {
            'retmode': 'xml'
        }
        
        if db:
            params['db'] = db
        
        if version == "2.0":
            params['version'] = "2.0"
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Make request
        response = self.client.request('einfo.fcgi', **params)
        
        # Parse response
        if version == "2.0":
            return self._parse_info_v2_response(response)
        else:
            return self._parse_info_v1_response(response)
    
    def get_databases(self) -> List[str]:
        """
        Get list of available NCBI databases.
        
        Returns:
            List of database names
        """
        result = self.info()
        return result.get('databases', [])
    
    def get_database_info(self, db: str, version: str = "2.0") -> Dict[str, Any]:
        """
        Get detailed information about a specific database.
        
        Args:
            db: Database name
            version: EInfo version
            
        Returns:
            Dictionary containing database details
        """
        return self.info(db=db, version=version)
    
    def get_search_fields(self, db: str) -> List[Dict[str, Any]]:
        """
        Get available search fields for a database.
        
        Args:
            db: Database name
            
        Returns:
            List of search field information
        """
        result = self.get_database_info(db)
        return result.get('fields', [])
    
    def get_links(self, db: str) -> List[Dict[str, Any]]:
        """
        Get available links for a database.
        
        Args:
            db: Database name
            
        Returns:
            List of link information
        """
        result = self.get_database_info(db)
        return result.get('links', [])
    
    def _parse_info_v1_response(self, xml_text: str) -> Dict[str, Any]:
        """
        Parse EInfo version 1.0 XML response.
        
        Args:
            xml_text: XML response text
            
        Returns:
            Parsed info results
            
        Raises:
            ParseError: If XML cannot be parsed
        """
        try:
            root = ET.fromstring(xml_text)
            
            # Check for errors
            error = root.find('ERROR')
            if error is not None:
                raise ParseError(f"EInfo error: {error.text}")
            
            result = {}
            
            # Check if this is a database list or single database info
            db_list = root.find('DbList')
            if db_list is not None:
                # Database list
                result['databases'] = [
                    db.text for db in db_list.findall('DbName')
                ]
            else:
                # Single database info
                db_info = root.find('DbInfo')
                if db_info is not None:
                    result = self._parse_db_info_v1(db_info)
            
            return result
            
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse EInfo v1.0 response: {str(e)}")
        except (ValueError, TypeError) as e:
            raise ParseError(f"Invalid data in EInfo v1.0 response: {str(e)}")
    
    def _parse_info_v2_response(self, xml_text: str) -> Dict[str, Any]:
        """
        Parse EInfo version 2.0 XML response.
        
        Args:
            xml_text: XML response text
            
        Returns:
            Parsed info results
            
        Raises:
            ParseError: If XML cannot be parsed
        """
        try:
            root = ET.fromstring(xml_text)
            
            # Check for errors
            error = root.find('ERROR')
            if error is not None:
                raise ParseError(f"EInfo error: {error.text}")
            
            result = {}
            
            # Check if this is a database list or single database info
            db_list = root.find('DbList')
            if db_list is not None:
                # Database list
                result['databases'] = [
                    db.text for db in db_list.findall('DbName')
                ]
            else:
                # Single database info (v2.0 format)
                db_info = root.find('DbInfo')
                if db_info is not None:
                    result = self._parse_db_info_v2(db_info)
            
            return result
            
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse EInfo v2.0 response: {str(e)}")
        except (ValueError, TypeError) as e:
            raise ParseError(f"Invalid data in EInfo v2.0 response: {str(e)}")
    
    def _parse_db_info_v1(self, db_info: ET.Element) -> Dict[str, Any]:
        """Parse database info from version 1.0 format."""
        result = {
            'dbname': db_info.findtext('DbName'),
            'description': db_info.findtext('Description'),
            'count': int(db_info.findtext('Count') or '0'),
            'lastupdate': db_info.findtext('LastUpdate'),
            'fields': [],
            'links': []
        }
        
        # Parse field list
        field_list = db_info.find('FieldList')
        if field_list is not None:
            for field in field_list.findall('Field'):
                field_info = {
                    'name': field.findtext('Name'),
                    'fullname': field.findtext('FullName'),
                    'description': field.findtext('Description'),
                    'termcount': int(field.findtext('TermCount') or '0'),
                    'isdate': field.findtext('IsDate') == 'Y',
                    'isnumerical': field.findtext('IsNumerical') == 'Y',
                    'ishierarchy': field.findtext('IsHierarchy') == 'Y'
                }
                result['fields'].append(field_info)
        
        # Parse link list
        link_list = db_info.find('LinkList')
        if link_list is not None:
            for link in link_list.findall('Link'):
                link_info = {
                    'name': link.findtext('Name'),
                    'description': link.findtext('Description'),
                    'dbto': link.findtext('DbTo')
                }
                result['links'].append(link_info)
        
        return result
    
    def _parse_db_info_v2(self, db_info: ET.Element) -> Dict[str, Any]:
        """Parse database info from version 2.0 format."""
        result = {
            'dbname': db_info.findtext('DbName'),
            'description': db_info.findtext('Description'),
            'count': int(db_info.findtext('Count') or '0'),
            'lastupdate': db_info.findtext('LastUpdate'),
            'fields': [],
            'links': []
        }
        
        # Parse field list (v2.0 has more detailed structure)
        field_list = db_info.find('FieldList')
        if field_list is not None:
            for field in field_list.findall('Field'):
                field_info = {
                    'name': field.findtext('Name'),
                    'fullname': field.findtext('FullName'),
                    'description': field.findtext('Description'),
                    'termcount': int(field.findtext('TermCount') or '0'),
                    'isdate': field.findtext('IsDate') == 'Y',
                    'isnumerical': field.findtext('IsNumerical') == 'Y',
                    'ishierarchy': field.findtext('IsHierarchy') == 'Y',
                    'israngable': field.findtext('IsRangable') == 'Y',
                    'istranslatable': field.findtext('IsTranslatable') == 'Y'
                }
                result['fields'].append(field_info)
        
        # Parse link list
        link_list = db_info.find('LinkList')
        if link_list is not None:
            for link in link_list.findall('Link'):
                link_info = {
                    'name': link.findtext('Name'),
                    'description': link.findtext('Description'),
                    'dbto': link.findtext('DbTo'),
                    'category': link.findtext('Category'),
                    'linktype': link.findtext('LinkType')
                }
                result['links'].append(link_info)
        
        return result
