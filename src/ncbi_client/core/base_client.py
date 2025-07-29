"""
Base HTTP client for NCBI E-utilities.
"""

import os
import ssl
import time
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, Union, List

from ncbi_client.core.exceptions import NCBIError, RateLimitError, NetworkError, AuthenticationError
from ncbi_client.core.rate_limiter import RateLimiter
from ncbi_client.eutils.esearch import ESearch
from ncbi_client.eutils.efetch import EFetch
from ncbi_client.eutils.epost import EPost
from ncbi_client.eutils.esummary import ESummary
from ncbi_client.eutils.elink import ELink
from ncbi_client.eutils.einfo import EInfo
from ncbi_client.eutils.egquery import EGQuery
from ncbi_client.eutils.espell import ESpell
from ncbi_client.eutils.ecitmatch import ECitMatch
from ncbi_client.utils.history import HistoryManager


logger = logging.getLogger(__name__)


class NCBIClient:
    """
    Main client for accessing NCBI E-utilities.
    
    The client handles authentication, rate limiting, and provides access
    to all E-utility functions.
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        tool: str = "python-ncbi-client",
        rate_limit: Optional[int] = None,
        verify_ssl: bool = True,
        ssl_context: Optional[ssl.SSLContext] = None
    ):
        """
        Initialize NCBI client.
        
        Args:
            api_key: NCBI API key (can also be set via NCBI_API_KEY env var)
            email: Email address for identification (recommended)
            tool: Tool name for identification
            rate_limit: Custom rate limit (requests per second)
            verify_ssl: Whether to verify SSL certificates (default: True)
            ssl_context: Custom SSL context (optional)
        """
        # Set up authentication
        self.api_key = api_key or os.environ.get('NCBI_API_KEY')
        self.email = email
        self.tool = tool
        
        # Set up SSL handling
        self.verify_ssl = verify_ssl
        self.ssl_context = ssl_context
        
        # Create SSL context if needed
        if not self.verify_ssl and not self.ssl_context:
            # Create unverified SSL context for cases where certificates are problematic
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
            logger.warning("SSL verification disabled. This is not recommended for production use.")
        elif self.ssl_context is None:
            # Use default verified SSL context
            self.ssl_context = ssl.create_default_context()
        
        # Set up rate limiting based on API key availability
        if rate_limit is not None:
            self.rate_limiter = RateLimiter(max_requests=rate_limit)
        else:
            # NCBI allows 10 req/sec with API key, 3 req/sec without
            max_requests = 10 if self.api_key else 3
            self.rate_limiter = RateLimiter(max_requests=max_requests)
        
        # Set up URL opener with proper headers
        self.opener = self._setup_opener()
        
        # Initialize history manager
        self.history = HistoryManager()
        
        # Initialize E-utility interfaces
        self.esearch = ESearch(self)
        self.efetch = EFetch(self)
        self.epost = EPost(self)
        self.esummary = ESummary(self)
        self.elink = ELink(self)
        self.einfo = EInfo(self)
        self.egquery = EGQuery(self)
        self.espell = ESpell(self)
        self.ecitmatch = ECitMatch(self)
    
    def _setup_opener(self) -> urllib.request.OpenerDirector:
        """
        Create URL opener with proper headers and error handling.
        """
        opener = urllib.request.build_opener()
        
        # Set up default headers
        opener.addheaders = [
            ('User-Agent', f'ncbi-client/{self.tool} ({self.email})'),
        ]
        
        return opener
    
    def _build_params(self, **kwargs) -> Dict[str, Any]:
        """
        Build request parameters with authentication.
        """
        params = {}
        
        # Add authentication parameters
        if self.api_key:
            params['api_key'] = self.api_key
        if self.email:
            params['email'] = self.email
        params['tool'] = self.tool
        
        # Add user parameters
        params.update(kwargs)
        
        # Clean up None values
        return {k: v for k, v in params.items() if v is not None}
    
    def request(
        self,
        endpoint: str,
        method: str = 'GET',
        **params
    ) -> str:
        """
        Make a request to NCBI E-utilities with rate limiting.
        
        Args:
            endpoint: E-utility endpoint (e.g., 'esearch.fcgi')
            method: HTTP method
            **params: Request parameters
            
        Returns:
            Response text
            
        Raises:
            RateLimitError: If rate limit is exceeded
            NetworkError: If network request fails
            AuthenticationError: If authentication fails
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Build full URL
        url = f"{self.BASE_URL}{endpoint}"
        
        # Build parameters
        request_params = self._build_params(**params)
        
        try:
            logger.debug(f"Making {method} request to {url} with params: {request_params}")
            
            if method.upper() == 'GET':
                if request_params:
                    query_string = urllib.parse.urlencode(request_params)
                    url = f"{url}?{query_string}"
                
                # Create request with SSL context
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=30, context=self.ssl_context) as response:
                    return response.read().decode('utf-8')
                    
            elif method.upper() == 'POST':
                data = urllib.parse.urlencode(request_params).encode('utf-8')
                req = urllib.request.Request(url, data=data, method='POST')
                
                with urllib.request.urlopen(req, timeout=30, context=self.ssl_context) as response:
                    return response.read().decode('utf-8')
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif e.code == 401:
                raise AuthenticationError("Invalid API key")
            else:
                raise NetworkError(f"HTTP {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            # Provide more helpful SSL error messages
            error_msg = str(e.reason)
            if "CERTIFICATE_VERIFY_FAILED" in error_msg:
                raise NetworkError(
                    f"SSL certificate verification failed: {e.reason}\n"
                    "Try initializing the client with verify_ssl=False: "
                    "NCBIClient(verify_ssl=False)"
                )
            else:
                raise NetworkError(f"Request failed: {e.reason}")
        except Exception as e:
            raise NetworkError(f"Request failed: {str(e)}")
    
    def get_databases(self) -> List[str]:
        """
        Get list of available NCBI databases.
        
        Returns:
            List of database names
        """
        return self.einfo.get_databases()
    
    def __repr__(self) -> str:
        """String representation of the client."""
        auth_status = "authenticated" if self.api_key else "unauthenticated"
        rate_limit = self.rate_limiter.max_requests
        return f"NCBIClient({auth_status}, rate_limit={rate_limit}/sec)"
