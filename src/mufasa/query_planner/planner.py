from __future__ import annotations
from typing import Optional, List, Union, Any, TYPE_CHECKING
from mufasa.logical_plan.operators import Projection, Filter, Scan, GroupBy, LogicalPlan
from mufasa.physical_plan.operators import (
    PhysicalProjection,
    PhysicalFilter,
    PhysicalScan,
    PhysicalGroupBy,
    PhysicalPlan,
)
from mufasa.logical_plan.expressions import Column, Literal, Alias, Binary, Aggregate, LogicalExpr
from mufasa.physical_plan.expressions import (
    ColumnExpr,
    LiteralExpr,
    AliasExpr,
    BinaryExpr,
    AggregateExpr,
    PhysicalExpr,
)
from mufasa.optimizer.optimizer import Optimizer

if TYPE_CHECKING:
    pass


class QueryPlanner:
    """
    Converts a LogicalPlan into a PhysicalPlan with optimizations.
    """

    def __init__(self, logical_plan: LogicalPlan, optimize: bool = True) -> None:
        self.logical_plan = logical_plan
        self.optimize = optimize
        self.optimizer = Optimizer() if optimize else None

    def create_physical_plan(self, plan: Optional[LogicalPlan] = None) -> PhysicalPlan:
        """
        Create a physical plan from the logical plan.

        Args:
            plan: The logical plan to convert. If None, uses the plan passed in __init__.

        Returns:
            The corresponding PhysicalPlan.
        """
        if plan is None:
            plan = self.logical_plan
        
        # Apply optimizations before converting to physical plan
        if self.optimizer:
            plan = self.optimizer.optimize(plan)

        if isinstance(plan, Scan):
            return PhysicalScan(plan.datasource, plan.projection)
        elif isinstance(plan, Projection):
            child_plan = self.create_physical_plan(plan.child)
            proj_exprs = []
            for expr in plan.expr:
                proj_exprs.append(self.create_physical_expr(expr, plan.child))
            return PhysicalProjection(child_plan, proj_exprs)
        elif isinstance(plan, Filter):
            child_plan = self.create_physical_plan(plan.child)
            filter_expr = self.create_physical_expr(plan.expr, plan.child)
            return PhysicalFilter(child_plan, filter_expr)
        elif isinstance(plan, GroupBy):
            child_plan = self.create_physical_plan(plan.child)
            group_exprs = [
                self.create_physical_expr(expr, plan.child) for expr in plan.group_exprs
            ]
            agg_exprs = [
                self.create_physical_expr(expr, plan.child) for expr in plan.agg_exprs
            ]
            return PhysicalGroupBy(child_plan, group_exprs, agg_exprs)
        else:
            raise Exception(f"No Match in Physical Plan Execution: {type(plan)}")

    def create_physical_expr(self, expr: LogicalExpr, plan: LogicalPlan) -> PhysicalExpr:
        """
        Create a physical expression from a logical expression.

        Args:
            expr: The logical expression.
            plan: The logical plan context.

        Returns:
            The corresponding PhysicalExpr.
        """
        if isinstance(expr, Column):
            return ColumnExpr(expr.name)
        elif isinstance(expr, Literal):
            return LiteralExpr(expr.value)
        elif isinstance(expr, Alias):
            result = self.create_physical_expr(expr.expr, plan)
            return AliasExpr(result, expr.alias)
        elif isinstance(expr, Binary):
            left = self.create_physical_expr(expr.left, plan)
            right = self.create_physical_expr(expr.right, plan)
            return BinaryExpr(expr.name, left, expr.op, right)
        elif isinstance(expr, Aggregate):
            result = self.create_physical_expr(expr.expr, plan)
            return AggregateExpr(expr.name, result)
        else:
            raise Exception(f"No Match in Physical Expr Execution {expr}")
