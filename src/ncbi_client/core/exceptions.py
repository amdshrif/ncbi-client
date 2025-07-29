"""
Custom exceptions for NCBI Client.
"""


class NCBIError(Exception):
    """Base exception for all NCBI client errors."""
    pass


class RateLimitError(NCBIError):
    """Raised when rate limit is exceeded."""
    pass


class AuthenticationError(NCBIError):
    """Raised when API key authentication fails."""
    pass


class ValidationError(NCBIError):
    """Raised when input validation fails."""
    pass


class NetworkError(NCBIError):
    """Raised when network requests fail."""
    pass


class ParseError(NCBIError):
    """Raised when response parsing fails."""
    pass


class DatabaseError(NCBIError):
    """Raised when database-specific errors occur."""
    pass


class APIError(NCBIError):
    """Raised when API requests fail."""
    pass
