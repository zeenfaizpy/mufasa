from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from mufasa.datatypes.schema import Schema

if TYPE_CHECKING:
    from mufasa.logical_plan.expressions import LogicalExpr


class LogicalPlan:
    """Base class for all logical plan operators."""
    
    def schema(self) -> Schema:
        """Get the schema of this plan."""
        raise NotImplementedError()

    def children(self) -> List[LogicalPlan]:
        """Get child plans."""
        raise NotImplementedError()

    def format(self, plan: Optional[LogicalPlan] = None, indent: int = 0) -> str:
        """Format the plan as a string."""
        if plan is None:
            plan = self
        plan_string = []
        for _ in range(indent):
            plan_string.append("\t".expandtabs(2))
        plan_string.append(repr(plan))
        plan_string.append("\n")
        for child_plan in plan.children():
            plan_string.append(self.format(child_plan, indent + 1))
        return "".join(plan_string)


class Scan(LogicalPlan):
    """Logical plan operator for scanning a data source."""
    
    def __init__(self, filepath: str, datasource, projection: List[str]) -> None:
        """
        Initialize a Scan operator.
        
        Args:
            filepath: Path to the data file.
            datasource: Data source implementation.
            projection: List of column names to project (empty for all columns).
        """
        self.filepath = filepath
        self.datasource = datasource
        self.projection = projection
        self.child: Optional[LogicalPlan] = None

    def schema(self) -> Schema:
        """Get schema from datasource."""
        return self.datasource.schema()

    def children(self) -> List[LogicalPlan]:
        """Scan has no children."""
        return []

    def __repr__(self) -> str:
        if self.projection:
            return f"Scan: {self.filepath}; projection={self.projection}"
        else:
            return f"Scan: {self.filepath}"


class Projection(LogicalPlan):
    """Logical plan operator for projecting columns."""
    
    def __init__(self, child: LogicalPlan, expr: List[LogicalExpr]) -> None:
        """
        Initialize a Projection operator.
        
        Args:
            child: Child logical plan.
            expr: List of expressions to project.
        """
        self.child = child
        self.expr = expr

    def schema(self) -> Schema:
        """Get schema from projected expressions."""
        return Schema([e.to_field(self.child) for e in self.expr])

    def children(self) -> List[LogicalPlan]:
        """Get child plan."""
        return [self.child]

    def __repr__(self) -> str:
        proj_str = ", ".join([repr(e) for e in self.expr])
        return f"Projection {proj_str}"


class Filter(LogicalPlan):
    """Logical plan operator for filtering rows."""
    
    def __init__(self, child: LogicalPlan, expr: LogicalExpr) -> None:
        """
        Initialize a Filter operator.
        
        Args:
            child: Child logical plan.
            expr: Filter expression.
        """
        self.child = child
        self.expr = expr

    def schema(self) -> Schema:
        """Filter preserves schema of child."""
        return self.child.schema()

    def children(self) -> List[LogicalPlan]:
        """Get child plan."""
        return [self.child]

    def __repr__(self) -> str:
        return f"Filter {self.expr}"


class GroupBy(LogicalPlan):
    """Logical plan operator for grouping and aggregation."""
    
    def __init__(self, child: LogicalPlan, group_exprs: List[LogicalExpr], agg_exprs: List[LogicalExpr]) -> None:
        """
        Initialize a GroupBy operator.
        
        Args:
            child: Child logical plan.
            group_exprs: Expressions to group by.
            agg_exprs: Aggregate expressions.
        """
        self.child = child
        self.group_exprs = group_exprs
        self.agg_exprs = agg_exprs

    def schema(self) -> Schema:
        """Get schema from group and aggregate expressions."""
        group_fields = [e.to_field(self.child) for e in self.group_exprs]
        agg_fields = [e.to_field(self.child) for e in self.agg_exprs]
        fields = group_fields + agg_fields
        return Schema(fields)

    def children(self) -> List[LogicalPlan]:
        """Get child plan."""
        return [self.child]

    def __repr__(self) -> str:
        group_str = ", ".join([repr(e) for e in self.group_exprs])
        agg_str = ", ".join([repr(e) for e in self.agg_exprs])
        return f"GroupBy(group_cols=[{group_str}], agg_exprs=[{agg_str}])"
