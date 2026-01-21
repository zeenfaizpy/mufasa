from __future__ import annotations
from typing import List, TYPE_CHECKING
import pyarrow as pa

if TYPE_CHECKING:
    pass


class Field:
    """Represents a field in a schema."""
    
    def __init__(self, name: str, data_type: pa.DataType) -> None:
        """
        Initialize a field.
        
        Args:
            name: Field name.
            data_type: PyArrow data type.
        """
        self.name = name
        self.data_type = data_type

    def to_arrow(self) -> pa.Field:
        """Convert to PyArrow field."""
        return pa.field(self.name, self.data_type, nullable=False)


class Schema:
    """Represents a schema with multiple fields."""
    
    def __init__(self, fields: List[Field]) -> None:
        """
        Initialize a schema.
        
        Args:
            fields: List of Field objects.
        """
        self.fields = fields

    def to_arrow(self) -> pa.Schema:
        """Convert to PyArrow schema."""
        return pa.schema([field.to_arrow() for field in self.fields])
    
    def field_names(self) -> List[str]:
        """Get list of field names."""
        return [field.name for field in self.fields]