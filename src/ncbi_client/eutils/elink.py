"""
ELink - Find related data and links between NCBI databases.

Based on NCBI E-utilities documentation:
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi
"""

import xml.etree.ElementTree as ET
from typing import List, Union, Optional, Dict, Any

from ncbi_client.core.exceptions import ValidationError, ParseError


class ELink:
    """
    Interface to NCBI ELink utility.
    
    ELink finds related data and links between NCBI databases.
    """
    
    # Valid ELink command modes
    VALID_COMMANDS = [
        'neighbor',           # Default: find related records
        'neighbor_history',   # Find related records and store on history server
        'acheck',            # Check for links to external resources
        'ncheck',            # Check for neighbors
        'lcheck',            # Check for external links
        'llinks',            # List external links
        'llinkslib',         # List external links from libraries
        'prlinks'            # List primary external links
    ]
    
    def __init__(self, client):
        """Initialize with reference to main client."""
        self.client = client
    
    def link(
        self,
        dbfrom: str,
        db: str,
        id_list: Optional[List[Union[str, int]]] = None,
        cmd: str = 'neighbor',
        linkname: Optional[str] = None,
        term: Optional[str] = None,
        holding: Optional[str] = None,
        datetype: str = 'pdat',
        reldate: Optional[int] = None,
        mindate: Optional[str] = None,
        maxdate: Optional[str] = None,
        webenv: Optional[str] = None,
        query_key: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Find links between databases.
        
        Args:
            dbfrom: Source database
            db: Target database(s) - can be comma-separated list
            id_list: List of UIDs in source database
            cmd: Link command mode
            linkname: Specific link type
            term: Entrez query to filter results
            holding: Institution holding identifier
            datetype: Date type for filtering
            reldate: Number of days back for date filtering
            mindate: Start date (YYYY/MM/DD)
            maxdate: End date (YYYY/MM/DD)
            webenv: Web environment from previous search
            query_key: Query key from previous search
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing link results
            
        Raises:
            ValidationError: If parameters are invalid
            ParseError: If response cannot be parsed
        """
        # Validate parameters
        self._validate_link_params(dbfrom, db, id_list, webenv, query_key, cmd)
        
        # Build parameters
        params = {
            'dbfrom': dbfrom,
            'db': db,
            'cmd': cmd,
            'retmode': 'xml'
        }
        
        # Add ID list or history parameters
        if id_list:
            if isinstance(id_list, (list, tuple)):
                # For multiple IDs, use multiple &id parameters for "by ID" mode
                if len(id_list) == 1:
                    params['id'] = str(id_list[0])
                else:
                    # This will be handled specially in the request
                    params['id_list'] = id_list
            else:
                params['id'] = str(id_list)
        
        if webenv:
            params['WebEnv'] = webenv
        if query_key is not None:
            params['query_key'] = query_key
        
        # Add optional parameters
        if linkname:
            params['linkname'] = linkname
        if term:
            params['term'] = term
        if holding:
            params['holding'] = holding
        if datetype != 'pdat':
            params['datetype'] = datetype
        if reldate:
            params['reldate'] = reldate
        if mindate:
            params['mindate'] = mindate
        if maxdate:
            params['maxdate'] = maxdate
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Handle multiple IDs for "by ID" mode
        if 'id_list' in params and len(params['id_list']) > 1:
            # Make special request with multiple &id parameters
            return self._link_by_id(params)
        else:
            # Remove id_list if it exists and use regular id
            if 'id_list' in params:
                params['id'] = str(params['id_list'][0])
                del params['id_list']
            
            # Make request
            response = self.client.request('elink.fcgi', **params)
            return self._parse_link_response(response)
    
    def link_by_ids(
        self,
        dbfrom: str,
        db: str,
        ids: List[Union[str, int]],
        cmd: str = 'neighbor',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Find links for each ID separately (by ID mode).
        
        Args:
            dbfrom: Source database
            db: Target database
            ids: List of UIDs
            cmd: Link command mode
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing link results for each ID
        """
        return self.link(
            dbfrom=dbfrom,
            db=db,
            id_list=ids,
            cmd=cmd,
            **kwargs
        )
    
    def link_from_history(
        self,
        dbfrom: str,
        db: str,
        webenv: str,
        query_key: int,
        cmd: str = 'neighbor_history',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Find links from history server.
        
        Args:
            dbfrom: Source database
            db: Target database
            webenv: Web environment
            query_key: Query key
            cmd: Link command mode
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing link results
        """
        return self.link(
            dbfrom=dbfrom,
            db=db,
            webenv=webenv,
            query_key=query_key,
            cmd=cmd,
            **kwargs
        )
    
    def check_links(
        self,
        dbfrom: str,
        ids: List[Union[str, int]],
        cmd: str = 'acheck'
    ) -> Dict[str, Any]:
        """
        Check for availability of links.
        
        Args:
            dbfrom: Source database
            ids: List of UIDs to check
            cmd: Check command ('acheck', 'ncheck', 'lcheck')
            
        Returns:
            Dictionary containing link availability
        """
        return self.link(
            dbfrom=dbfrom,
            db='',  # Not needed for check commands
            id_list=ids,
            cmd=cmd
        )
    
    def _link_by_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle multiple ID requests using separate &id parameters.
        
        Args:
            params: Request parameters with id_list
            
        Returns:
            Combined link results
        """
        id_list = params.pop('id_list')
        
        # Build URL manually for multiple &id parameters
        base_params = params.copy()
        
        # Create parameter string with multiple &id entries
        param_parts = []
        for key, value in base_params.items():
            param_parts.append(f"{key}={value}")
        
        for uid in id_list:
            param_parts.append(f"id={uid}")
        
        # Make custom request
        url = f"{self.client.BASE_URL}elink.fcgi"
        response = self.client.session.get(url, params='&'.join(param_parts), timeout=30)
        
        return self._parse_link_response(response)
    
    def _validate_link_params(
        self,
        dbfrom: str,
        db: str,
        id_list: Optional[List],
        webenv: Optional[str],
        query_key: Optional[int],
        cmd: str
    ) -> None:
        """Validate link parameters."""
        if not dbfrom:
            raise ValidationError("Source database (dbfrom) parameter is required")
        
        if cmd not in self.VALID_COMMANDS:
            raise ValidationError(
                f"Invalid command '{cmd}'. Valid options: {', '.join(self.VALID_COMMANDS)}"
            )
        
        # For most commands, need either ID list or history parameters
        if cmd not in ['acheck', 'ncheck', 'lcheck']:
            if not id_list and not (webenv and query_key is not None):
                raise ValidationError("Must provide either id_list or webenv/query_key")
        
        # Check commands need ID list
        if cmd in ['acheck', 'ncheck', 'lcheck'] and not id_list:
            raise ValidationError(f"Command '{cmd}' requires id_list parameter")
    
    def _parse_link_response(self, xml_text: str) -> Dict[str, Any]:
        """
        Parse ELink XML response.
        
        Args:
            xml_text: XML response text
            
        Returns:
            Parsed link results
            
        Raises:
            ParseError: If XML cannot be parsed
        """
        try:
            root = ET.fromstring(xml_text)
            
            # Check for errors
            error_list = root.find('ERROR')
            if error_list is not None:
                raise ParseError(f"ELink error: {error_list.text}")
            
            result = {
                'linksets': []
            }
            
            # Parse LinkSets
            for linkset in root.findall('LinkSet'):
                linkset_data = {
                    'dbfrom': linkset.findtext('DbFrom'),
                    'ids': []
                }
                
                # Get source IDs
                id_list = linkset.find('IdList')
                if id_list is not None:
                    linkset_data['ids'] = [id_elem.text for id_elem in id_list.findall('Id')]
                
                # Get link info
                linkset_data['linkinfos'] = []
                for linkinfo in linkset.findall('LinkInfo'):
                    info = {
                        'dbto': linkinfo.findtext('DbTo'),
                        'linkname': linkinfo.findtext('LinkName'),
                        'description': linkinfo.findtext('Description'),
                        'menu_tag': linkinfo.findtext('MenuTag')
                    }
                    linkset_data['linkinfos'].append(info)
                
                # Get linked UIDs
                linkset_data['linksetdbs'] = []
                for linksetdb in linkset.findall('LinkSetDb'):
                    db_links = {
                        'dbto': linksetdb.findtext('DbTo'),
                        'linkname': linksetdb.findtext('LinkName'),
                        'links': []
                    }
                    
                    link_list = linksetdb.find('Link')
                    if link_list is not None:
                        db_links['links'] = [
                            link.findtext('Id') for link in link_list.findall('Id')
                        ]
                    
                    linkset_data['linksetdbs'].append(db_links)
                
                # Get web environment info if present
                webenv = linkset.findtext('WebEnv')
                query_key = linkset.findtext('QueryKey')
                if webenv:
                    linkset_data['webenv'] = webenv
                if query_key:
                    linkset_data['query_key'] = int(query_key)
                
                result['linksets'].append(linkset_data)
            
            return result
            
        except ET.ParseError as e:
            raise ParseError(f"Failed to parse ELink response: {str(e)}")
        except (ValueError, TypeError) as e:
            raise ParseError(f"Invalid data in ELink response: {str(e)}")
