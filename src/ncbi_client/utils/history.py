"""
History server management for NCBI E-utilities.

Manages WebEnv and QueryKey parameters for maintaining state
across multiple E-utility calls.
"""

from typing import Optional, Dict, Any, List


class HistoryManager:
    """
    Manages NCBI Entrez history server state.
    
    The history server allows storing search results and UIDs for use
    in subsequent E-utility calls, enabling efficient processing of
    large datasets and complex queries.
    """
    
    def __init__(self):
        """Initialize empty history manager."""
        self.webenv: Optional[str] = None
        self.query_key: Optional[int] = None
        self.query_history: List[Dict[str, Any]] = []
    
    def save_search(
        self,
        webenv: str,
        query_key: int,
        db: str,
        term: str,
        count: int
    ) -> None:
        """
        Save search results to history.
        
        Args:
            webenv: Web environment string
            query_key: Query key number
            db: Database searched
            term: Search term used
            count: Number of results
        """
        self.webenv = webenv
        self.query_key = query_key
        
        # Add to history log
        history_entry = {
            'webenv': webenv,
            'query_key': query_key,
            'database': db,
            'term': term,
            'count': count,
            'timestamp': self._get_timestamp()
        }
        
        self.query_history.append(history_entry)
    
    def save_post(
        self,
        webenv: str,
        query_key: int,
        db: str,
        id_count: int
    ) -> None:
        """
        Save posted UIDs to history.
        
        Args:
            webenv: Web environment string
            query_key: Query key number
            db: Database
            id_count: Number of IDs posted
        """
        self.webenv = webenv
        self.query_key = query_key
        
        # Add to history log
        history_entry = {
            'webenv': webenv,
            'query_key': query_key,
            'database': db,
            'operation': 'post',
            'count': id_count,
            'timestamp': self._get_timestamp()
        }
        
        self.query_history.append(history_entry)
    
    def clear(self) -> None:
        """Clear current history state."""
        self.webenv = None
        self.query_key = None
    
    def clear_all(self) -> None:
        """Clear all history including log."""
        self.clear()
        self.query_history.clear()
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current history state.
        
        Returns:
            Dictionary with current WebEnv and QueryKey
        """
        return {
            'webenv': self.webenv,
            'query_key': self.query_key
        }
    
    def has_history(self) -> bool:
        """
        Check if there is current history state.
        
        Returns:
            True if WebEnv and QueryKey are available
        """
        return self.webenv is not None and self.query_key is not None
    
    def get_history_log(self) -> List[Dict[str, Any]]:
        """
        Get complete history log.
        
        Returns:
            List of all history entries
        """
        return self.query_history.copy()
    
    def combine_queries(
        self,
        query_keys: List[int],
        operator: str = "AND"
    ) -> str:
        """
        Create a combination query from multiple query keys.
        
        Args:
            query_keys: List of query key numbers to combine
            operator: Boolean operator ("AND", "OR", "NOT")
            
        Returns:
            Combined query string for use in ESearch
        """
        if len(query_keys) < 2:
            raise ValueError("Need at least 2 query keys to combine")
        
        terms = [f"#{key}" for key in query_keys]
        return f" {operator} ".join(terms)
    
    def get_query_by_key(self, query_key: int) -> Optional[Dict[str, Any]]:
        """
        Get history entry by query key.
        
        Args:
            query_key: Query key to search for
            
        Returns:
            History entry or None if not found
        """
        for entry in self.query_history:
            if entry.get('query_key') == query_key:
                return entry
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def __repr__(self) -> str:
        """String representation of history manager."""
        state = "active" if self.has_history() else "empty"
        entries = len(self.query_history)
        return f"HistoryManager(state={state}, entries={entries})"
