"""
PubChem PUG-REST API integration.

Provides access to PubChem chemical database through the
Power User Gateway (PUG) REST API.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Optional, Any, Union
from ncbi_client.core.base_client import NCBIClient
from ncbi_client.core.exceptions import NCBIError, APIError


class PubChemAPI:
    """
    Interface to PubChem PUG-REST API.
    """
    
    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    def __init__(self, ncbi_client: Optional[NCBIClient] = None):
        """
        Initialize PubChem API client.
        
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
            raise APIError(f"PubChem API request failed: HTTP {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            raise APIError(f"PubChem API request failed: {e.reason}")
        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response: {e}")
    
    def get_compound_by_cid(self, cid: int, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get compound information by CID.
        
        Args:
            cid: Compound ID
            properties: List of properties to retrieve
            
        Returns:
            Compound data
        """
        if properties:
            prop_str = ','.join(properties)
            endpoint = f"compound/cid/{cid}/property/{prop_str}/JSON"
        else:
            endpoint = f"compound/cid/{cid}/JSON"
        
        return self._make_request(endpoint)
    
    def get_compound_by_name(self, name: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get compound information by name.
        
        Args:
            name: Compound name
            properties: List of properties to retrieve
            
        Returns:
            Compound data
        """
        if properties:
            prop_str = ','.join(properties)
            endpoint = f"compound/name/{name}/property/{prop_str}/JSON"
        else:
            endpoint = f"compound/name/{name}/JSON"
        
        return self._make_request(endpoint)
    
    def get_compound_by_smiles(self, smiles: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get compound information by SMILES.
        
        Args:
            smiles: SMILES string
            properties: List of properties to retrieve
            
        Returns:
            Compound data
        """
        if properties:
            prop_str = ','.join(properties)
            endpoint = f"compound/smiles/{smiles}/property/{prop_str}/JSON"
        else:
            endpoint = f"compound/smiles/{smiles}/JSON"
        
        return self._make_request(endpoint)
    
    def search_compounds(self, query: str, search_type: str = "name") -> Dict[str, Any]:
        """
        Search for compounds.
        
        Args:
            query: Search query
            search_type: Type of search (name, smiles, formula)
            
        Returns:
            Search results
        """
        endpoint = f"compound/{search_type}/{query}/cids/JSON"
        return self._make_request(endpoint)
    
    def get_compound_synonyms(self, cid: int) -> Dict[str, Any]:
        """
        Get synonyms for a compound.
        
        Args:
            cid: Compound ID
            
        Returns:
            Synonym data
        """
        endpoint = f"compound/cid/{cid}/synonyms/JSON"
        return self._make_request(endpoint)
    
    def get_compound_sdf(self, cid: int) -> str:
        """
        Get SDF structure for compound.
        
        Args:
            cid: Compound ID
            
        Returns:
            SDF format string
        """
        url = f"{self.BASE_URL}/compound/cid/{cid}/SDF"
        
        try:
            with urllib.request.urlopen(url) as response:
                return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            raise APIError(f"PubChem SDF request failed: HTTP {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            raise APIError(f"PubChem SDF request failed: {e.reason}")
    
    def get_compound_image(self, cid: int, image_size: str = "large") -> bytes:
        """
        Get 2D structure image for compound.
        
        Args:
            cid: Compound ID
            image_size: Image size (small, medium, large)
            
        Returns:
            PNG image data
        """
        url = f"{self.BASE_URL}/compound/cid/{cid}/PNG"
        params = {'image_size': image_size}
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
        
        try:
            with urllib.request.urlopen(full_url) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            raise APIError(f"PubChem image request failed: HTTP {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            raise APIError(f"PubChem image request failed: {e.reason}")
    
    def get_assay_by_aid(self, aid: int) -> Dict[str, Any]:
        """
        Get assay information by AID.
        
        Args:
            aid: Assay ID
            
        Returns:
            Assay data
        """
        endpoint = f"assay/aid/{aid}/JSON"
        return self._make_request(endpoint)
    
    def search_assays(self, query: str, search_type: str = "name") -> Dict[str, Any]:
        """
        Search for assays.
        
        Args:
            query: Search query
            search_type: Type of search (name, target)
            
        Returns:
            Search results
        """
        endpoint = f"assay/{search_type}/{query}/aids/JSON"
        return self._make_request(endpoint)
    
    def get_bioactivity_data(self, aid: int, cid: Optional[int] = None) -> Dict[str, Any]:
        """
        Get bioactivity data for assay.
        
        Args:
            aid: Assay ID
            cid: Optional compound ID filter
            
        Returns:
            Bioactivity data
        """
        if cid:
            endpoint = f"assay/aid/{aid}/cid/{cid}/JSON"
        else:
            endpoint = f"assay/aid/{aid}/JSON"
        
        return self._make_request(endpoint)
    
    def get_substance_by_sid(self, sid: int) -> Dict[str, Any]:
        """
        Get substance information by SID.
        
        Args:
            sid: Substance ID
            
        Returns:
            Substance data
        """
        endpoint = f"substance/sid/{sid}/JSON"
        return self._make_request(endpoint)
    
    def convert_identifiers(self, identifiers: List[Union[str, int]], 
                          from_type: str, to_type: str) -> Dict[str, Any]:
        """
        Convert between different identifier types.
        
        Args:
            identifiers: List of identifiers to convert
            from_type: Source identifier type (cid, name, smiles, etc.)
            to_type: Target identifier type
            
        Returns:
            Conversion results
        """
        id_str = ','.join(map(str, identifiers))
        endpoint = f"compound/{from_type}/{id_str}/{to_type}/JSON"
        return self._make_request(endpoint)
    
    def get_chemical_properties(self, cid: int) -> Dict[str, Any]:
        """
        Get computed chemical properties.
        
        Args:
            cid: Compound ID
            
        Returns:
            Chemical properties
        """
        properties = [
            'MolecularFormula', 'MolecularWeight', 'CanonicalSMILES',
            'IsomericSMILES', 'InChI', 'InChIKey', 'IUPACName',
            'XLogP', 'ExactMass', 'MonoisotopicMass', 'TPSA',
            'Complexity', 'Charge', 'HBondDonorCount', 'HBondAcceptorCount',
            'RotatableBondCount', 'HeavyAtomCount'
        ]
        
        return self.get_compound_by_cid(cid, properties)


class Compound:
    """
    Represents a chemical compound from PubChem.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize from API response data.
        
        Args:
            data: Compound data from API
        """
        self.data = data
        
        # Handle different response formats
        if 'PC_Compounds' in data:
            self.compound_data = data['PC_Compounds'][0] if data['PC_Compounds'] else {}
        elif 'PropertyTable' in data:
            self.compound_data = data['PropertyTable']['Properties'][0] if data['PropertyTable']['Properties'] else {}
        else:
            self.compound_data = data
    
    @property
    def cid(self) -> Optional[int]:
        """Get Compound ID."""
        if 'CID' in self.compound_data:
            return self.compound_data['CID']
        elif 'id' in self.compound_data:
            return self.compound_data['id']['id']['cid']
        return None
    
    @property
    def molecular_formula(self) -> Optional[str]:
        """Get molecular formula."""
        return self.compound_data.get('MolecularFormula')
    
    @property
    def molecular_weight(self) -> Optional[float]:
        """Get molecular weight."""
        return self.compound_data.get('MolecularWeight')
    
    @property
    def canonical_smiles(self) -> Optional[str]:
        """Get canonical SMILES."""
        return self.compound_data.get('CanonicalSMILES')
    
    @property
    def isomeric_smiles(self) -> Optional[str]:
        """Get isomeric SMILES."""
        return self.compound_data.get('IsomericSMILES')
    
    @property
    def inchi(self) -> Optional[str]:
        """Get InChI string."""
        return self.compound_data.get('InChI')
    
    @property
    def inchi_key(self) -> Optional[str]:
        """Get InChI Key."""
        return self.compound_data.get('InChIKey')
    
    @property
    def iupac_name(self) -> Optional[str]:
        """Get IUPAC name."""
        return self.compound_data.get('IUPACName')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cid': self.cid,
            'molecular_formula': self.molecular_formula,
            'molecular_weight': self.molecular_weight,
            'canonical_smiles': self.canonical_smiles,
            'isomeric_smiles': self.isomeric_smiles,
            'inchi': self.inchi,
            'inchi_key': self.inchi_key,
            'iupac_name': self.iupac_name
        }


class Assay:
    """
    Represents a bioassay from PubChem.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize from API response data.
        
        Args:
            data: Assay data from API
        """
        self.data = data
        
        if 'PC_AssayContainer' in data:
            self.assay_data = data['PC_AssayContainer'][0]['assay']['descr'] if data['PC_AssayContainer'] else {}
        else:
            self.assay_data = data
    
    @property
    def aid(self) -> Optional[int]:
        """Get Assay ID."""
        return self.assay_data.get('aid', {}).get('id')
    
    @property
    def name(self) -> Optional[str]:
        """Get assay name."""
        return self.assay_data.get('name')
    
    @property
    def description(self) -> Optional[str]:
        """Get assay description."""
        description_list = self.assay_data.get('description', [])
        return description_list[0] if description_list else None
    
    @property
    def target(self) -> Optional[str]:
        """Get assay target."""
        targets = self.assay_data.get('target', [])
        if targets and isinstance(targets[0], dict):
            return targets[0].get('name')
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'aid': self.aid,
            'name': self.name,
            'description': self.description,
            'target': self.target
        }
