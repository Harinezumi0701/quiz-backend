# app/utils/search_pagination.py
"""
Utility functions for search and pagination functionality in GET endpoints.
Uses Strategy Pattern for search types and Builder Pattern for configuration.
"""
import re
import unicodedata
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.orm import Query


def remove_vietnamese_accents(text: str) -> str:
    """
    Remove Vietnamese accents from text for accent-insensitive search.
    
    Args:
        text: Input text with Vietnamese accents
        
    Returns:
        Text without Vietnamese accents
        
    Example:
        remove_vietnamese_accents("Nguyễn") -> "Nguyen"
        remove_vietnamese_accents("Việt Nam") -> "Viet Nam"
    """
    if not text:
        return text
    
    # Normalize to NFD (decomposed form) to separate base characters and combining marks
    nfd_text = unicodedata.normalize("NFD", text)
    
    # Remove combining marks (accents)
    no_accents = "".join(
        char for char in nfd_text if unicodedata.category(char) != "Mn"
    )
    
    # Normalize back to NFC (composed form) for consistency
    return unicodedata.normalize("NFC", no_accents)


def create_accent_insensitive_pattern(search_value: str) -> str:
    """
    Create a regex pattern that matches text with or without Vietnamese accents.
    
    Args:
        search_value: Search value (may or may not have accents)
        
    Returns:
        Regex pattern string for accent-insensitive matching
    """
    if not search_value:
        return search_value
    
    # Remove accents from search value
    normalized_search = remove_vietnamese_accents(search_value)
    
    # Escape special regex characters
    escaped = re.escape(normalized_search)
    
    # Create pattern that matches with or without accents
    # This is a simplified approach - for full support, we'd need to map
    # each character to its accented variants
    pattern = escaped
    
    # Replace common Vietnamese characters with their variants
    replacements = {
        'a': '[aàáạảãâầấậẩẫăằắặẳẵ]',
        'A': '[AÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴ]',
        'e': '[eèéẹẻẽêềếệểễ]',
        'E': '[EÈÉẸẺẼÊỀẾỆỂỄ]',
        'i': '[iìíịỉĩ]',
        'I': '[IÌÍỊỈĨ]',
        'o': '[oòóọỏõôồốộổỗơờớợởỡ]',
        'O': '[OÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]',
        'u': '[uùúụủũưừứựửữ]',
        'U': '[UÙÚỤỦŨƯỪỨỰỬỮ]',
        'y': '[yỳýỵỷỹ]',
        'Y': '[YỲÝỴỶỸ]',
        'd': '[dđ]',
        'D': '[DĐ]',
    }
    
    # Build pattern with character variants
    result = []
    for char in pattern:
        if char in replacements:
            result.append(replacements[char])
        else:
            result.append(char)
    
    return ''.join(result)


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
    """Strategy for text search (case-sensitive or case-insensitive, with Vietnamese accent-insensitive support)."""

    def apply(
        self,
        query: Query,
        column: Any,
        search_value: str,
        case_sensitive: bool = False,
        accent_insensitive: bool = True,
        **kwargs,
    ) -> Query:
        """Apply text search filter with optional Vietnamese accent-insensitive support."""
        if accent_insensitive:
            # Normalize search value (remove accents)
            normalized_search = remove_vietnamese_accents(search_value)
            normalized_search_lower = normalized_search.lower()
            
            # Use PostgreSQL's translate function to normalize Vietnamese accents in column
            # Map all Vietnamese accented characters to their base forms
            vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
            base_chars = 'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiioooooooooooooooouuuuuuuuuuuyyyyyyd'
            
            # Normalize the column: convert to lowercase and replace accented chars
            normalized_column = func.lower(
                func.translate(
                    func.lower(column),
                    vietnamese_chars + vietnamese_chars.upper(),
                    base_chars + base_chars.upper()
                )
            )
            
            return query.filter(normalized_column.like(f"%{normalized_search_lower}%"))
        else:
            # Standard search without accent normalization
            if case_sensitive:
                return query.filter(column.like(f"%{search_value}%"))
            else:
                return query.filter(column.ilike(f"%{search_value}%"))


class DateSearchStrategy(SearchStrategy):
    """Strategy for date search. Supports both Unix timestamp (int) and date string formats."""

    def apply(
        self,
        query: Query,
        column: Any,
        search_value: str,
        date_format: str | None = None,
        **kwargs,
    ) -> Query:
        """Apply date search filter."""
        try:
            # Try to parse as Unix timestamp first (int as string)
            try:
                timestamp = int(search_value)
                search_date = datetime.fromtimestamp(timestamp)
            except (ValueError, OSError, OverflowError):
                # Not a timestamp, try parsing as date string
                if date_format:
                    search_date = datetime.strptime(search_value, date_format)
                else:
                    # Try ISO format
                    search_date = datetime.fromisoformat(
                        search_value.replace("Z", "+00:00")
                    )

            return query.filter(func.date(column) == search_date.date())
        except (ValueError, AttributeError):
            # Invalid date format, return original query
            return query


class BooleanSearchStrategy(SearchStrategy):
    """Strategy for boolean search."""

    def apply(
        self,
        query: Query,
        column: Any,
        search_value: str,
        **kwargs,
    ) -> Query:
        """Apply boolean search filter."""
        # Convert string to boolean
        # Accept: "true", "1", "yes", "t" (case-insensitive) -> True
        # Accept: "false", "0", "no", "f" (case-insensitive) -> False
        search_value_lower = search_value.lower().strip()
        if search_value_lower in ("true", "1", "yes", "t", "on"):
            return query.filter(column == True)
        elif search_value_lower in ("false", "0", "no", "f", "off"):
            return query.filter(column == False)
        else:
            # Invalid boolean value, return query without filter
            return query


class ExactSearchStrategy(SearchStrategy):
    """Strategy for exact match search."""

    def apply(
        self,
        query: Query,
        column: Any,
        search_value: str,
        case_sensitive: bool = False,
        **kwargs,
    ) -> Query:
        """Apply exact match search filter."""
        # Always use == for exact match to support UUID and other non-text types
        # If case-insensitive matching is needed, use "text" strategy instead
        return query.filter(column == search_value)


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


class MultipleValueSearchStrategy(SearchStrategy):
    """Strategy for multiple values search (comma-separated -> OR condition)."""

    def apply(
        self,
        query: Query,
        column: Any,
        search_value: str,
        base_strategy: str | None = "exact",
        **kwargs,
    ) -> Query:
        """
        Apply multiple values search filter (OR condition).

        Args:
            query: SQLAlchemy query object
            column: Column to search in
            search_value: Comma-separated values (e.g., "id1,id2,id3")
            base_strategy: Base strategy to use for each value ("exact", "text", etc.)
            **kwargs: Additional strategy-specific parameters

        Returns:
            Modified query with OR condition applied
        """
        if not search_value:
            return query

        # Split by comma and strip whitespace
        values = [v.strip() for v in search_value.split(",") if v.strip()]
        if not values:
            return query

        # Get base strategy
        strategy = SearchStrategyFactory.get_strategy(base_strategy)
        if not strategy:
            strategy = ExactSearchStrategy()

        # Build OR conditions
        conditions = []
        for value in values:
            # Create a temporary query to get the condition
            # We'll use the base strategy's logic but apply OR
            if base_strategy == "exact":
                # For exact match, always use == (not ilike) to support UUID and other non-text types
                conditions.append(column == value)
            elif base_strategy == "text":
                case_sensitive = kwargs.get("case_sensitive", False)
                accent_insensitive = kwargs.get("accent_insensitive", True)
                
                if accent_insensitive:
                    # Normalize search value (remove accents)
                    normalized_value = remove_vietnamese_accents(value)
                    normalized_value_lower = normalized_value.lower()
                    
                    # Use PostgreSQL's translate function to normalize Vietnamese accents
                    vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
                    base_chars = 'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiioooooooooooooooouuuuuuuuuuuyyyyyyd'
                    
                    normalized_column = func.lower(
                        func.translate(
                            func.lower(column),
                            vietnamese_chars + vietnamese_chars.upper(),
                            base_chars + base_chars.upper()
                        )
                    )
                    conditions.append(normalized_column.like(f"%{normalized_value_lower}%"))
                else:
                    if case_sensitive:
                        conditions.append(column.like(f"%{value}%"))
                    else:
                        conditions.append(column.ilike(f"%{value}%"))
            elif base_strategy == "boolean":
                # Convert string to boolean
                value_lower = value.lower().strip()
                if value_lower in ("true", "1", "yes", "t", "on"):
                    conditions.append(column == True)
                elif value_lower in ("false", "0", "no", "f", "off"):
                    conditions.append(column == False)
                # Invalid boolean value is ignored
            else:
                # For other strategies, use exact match as fallback
                conditions.append(column == value)

        if conditions:
            return query.filter(or_(*conditions))

        return query


class SearchStrategyFactory:
    """Factory for creating search strategies."""

    _strategies: dict[str, SearchStrategy] = {
        "text": TextSearchStrategy(),
        "date": DateSearchStrategy(),
        "exact": ExactSearchStrategy(),
        "boolean": BooleanSearchStrategy(),
        "null": NullSearchStrategy(),
        "multiple": MultipleValueSearchStrategy(),
    }

    @classmethod
    def get_strategy(cls, search_type: str) -> SearchStrategy | None:
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
        self._config: dict[str, dict[str, Any]] = {}

    def add_text_search(
        self, key: str, column: Any, case_sensitive: bool = False
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
            "case_sensitive": case_sensitive,
        }
        return self

    def add_date_search(
        self, key: str, column: Any, date_format: str | None = None
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
            "date_format": date_format,
        }
        return self

    def add_exact_search(
        self, key: str, column: Any, case_sensitive: bool = False
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
            "case_sensitive": case_sensitive,
        }
        return self

    def add_null_search(self, key: str, column: Any) -> "SearchConfigBuilder":
        """
        Add null/empty search configuration.

        Args:
            key: Search key identifier
            column: Column to check for null/empty

        Returns:
            Self for method chaining
        """
        self._config[key] = {"column": column, "type": "null"}
        return self

    def build(self) -> dict[str, dict[str, Any]]:
        """
        Build and return the search configuration.

        Returns:
            Search configuration dictionary
        """
        return self._config.copy()


class SearchFilter:
    """Context class that uses search strategies."""

    def __init__(self, search_config: dict[str, dict[str, Any]]):
        """
        Initialize search filter with configuration.

        Args:
            search_config: Search configuration dictionary
        """
        self.search_config = search_config

    def apply(
        self, query: Query, search_key: str | None, search_value: str | None
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
        strategy_params = {
            k: v for k, v in config.items() if k not in ["column", "type"]
        }

        # Check if search_value contains comma (multiple values)
        if "," in search_value:
            # Use multiple value strategy
            multiple_strategy = SearchStrategyFactory.get_strategy("multiple")
            if multiple_strategy:
                # Pass base strategy type to multiple strategy
                strategy_params["base_strategy"] = search_type
                return multiple_strategy.apply(
                    query, column, search_value, **strategy_params
                )

        # Apply strategy
        return strategy.apply(query, column, search_value, **strategy_params)

    def apply_multiple(self, query: Query, filters: list[tuple[str, str]]) -> Query:
        """
        Apply multiple search filters to query.

        Args:
            query: SQLAlchemy query object
            filters: List of (search_key, search_value) tuples

        Returns:
            Modified query with all filters applied (AND condition)
        """
        for search_key, search_value in filters:
            if search_key and search_value:
                query = self.apply(query, search_key, search_value)
        return query


class PaginationHandler:
    """Handler for pagination operations."""

    @staticmethod
    def apply(query: Query, page: int = 1, page_size: int = 10) -> tuple[Query, int]:
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
    def get_meta(total: int, page: int, page_size: int) -> dict[str, Any]:
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
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
        }




def parse_multiple_filters(
    request_params: dict[str, Any],
    search_config: dict[str, dict[str, Any]] | None = None
) -> list[tuple[str, str]]:
    """
    Parse multiple filter parameters from request query params.

    Supports format: key=value
    Also supports comma-separated values (e.g., id=id1,id2,id3 -> OR condition)

    Args:
        request_params: Dictionary of request parameters (from FastAPI Query params)
        search_config: Optional search configuration to validate keys against

    Returns:
        List of (search_key, search_value) tuples
    """
    filters = []
    
    # keys to ignore
    ignore_keys = ["page", "page_size"]
    
    for key, value in request_params.items():
        if key in ignore_keys:
            continue
            
        # If search_config is provided, only accept keys present in config
        if search_config and key not in search_config:
            continue
            
        if value:
            filters.append((key, str(value)))

    return filters


def paginate_query_with_multiple_filters(
    query: Query,
    request_params: dict[str, Any],
    search_config: dict[str, dict[str, Any]] | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> tuple[Query, int]:
    """
    Apply multiple search filters and pagination to a query.

    This function parses multiple filter parameters from request_params and applies them.
    Supports format: key=value (e.g., ?name=John&status=active)

    Args:
        query: SQLAlchemy query object
        request_params: Dictionary of request parameters (from FastAPI Query params)
        search_config: Search configuration dictionary
        page: Page number (1-indexed). If None, will try to get from request_params
        page_size: Number of items per page. If None, will try to get from request_params

    Returns:
        Tuple of (paginated query, total count)
    """
    # Get page and page_size from request_params if not provided
    if page is None:
        page = request_params.get("page", 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1

    if page_size is None:
        page_size = request_params.get("page_size", 10)
        try:
            page_size = int(page_size)
        except (ValueError, TypeError):
            page_size = 10

    if search_config:
        search_filter = SearchFilter(search_config)

        # Parse filters directly from params
        filters = parse_multiple_filters(request_params, search_config)

        if filters:
            # Apply multiple filters
            query = search_filter.apply_multiple(query, filters)

    # Apply pagination
    return PaginationHandler.apply(query, page, page_size)


def get_pagination_meta(total: int, page: int, page_size: int) -> dict[str, Any]:
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
