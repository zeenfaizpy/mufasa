from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from mufasa.dataframe.dataframe import DataFrame
from mufasa.datasource.csv import CSVDataSource
from mufasa.logical_plan.operators import Scan
from mufasa.query_planner.planner import QueryPlanner
from mufasa.sql.parser import SQLParser
from .catalog import Catalog

if TYPE_CHECKING:
    pass


class ExecutionContext:
    """Execution context for running queries with optimization."""
    
    def __init__(self, optimize: bool = True) -> None:
        """
        Initialize execution context.
        
        Args:
            optimize: Whether to apply query optimizations. Defaults to True.
        """
        self.catalog = Catalog()
        self.optimize = optimize

    def csv(self, filename: str, has_headers: bool = False, batch_size: int = 8192) -> DataFrame:
        """
        Create a DataFrame from a CSV file.
        
        Args:
            filename: Path to the CSV file.
            has_headers: Whether the CSV file has headers. Defaults to False.
            batch_size: Batch size for reading. Defaults to 8192 rows.
        
        Returns:
            A DataFrame representing the CSV data.
        """
        datasource = CSVDataSource(filename, has_headers, batch_size)
        plan = Scan(filename, datasource, [])
        df = DataFrame(self, plan)
        return df

    def execute(self, df: DataFrame) -> list:
        """
        Execute a DataFrame query and return results.
        
        Args:
            df: The DataFrame to execute.
        
        Returns:
            List of PyArrow RecordBatches.
        """
        logical_plan = df.logical_plan()
        planner = QueryPlanner(logical_plan, optimize=self.optimize)
        physical_plan = planner.create_physical_plan()
        result = physical_plan.execute()
        return result

    def register_table(self, name: str, df: DataFrame) -> None:
        """
        Register a DataFrame as a table in the catalog.
        
        Args:
            name: Table name.
            df: DataFrame to register.
        """
        self.catalog.register_table(name, df)

    def sql(self, query: str) -> DataFrame:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string.
        
        Returns:
            A DataFrame with the query results.
        """
        parser = SQLParser(self.catalog)
        return parser.parse(query)
