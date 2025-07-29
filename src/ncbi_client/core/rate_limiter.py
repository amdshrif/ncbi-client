"""
Rate limiting functionality for NCBI API requests.
"""

import time
from collections import deque
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter for NCBI API requests.
    
    NCBI allows:
    - 3 requests per second without API key
    - 10 requests per second with API key
    """
    
    def __init__(self, max_requests: int = 3, time_window: float = 1.0):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: deque = deque()
    
    def wait_if_needed(self) -> None:
        """
        Wait if necessary to respect rate limits.
        """
        now = time.time()
        
        # Remove requests outside the time window
        while self.requests and self.requests[0] <= now - self.time_window:
            self.requests.popleft()
        
        # If we're at the limit, wait
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                # Clean up after waiting
                now = time.time()
                while self.requests and self.requests[0] <= now - self.time_window:
                    self.requests.popleft()
        
        # Record this request
        self.requests.append(now)
    
    def set_rate(self, max_requests: int) -> None:
        """
        Update the rate limit.
        
        Args:
            max_requests: New maximum requests per time window
        """
        self.max_requests = max_requests
