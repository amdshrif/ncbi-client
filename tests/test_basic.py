"""
Basic tests for NCBI Client functionality.
"""

import pytest
from unittest.mock import Mock, patch
from ncbi_client import NCBIClient
from ncbi_client.core.exceptions import ValidationError, RateLimitError


class TestNCBIClient:
    """Test the main NCBIClient class."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = NCBIClient()
        assert client.tool == "python-ncbi-client"
        assert client.rate_limiter.max_requests == 3  # Default without API key
    
    def test_client_with_api_key(self):
        """Test client initialization with API key."""
        client = NCBIClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.rate_limiter.max_requests == 10  # With API key
    
    def test_client_components(self):
        """Test that all E-utility components are initialized."""
        client = NCBIClient()
        assert hasattr(client, 'esearch')
        assert hasattr(client, 'efetch')
        assert hasattr(client, 'epost')
        assert hasattr(client, 'esummary')
        assert hasattr(client, 'elink')
        assert hasattr(client, 'einfo')
        assert hasattr(client, 'egquery')
        assert hasattr(client, 'espell')
        assert hasattr(client, 'ecitmatch')


class TestESearch:
    """Test ESearch functionality."""
    
    def test_search_validation(self):
        """Test search parameter validation."""
        client = NCBIClient()
        
        # Test missing database
        with pytest.raises(ValidationError):
            client.esearch.search(db="", term="test")
        
        # Test missing term
        with pytest.raises(ValidationError):
            client.esearch.search(db="pubmed", term="")
        
        # Test invalid retmax
        with pytest.raises(ValidationError):
            client.esearch.search(db="pubmed", term="test", retmax=0)
    
    @patch('ncbi_client.core.base_client.requests.Session.get')
    def test_search_request(self, mock_get):
        """Test search request formation."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<?xml version="1.0"?>
        <eSearchResult>
            <Count>1</Count>
            <RetMax>1</RetMax>
            <RetStart>0</RetStart>
            <IdList>
                <Id>12345</Id>
            </IdList>
        </eSearchResult>'''
        mock_get.return_value = mock_response
        
        client = NCBIClient()
        result = client.esearch.search(db="pubmed", term="test")
        
        assert result['count'] == 1
        assert result['id_list'] == ['12345']


class TestEFetch:
    """Test EFetch functionality."""
    
    def test_fetch_validation(self):
        """Test fetch parameter validation."""
        client = NCBIClient()
        
        # Test missing database
        with pytest.raises(ValidationError):
            client.efetch.fetch(db="", id_list=["123"])
        
        # Test missing IDs and history
        with pytest.raises(ValidationError):
            client.efetch.fetch(db="pubmed")


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        from ncbi_client.core.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_requests=5)
        assert limiter.max_requests == 5
        assert len(limiter.requests) == 0
    
    def test_rate_limiting(self):
        """Test rate limiting behavior."""
        from ncbi_client.core.rate_limiter import RateLimiter
        import time
        
        limiter = RateLimiter(max_requests=2, time_window=0.1)
        
        # First two requests should be fast
        start = time.time()
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        assert elapsed < 0.05  # Should be very quick
        
        # Third request should be delayed
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        assert elapsed >= 0.05  # Should wait


class TestHistoryManager:
    """Test history server management."""
    
    def test_history_initialization(self):
        """Test history manager initialization."""
        from ncbi_client.utils.history import HistoryManager
        
        history = HistoryManager()
        assert history.webenv is None
        assert history.query_key is None
        assert not history.has_history()
    
    def test_save_search(self):
        """Test saving search to history."""
        from ncbi_client.utils.history import HistoryManager
        
        history = HistoryManager()
        history.save_search(
            webenv="test_webenv",
            query_key=1,
            db="pubmed",
            term="test",
            count=100
        )
        
        assert history.webenv == "test_webenv"
        assert history.query_key == 1
        assert history.has_history()
        assert len(history.query_history) == 1
    
    def test_combine_queries(self):
        """Test query combination."""
        from ncbi_client.utils.history import HistoryManager
        
        history = HistoryManager()
        combined = history.combine_queries([1, 2, 3], "OR")
        assert combined == "#1 OR #2 OR #3"


if __name__ == "__main__":
    pytest.main([__file__])
