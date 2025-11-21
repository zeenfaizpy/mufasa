from __future__ import annotations
import pyarrow as pa
from typing import Any, Optional, TYPE_CHECKING
from mufasa.datatypes.schema import Field

if TYPE_CHECKING:
    from .operators import LogicalPlan


class LogicalExpr:
    """
    Base class for all logical expressions in the query plan.
    """

    def evaluate(self) -> Any:
        """
        Evaluate the expression.
        """
        raise NotImplementedError()

    def __lt__(self, other: Any) -> Binary:
        return Binary("lt", self, "<", other)

    def __le__(self, other: Any) -> Binary:
        return Binary("lte", self, "<=", other)

    def __gt__(self, other: Any) -> Binary:
        return Binary("gt", self, ">", other)

    def __ge__(self, other: Any) -> Binary:
        return Binary("gte", self, ">=", other)

    def __and__(self, other: Any) -> Binary:
        return Binary("and_op", self, "AND", other)

    def __or__(self, other: Any) -> Binary:
        return Binary("or_op", self, "OR", other)

    def to_field(self, plan: LogicalPlan) -> Field:
        """
        Get the schema field for this expression.

        Args:
            plan: The logical plan context.

        Returns:
            The Field object representing this expression's output type.
        """
        raise NotImplementedError()

    def alias(self, name: str) -> Alias:
        """
        Create an alias for this expression.

        Args:
            name: The alias name.

        Returns:
            An Alias expression.
        """
        return Alias(self, name)


class Column(LogicalExpr):
    """
    Represents a column reference in a logical plan.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def to_field(self, plan: LogicalPlan) -> Field:
        """
        Resolve the column to a field in the plan's schema.
        """
        try:
            return next(f for f in plan.schema().fields if f.name == self.name)
        except StopIteration:
            raise Exception(f"No Column named {self.name}")

    def eq(self, right: Any) -> Binary:
        return Binary("eq", self, "=", right)

    def neq(self, right: Any) -> Binary:
        return Binary("not_eq", self, "!=", right)

    def not_eq(self, right: Any) -> Binary:
        return Binary("not_eq", self, "!=", right)

    def gt(self, right: Any) -> Binary:
        return Binary("gt", self, ">", right)

    def gte(self, right: Any) -> Binary:
        return Binary("gte", self, ">=", right)

    def lt(self, right: Any) -> Binary:
        return Binary("lt", self, "<", right)

    def lte(self, right: Any) -> Binary:
        return Binary("lte", self, "<=", right)

    def and_op(self, right: Any) -> Binary:
        return Binary("and_op", self, "AND", right)

    def or_op(self, right: Any) -> Binary:
        return Binary("or_op", self, "OR", right)

    def __repr__(self) -> str:
        return f"#{self.name}"


class Literal(LogicalExpr):
    """
    Represents a literal value.
    """

    def __init__(self, value: Any) -> None:
        self.value = value

    def to_field(self, plan: LogicalPlan) -> Field:
        return Field(str(self.value), pa.string())

    def __repr__(self) -> str:
        return f"'{self.value}'"


class Alias(LogicalExpr):
    """
    Represents an aliased expression.
    """

    def __init__(self, expr: LogicalExpr, alias: str) -> None:
        self.expr = expr
        self.alias = alias

    def to_field(self, plan: LogicalPlan) -> Field:
        return Field(self.alias, self.expr.to_field(plan).data_type)

    def __repr__(self) -> str:
        return f"{self.expr} as #{self.alias}"


class Binary(LogicalExpr):
    """
    Represents a binary operation (e.g., a + b, a > b).
    """

    def __init__(self, name: str, left: Any, op: str, right: Any) -> None:
        self.name = name
        self.left = left
        self.op = op
        self.right = right

    def to_field(self, plan: LogicalPlan) -> Field:
        return Field(self.name, pa.bool_())

    def __repr__(self) -> str:
        return f"{self.left} {self.op} {self.right}"


class Aggregate(LogicalExpr):
    """
    Represents an aggregate function (e.g., SUM, COUNT).
    """

    def __init__(self, name: str, expr: LogicalExpr) -> None:
        self.name = name
        self.expr = expr

    def to_field(self, plan: LogicalPlan) -> Field:
        return Field(self.name, pa.string())

    def __repr__(self) -> str:
        return f"{self.name}({self.expr})"
