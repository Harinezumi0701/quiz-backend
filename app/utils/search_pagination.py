# app/utils/search_pagination.py
"""
Utility functions for search and pagination functionality in GET endpoints.
Uses Strategy Pattern for search types and Builder Pattern for configuration.
"""
from abc import ABC, abstractmethod
from sqlalchemy.orm import Query
from sqlalchemy import func
from typing import Optional, Tuple, Dict, Any
from datetime import datetime


class SearchStrategy(ABC):
    """Abstract base class for search strategies."""
    
    @abstractmethod
    def apply(self, query: Query, column: Any, search_value: str, **kwargs) -> Query:
        """
        Apply search filter to query.
        
        Args:
            query: SQLAlchemy query object
            column: Column to search in
            search_value: Value to search for
            **kwargs: Additional strategy-specific parameters
        
        Returns:
            Modified query with search filter applied
        """
        pass


class TextSearchStrategy(SearchStrategy):
    """Strategy for text search (case-sensitive or case-insensitive)."""
    
    def apply(self, query: Query, column: Any, search_value: str, case_sensitive: bool = False, **kwargs) -> Query:
        """Apply text search filter."""
        if case_sensitive:
            return query.filter(column.like(f"%{search_value}%"))
        else:
            return query.filter(column.ilike(f"%{search_value}%"))


class DateSearchStrategy(SearchStrategy):
    """Strategy for date search."""
    
    def apply(self, query: Query, column: Any, search_value: str, date_format: Optional[str] = None, **kwargs) -> Query:
        """Apply date search filter."""
        try:
            if date_format:
                search_date = datetime.strptime(search_value, date_format)
            else:
                # Try ISO format
                search_date = datetime.fromisoformat(search_value.replace("Z", "+00:00"))
            
            return query.filter(func.date(column) == search_date.date())
        except (ValueError, AttributeError):
            # Invalid date format, return original query
            return query


class ExactSearchStrategy(SearchStrategy):
    """Strategy for exact match search."""
    
    def apply(self, query: Query, column: Any, search_value: str, case_sensitive: bool = False, **kwargs) -> Query:
        """Apply exact match search filter."""
        if case_sensitive:
            return query.filter(column == search_value)
        else:
            # For case-insensitive exact match, use ilike with exact pattern
            return query.filter(column.ilike(search_value))


class NullSearchStrategy(SearchStrategy):
    """Strategy for null/empty search."""
    
    NULL_VALUES = ["Default", "", "null", "None", "NULL"]
    
    def apply(self, query: Query, column: Any, search_value: str, **kwargs) -> Query:
        """Apply null/empty search filter."""
        if search_value in self.NULL_VALUES:
            return query.filter(column.is_(None))
        # If not a null value, treat as text search
        text_strategy = TextSearchStrategy()
        return text_strategy.apply(query, column, search_value, case_sensitive=False)


class SearchStrategyFactory:
    """Factory for creating search strategies."""
    
    _strategies: Dict[str, SearchStrategy] = {
        "text": TextSearchStrategy(),
        "date": DateSearchStrategy(),
        "exact": ExactSearchStrategy(),
        "null": NullSearchStrategy(),
    }
    
    @classmethod
    def get_strategy(cls, search_type: str) -> Optional[SearchStrategy]:
        """
        Get search strategy by type.
        
        Args:
            search_type: Type of search ("text", "date", "exact", "null")
        
        Returns:
            SearchStrategy instance or None if type not found
        """
        return cls._strategies.get(search_type)
    
    @classmethod
    def register_strategy(cls, search_type: str, strategy: SearchStrategy):
        """
        Register a custom search strategy.
        
        Args:
            search_type: Type identifier for the strategy
            strategy: SearchStrategy instance
        """
        cls._strategies[search_type] = strategy


class SearchConfigBuilder:
    """Builder for creating search configuration dictionaries."""
    
    def __init__(self):
        self._config: Dict[str, Dict[str, Any]] = {}
    
    def add_text_search(
        self,
        key: str,
        column: Any,
        case_sensitive: bool = False
    ) -> "SearchConfigBuilder":
        """
        Add text search configuration.
        
        Args:
            key: Search key identifier
            column: Column to search in
            case_sensitive: Whether search should be case sensitive
        
        Returns:
            Self for method chaining
        """
        self._config[key] = {
            "column": column,
            "type": "text",
            "case_sensitive": case_sensitive
        }
        return self
    
    def add_date_search(
        self,
        key: str,
        column: Any,
        date_format: Optional[str] = None
    ) -> "SearchConfigBuilder":
        """
        Add date search configuration.
        
        Args:
            key: Search key identifier
            column: Date column to search in
            date_format: Optional custom date format string
        
        Returns:
            Self for method chaining
        """
        self._config[key] = {
            "column": column,
            "type": "date",
            "date_format": date_format
        }
        return self
    
    def add_exact_search(
        self,
        key: str,
        column: Any,
        case_sensitive: bool = False
    ) -> "SearchConfigBuilder":
        """
        Add exact match search configuration.
        
        Args:
            key: Search key identifier
            column: Column to search in
            case_sensitive: Whether search should be case sensitive
        
        Returns:
            Self for method chaining
        """
        self._config[key] = {
            "column": column,
            "type": "exact",
            "case_sensitive": case_sensitive
        }
        return self
    
    def add_null_search(
        self,
        key: str,
        column: Any
    ) -> "SearchConfigBuilder":
        """
        Add null/empty search configuration.
        
        Args:
            key: Search key identifier
            column: Column to check for null/empty
        
        Returns:
            Self for method chaining
        """
        self._config[key] = {
            "column": column,
            "type": "null"
        }
        return self
    
    def build(self) -> Dict[str, Dict[str, Any]]:
        """
        Build and return the search configuration.
        
        Returns:
            Search configuration dictionary
        """
        return self._config.copy()


class SearchFilter:
    """Context class that uses search strategies."""
    
    def __init__(self, search_config: Dict[str, Dict[str, Any]]):
        """
        Initialize search filter with configuration.
        
        Args:
            search_config: Search configuration dictionary
        """
        self.search_config = search_config
    
    def apply(
        self,
        query: Query,
        search_key: Optional[str],
        search_value: Optional[str]
    ) -> Query:
        """
        Apply search filter to query using appropriate strategy.
        
        Args:
            query: SQLAlchemy query object
            search_key: Key indicating which field to search
            search_value: Value to search for
        
        Returns:
            Modified query with search filter applied
        """
        if not search_key or not search_value:
            return query
        
        if search_key not in self.search_config:
            return query
        
        config = self.search_config[search_key]
        column = config["column"]
        search_type = config.get("type", "text")
        
        # Get strategy from factory
        strategy = SearchStrategyFactory.get_strategy(search_type)
        if not strategy:
            return query
        
        # Extract strategy-specific parameters from config
        strategy_params = {k: v for k, v in config.items() if k not in ["column", "type"]}
        
        # Apply strategy
        return strategy.apply(query, column, search_value, **strategy_params)


class PaginationHandler:
    """Handler for pagination operations."""
    
    @staticmethod
    def apply(query: Query, page: int = 1, page_size: int = 10) -> Tuple[Query, int]:
        """
        Apply pagination to a query and get total count.
        
        Args:
            query: SQLAlchemy query object
            page: Page number (1-indexed)
            page_size: Number of items per page
        
        Returns:
            Tuple of (paginated query, total count)
        """
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        paginated_query = query.offset(offset).limit(page_size)
        
        return paginated_query, total
    
    @staticmethod
    def get_meta(total: int, page: int, page_size: int) -> Dict[str, Any]:
        """
        Generate pagination metadata.
        
        Args:
            total: Total number of items
            page: Current page number
            page_size: Number of items per page
        
        Returns:
            Dictionary with pagination metadata
        """
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
        }


def paginate_query(
    query: Query,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    search_config: Optional[Dict[str, Dict[str, Any]]] = None,
    page: int = 1,
    page_size: int = 10
) -> Tuple[Query, int]:
    """
    Apply search filter and pagination to a query.
    
    This is a convenience function that combines SearchFilter and PaginationHandler.
    
    Args:
        query: SQLAlchemy query object
        search_key: Key indicating which field to search
        search_value: Value to search for
        search_config: Search configuration dictionary
        page: Page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        Tuple of (paginated query, total count)
    
    Example:
        ```python
        search_config = {
            "content": {
                "column": Model.content,
                "type": "text",
                "case_sensitive": False
            }
        }
        paginated_query, total = paginate_query(
            query, search_key="content", search_value="test",
            search_config=search_config, page=1, page_size=10
        )
        ```
    """
    # Apply search filter if provided
    if search_config:
        search_filter = SearchFilter(search_config)
        query = search_filter.apply(query, search_key, search_value)
    
    # Apply pagination
    return PaginationHandler.apply(query, page, page_size)


def get_pagination_meta(total: int, page: int, page_size: int) -> Dict[str, Any]:
    """
    Generate pagination metadata.
    
    Convenience function that delegates to PaginationHandler.
    
    Args:
        total: Total number of items
        page: Current page number
        page_size: Number of items per page
    
    Returns:
        Dictionary with pagination metadata
    """
    return PaginationHandler.get_meta(total, page, page_size)


def apply_search_filter(
    query: Query,
    search_key: Optional[str],
    search_value: Optional[str],
    search_config: Dict[str, Dict[str, Any]]
) -> Query:
    """
    Apply search filter based on search_key and search_value using a configuration.
    
    Convenience function that delegates to SearchFilter.
    
    Args:
        query: SQLAlchemy query object
        search_key: Key indicating which field to search
        search_value: Value to search for
        search_config: Dictionary mapping search_key to search configuration
    
    Returns:
        Modified query with search filter applied
    """
    search_filter = SearchFilter(search_config)
    return search_filter.apply(query, search_key, search_value)
