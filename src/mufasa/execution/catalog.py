from __future__ import annotations
from typing import Dict, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..dataframe.dataframe import DataFrame


class Catalog:
    """Catalog for managing registered tables."""
    
    def __init__(self) -> None:
        """Initialize an empty catalog."""
        self.tables: Dict[str, DataFrame] = {}

    def register_table(self, name: str, df: DataFrame) -> None:
        """
        Register a DataFrame as a table.
        
        Args:
            name: Table name.
            df: DataFrame to register.
        """
        self.tables[name] = df

    def get_table(self, name: str) -> Optional[DataFrame]:
        """
        Get a table by name.
        
        Args:
            name: Table name.
        
        Returns:
            DataFrame if found, None otherwise.
        """
        return self.tables.get(name)

    def list_tables(self) -> List[str]:
        """
        List all registered table names.
        
        Returns:
            List of table names.
        """
        return list(self.tables.keys())

    def is_table_exists(self, name: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            name: Table name.
        
        Returns:
            True if table exists, False otherwise.
        """
        return name in self.tables
