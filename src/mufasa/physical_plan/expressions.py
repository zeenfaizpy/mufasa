from __future__ import annotations
from typing import TYPE_CHECKING
from itertools import repeat
import pyarrow as pa
import pyarrow.compute as pc

if TYPE_CHECKING:
    pass


class PhysicalExpr:
    """Base class for all physical expressions."""
    
    def evaluate(self, record_batch: pa.RecordBatch) -> pa.Array:
        """
        Evaluate the expression on a record batch.
        
        Args:
            record_batch: The record batch to evaluate on.
        
        Returns:
            A PyArrow array with the result.
        """
        raise NotImplementedError()


class ColumnExpr(PhysicalExpr):
    """Physical expression for column references."""
    
    def __init__(self, name: str) -> None:
        """
        Initialize a column expression.
        
        Args:
            name: Column name.
        """
        self.name = name

    def evaluate(self, record_batch: pa.RecordBatch) -> pa.Array:
        """Get the column from the record batch."""
        if self.name in record_batch.schema.names:
            return record_batch.column(self.name)
        else:
            raise ValueError(f"Column name {self.name} doesn't exist in schema")

    def __repr__(self) -> str:
        return f"#{self.name}"


class LiteralExpr(PhysicalExpr):
    """Physical expression for literal values."""
    
    def __init__(self, value: any) -> None:
        """
        Initialize a literal expression.
        
        Args:
            value: Literal value.
        """
        self.value = value

    def evaluate(self, record_batch: pa.RecordBatch) -> pa.Array:
        """Create an array with the literal value repeated."""
        data_type = pa.string()
        if isinstance(self.value, int):
            data_type = pa.int64()
        elif isinstance(self.value, float):
            data_type = pa.float64()
        elif isinstance(self.value, str):
            data_type = pa.string()
        elif isinstance(self.value, bool):
            data_type = pa.bool_()
        return pa.array(repeat(self.value, record_batch.num_rows), type=data_type)

    def __repr__(self) -> str:
        return f"#{self.value}"


class AliasExpr(PhysicalExpr):
    """Physical expression for aliased expressions."""
    
    def __init__(self, expr: PhysicalExpr, alias: str) -> None:
        """
        Initialize an alias expression.
        
        Args:
            expr: The expression to alias.
            alias: The alias name.
        """
        self.expr = expr
        self.alias = alias
        self.name = alias

    def evaluate(self, record_batch: pa.RecordBatch) -> pa.Array:
        """Evaluate the aliased expression."""
        return self.expr.evaluate(record_batch)

    def __repr__(self) -> str:
        return f"#{self.alias}"


class BinaryExpr(PhysicalExpr):
    """Physical expression for binary operations."""
    
    def __init__(self, name: str, left: PhysicalExpr, op: str, right: PhysicalExpr) -> None:
        """
        Initialize a binary expression.
        
        Args:
            name: Expression name.
            left: Left operand.
            op: Operation symbol.
            right: Right operand.
        """
        self.name = name
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, record_batch: pa.RecordBatch) -> pa.Array:
        """Evaluate the binary operation."""
        left = self.left.evaluate(record_batch)
        right = self.right.evaluate(record_batch)

        # Type casting optimization: if comparing column with literal, cast literal to column type
        if isinstance(self.left, ColumnExpr) and isinstance(self.right, LiteralExpr):
            left_type = left.type
            try:
                right = pc.cast(right, target_type=left_type)
            except (pa.ArrowInvalid, pa.ArrowNotImplementedError):
                # If casting fails, try the reverse
                pass

        # Map operations to PyArrow compute functions
        op_map = {
            "=": pc.equal,
            "!=": pc.not_equal,
            "<": pc.less,
            ">": pc.greater,
            "<=": pc.less_equal,
            ">=": pc.greater_equal,
            "AND": pc.and_,
            "OR": pc.or_,
        }
        
        op_func = op_map.get(self.op)
        if op_func is None:
            raise ValueError(f"Unsupported operation: {self.op}")
        
        return op_func(left, right)

    def __repr__(self) -> str:
        return f"{self.left} {self.op} {self.right}"


class AggregateExpr(PhysicalExpr):
    """Physical expression for aggregate operations."""
    
    def __init__(self, name: str, expr: PhysicalExpr) -> None:
        """
        Initialize an aggregate expression.
        
        Args:
            name: Aggregate function name (MAX, MIN, SUM, AVG, COUNT).
            expr: Expression to aggregate.
        """
        self.name = name
        self.expr = expr

    def evaluate(self, record_batch: pa.RecordBatch) -> pa.Array:
        """Evaluate the aggregate operation."""
        result = self.expr.evaluate(record_batch)

        # Validate that numeric aggregates aren't applied to strings
        allowed_funs = ["MAX", "MIN", "SUM", "AVG"]
        if self.name in allowed_funs and pa.types.is_string(result.type):
            raise ValueError(f"{self.name} operation on String Column is not supported")

        # Map aggregate names to PyArrow compute functions
        agg_map = {
            "MAX": pc.max,
            "MIN": pc.min,
            "SUM": pc.sum,
            "AVG": pc.mean,
            "COUNT": pc.count,
        }
        
        agg_func = agg_map.get(self.name.upper())
        if agg_func is None:
            raise ValueError(f"Unsupported aggregate operation: {self.name}")
        
        final_val = agg_func(result)
        return pa.array(repeat(final_val, record_batch.num_rows), type=final_val.type)

    def __repr__(self) -> str:
        return f"{self.name}({self.expr})"
