from __future__ import annotations
from typing import Optional, Iterator
import csv
import pyarrow as pa
import pyarrow.csv
from mufasa.datatypes.schema import Field, Schema


class CSVDataSource:
    """Optimized CSV data source with cached schema and projection support."""
    
    def __init__(self, filename: str, has_headers: bool = False, batch_size: int = 8192) -> None:
        self.filename = filename
        self.has_headers = has_headers
        self.batch_size = batch_size
        self._schema: Optional[Schema] = None  # Cache schema to avoid re-reading

    def schema(self) -> Schema:
        """Get the schema, using cached version if available."""
        if self._schema is None:
            self._schema = self.infer_schema()
        return self._schema

    def scan(self, projection: Optional[list[str]] = None) -> Iterator[pa.RecordBatch]:
        """
        Scan the CSV file and yield record batches.
        
        Args:
            projection: Optional list of column names to project. If None, all columns are returned.
        """
        # Use PyArrow's optimized CSV reader with better block size
        read_options = pyarrow.csv.ReadOptions(
            block_size=self.batch_size * 1024,  # Convert to bytes
            skip_rows=1 if self.has_headers else 0,
        )
        parse_options = pyarrow.csv.ParseOptions()
        convert_options = pyarrow.csv.ConvertOptions()
        
        # Apply projection if specified
        if projection:
            schema = self.schema()
            # Get all column names from schema
            all_cols = [field.name for field in schema.fields]
            # Only include columns that exist in projection
            convert_options.include_columns = [col for col in projection if col in all_cols]
        
        try:
            with pyarrow.csv.open_csv(
                self.filename,
                read_options=read_options,
                parse_options=parse_options,
                convert_options=convert_options,
            ) as reader:
                for chunk in reader:
                    if chunk is not None and chunk.num_rows > 0:
                        yield chunk
        except Exception as e:
            raise RuntimeError(f"Error reading CSV file {self.filename}: {e}") from e

    def infer_schema(self) -> Schema:
        """
        Infer schema from CSV file. Optimized to read only first few rows.
        """
        try:
            # Use PyArrow's schema inference which is more efficient
            read_options = pyarrow.csv.ReadOptions(
                skip_rows=1 if self.has_headers else 0,
            )
            parse_options = pyarrow.csv.ParseOptions()
            
            # Read just the first batch to infer schema
            with pyarrow.csv.open_csv(
                self.filename,
                read_options=read_options,
                parse_options=parse_options,
            ) as reader:
                first_batch = next(reader, None)
                if first_batch is None:
                    # Empty file - return empty schema
                    return Schema([])
                
                # Convert PyArrow schema to our Schema
                arrow_schema = first_batch.schema
                fields = [
                    Field(field.name, field.type)
                    for field in arrow_schema
                ]
                return Schema(fields)
        except Exception:
            # Fallback to manual inference if PyArrow fails
            with open(self.filename, encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                try:
                    first_line = next(reader)
                    if self.has_headers:
                        fields = [Field(col_name, pa.string()) for col_name in first_line]
                    else:
                        fields = [
                            Field(f"_{i}", pa.string())
                            for i, _ in enumerate(first_line)
                        ]
                    return Schema(fields)
                except StopIteration:
                    return Schema([])
