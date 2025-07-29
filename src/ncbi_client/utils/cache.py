"""
Caching utilities for NCBI client.

Provides local caching functionality to reduce API calls
and improve performance.
"""

import json
import os
import sqlite3
import time
import hashlib
from typing import Any, Dict, Optional, Union
from pathlib import Path


class CacheManager:
    """
    Simple file-based cache for API responses.
    """
    
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None, 
                 default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache files
            default_ttl: Default time-to-live in seconds
        """
        if cache_dir is None:
            cache_dir = Path.home() / '.ncbi_client_cache'
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
    
    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """
        Generate cache key from URL and parameters.
        
        Args:
            url: Request URL
            params: Request parameters
            
        Returns:
            Cache key string
        """
        cache_string = url
        if params:
            sorted_params = sorted(params.items())
            cache_string += str(sorted_params)
        
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Get cached response.
        
        Args:
            url: Request URL
            params: Request parameters
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if expired
            if time.time() > cache_data['expires_at']:
                cache_file.unlink()  # Remove expired cache
                return None
            
            return cache_data['data']
        
        except (json.JSONDecodeError, KeyError, OSError):
            # Remove corrupted cache file
            try:
                cache_file.unlink()
            except OSError:
                pass
            return None
    
    def set(self, url: str, data: Any, params: Optional[Dict] = None, 
            ttl: Optional[int] = None) -> None:
        """
        Cache response data.
        
        Args:
            url: Request URL
            data: Response data to cache
            params: Request parameters
            ttl: Time-to-live in seconds
        """
        if ttl is None:
            ttl = self.default_ttl
        
        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            'data': data,
            'cached_at': time.time(),
            'expires_at': time.time() + ttl
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except OSError:
            pass  # Ignore cache write errors
    
    def clear(self) -> None:
        """Clear all cached data."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError:
                pass
    
    def clear_expired(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        cleared = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                if current_time > cache_data.get('expires_at', 0):
                    cache_file.unlink()
                    cleared += 1
            
            except (json.JSONDecodeError, KeyError, OSError):
                # Remove corrupted files
                try:
                    cache_file.unlink()
                    cleared += 1
                except OSError:
                    pass
        
        return cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_files = len(cache_files)
        total_size = sum(f.stat().st_size for f in cache_files)
        
        expired_count = 0
        current_time = time.time()
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                if current_time > cache_data.get('expires_at', 0):
                    expired_count += 1
            
            except (json.JSONDecodeError, KeyError, OSError):
                expired_count += 1
        
        return {
            'total_entries': total_files,
            'expired_entries': expired_count,
            'valid_entries': total_files - expired_count,
            'total_size_bytes': total_size,
            'cache_directory': str(self.cache_dir)
        }


class SQLiteCache:
    """
    SQLite-based cache for better performance and query capabilities.
    """
    
    def __init__(self, db_path: Optional[Union[str, Path]] = None, 
                 default_ttl: int = 3600):
        """
        Initialize SQLite cache.
        
        Args:
            db_path: Path to SQLite database file
            default_ttl: Default time-to-live in seconds
        """
        if db_path is None:
            cache_dir = Path.home() / '.ncbi_client_cache'
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = cache_dir / 'cache.db'
        
        self.db_path = Path(db_path)
        self.default_ttl = default_ttl
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    cache_key TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    params TEXT,
                    data TEXT NOT NULL,
                    cached_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)
            
            # Create index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
            """)
    
    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from URL and parameters."""
        cache_string = url
        if params:
            sorted_params = sorted(params.items())
            cache_string += str(sorted_params)
        
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Get cached response.
        
        Args:
            url: Request URL
            params: Request parameters
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._get_cache_key(url, params)
        current_time = time.time()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM cache WHERE cache_key = ? AND expires_at > ?",
                (cache_key, current_time)
            )
            
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    # Remove corrupted entry
                    conn.execute("DELETE FROM cache WHERE cache_key = ?", (cache_key,))
                    return None
        
        return None
    
    def set(self, url: str, data: Any, params: Optional[Dict] = None, 
            ttl: Optional[int] = None) -> None:
        """
        Cache response data.
        
        Args:
            url: Request URL
            data: Response data to cache
            params: Request parameters
            ttl: Time-to-live in seconds
        """
        if ttl is None:
            ttl = self.default_ttl
        
        cache_key = self._get_cache_key(url, params)
        current_time = time.time()
        expires_at = current_time + ttl
        
        params_str = json.dumps(params) if params else None
        data_str = json.dumps(data)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache 
                (cache_key, url, params, data, cached_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cache_key, url, params_str, data_str, current_time, expires_at)
            )
    
    def clear(self) -> None:
        """Clear all cached data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
    
    def clear_expired(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        current_time = time.time()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM cache WHERE expires_at <= ?", (current_time,))
            return cursor.rowcount
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        current_time = time.time()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            total_entries = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM cache WHERE expires_at <= ?", (current_time,))
            expired_entries = cursor.fetchone()[0]
            
            # Get database file size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'valid_entries': total_entries - expired_entries,
            'database_size_bytes': db_size,
            'database_path': str(self.db_path)
        }


class MemoryCache:
    """
    Simple in-memory cache for short-term caching.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time-to-live in seconds
        """
        self.cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from URL and parameters."""
        cache_string = url
        if params:
            sorted_params = sorted(params.items())
            cache_string += str(sorted_params)
        
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Get cached response.
        
        Args:
            url: Request URL
            params: Request parameters
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._get_cache_key(url, params)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            if time.time() > entry['expires_at']:
                del self.cache[cache_key]
                return None
            
            return entry['data']
        
        return None
    
    def set(self, url: str, data: Any, params: Optional[Dict] = None, 
            ttl: Optional[int] = None) -> None:
        """
        Cache response data.
        
        Args:
            url: Request URL
            data: Response data to cache
            params: Request parameters
            ttl: Time-to-live in seconds
        """
        if ttl is None:
            ttl = self.default_ttl
        
        cache_key = self._get_cache_key(url, params)
        
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['cached_at'])
            del self.cache[oldest_key]
        
        self.cache[cache_key] = {
            'data': data,
            'cached_at': time.time(),
            'expires_at': time.time() + ttl
        }
    
    def clear(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
    
    def clear_expired(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        current_time = time.time()
        expired_count = sum(
            1 for entry in self.cache.values()
            if current_time > entry['expires_at']
        )
        
        return {
            'total_entries': len(self.cache),
            'expired_entries': expired_count,
            'valid_entries': len(self.cache) - expired_count,
            'max_size': self.max_size,
            'memory_usage_estimate': len(str(self.cache))
        }
