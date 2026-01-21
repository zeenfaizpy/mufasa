from __future__ import annotations
from typing import TYPE_CHECKING, List, Set, Optional
from mufasa.logical_plan.operators import (
    Projection,
    Filter,
    Scan,
    GroupBy,
    LogicalPlan,
)
from mufasa.logical_plan.expressions import Literal, Binary, Column, Alias, Aggregate, LogicalExpr

if TYPE_CHECKING:
    pass


class ConstantFolding:
    """Optimizes constant expressions by evaluating them at compile time."""
    
    def optimize(self, plan: LogicalPlan) -> LogicalPlan:
        """Apply constant folding to the plan."""
        if isinstance(plan, Projection):
            exprs = [self.fold_constants(expr) for expr in plan.expr]
            return Projection(self.optimize(plan.child), exprs)
        elif isinstance(plan, Filter):
            expr = self.fold_constants(plan.expr)
            return Filter(self.optimize(plan.child), expr)
        elif isinstance(plan, GroupBy):
            group_exprs = [self.fold_constants(expr) for expr in plan.group_exprs]
            agg_exprs = [self.fold_constants(expr) for expr in plan.agg_exprs]
            return GroupBy(self.optimize(plan.child), group_exprs, agg_exprs)
        else:
            return plan

    def fold_constants(self, expr: LogicalExpr) -> LogicalExpr:
        """Recursively fold constant expressions."""
        if isinstance(expr, Binary):
            left = self.fold_constants(expr.left)
            right = self.fold_constants(expr.right)
            if isinstance(left, Literal) and isinstance(right, Literal):
                return self._evaluate_binary(left.value, right.value, expr.op)
            return Binary(expr.name, left, expr.op, right)
        elif isinstance(expr, Alias):
            return Alias(self.fold_constants(expr.expr), expr.alias)
        elif isinstance(expr, Aggregate):
            return Aggregate(expr.name, self.fold_constants(expr.expr))
        else:
            return expr

    def _evaluate_binary(self, left_val: any, right_val: any, op: str) -> Literal:
        """Evaluate a binary operation on two literal values."""
        try:
            if op == "+":
                return Literal(left_val + right_val)
            elif op == "-":
                return Literal(left_val - right_val)
            elif op == "*":
                return Literal(left_val * right_val)
            elif op == "/":
                if right_val == 0:
                    raise ValueError("Division by zero")
                return Literal(left_val / right_val)
            elif op == "=":
                return Literal(left_val == right_val)
            elif op == "!=":
                return Literal(left_val != right_val)
            elif op == "<":
                return Literal(left_val < right_val)
            elif op == ">":
                return Literal(left_val > right_val)
            elif op == "<=":
                return Literal(left_val <= right_val)
            elif op == ">=":
                return Literal(left_val >= right_val)
            else:
                # For unsupported operations, return original binary
                return Literal(left_val)  # Fallback
        except (TypeError, ValueError):
            # If evaluation fails, return a binary with literals
            return Binary("folded", Literal(left_val), op, Literal(right_val))


class ProjectionPushdown:
    """Pushes projections down to scan operations to reduce data transfer."""
    
    def optimize(self, plan: LogicalPlan) -> LogicalPlan:
        """Apply projection pushdown optimization."""
        if isinstance(plan, Projection):
            # Extract column names from projection expressions
            required_cols = self._extract_columns(plan.expr, plan.child)
            
            # Push projection down to child
            optimized_child = self.optimize(plan.child)
            
            # If child is a Scan, add projection to it
            if isinstance(optimized_child, Scan):
                return Scan(
                    optimized_child.filepath,
                    optimized_child.datasource,
                    required_cols
                )
            # If child is a Projection, merge them
            elif isinstance(optimized_child, Projection):
                # Keep only the columns needed by parent projection
                merged_cols = self._merge_projections(plan.expr, optimized_child.expr, optimized_child.child)
                return Projection(optimized_child.child, merged_cols)
            else:
                return Projection(optimized_child, plan.expr)
        elif isinstance(plan, Filter):
            return Filter(self.optimize(plan.child), plan.expr)
        elif isinstance(plan, GroupBy):
            # For GroupBy, we need columns from group_exprs and agg_exprs
            required_cols = self._extract_columns(plan.group_exprs + plan.agg_exprs, plan.child)
            optimized_child = self.optimize(plan.child)
            if isinstance(optimized_child, Scan):
                optimized_child = Scan(
                    optimized_child.filepath,
                    optimized_child.datasource,
                    required_cols
                )
            return GroupBy(optimized_child, plan.group_exprs, plan.agg_exprs)
        else:
            return plan

    def _extract_columns(self, exprs: List[LogicalExpr], plan: LogicalPlan) -> List[str]:
        """Extract column names from expressions."""
        cols: Set[str] = set()
        
        def collect_cols(expr: LogicalExpr) -> None:
            if isinstance(expr, Column):
                cols.add(expr.name)
            elif isinstance(expr, Alias):
                collect_cols(expr.expr)
            elif isinstance(expr, Binary):
                collect_cols(expr.left)
                collect_cols(expr.right)
            elif isinstance(expr, Aggregate):
                collect_cols(expr.expr)
        
        for expr in exprs:
            collect_cols(expr)
        
        return list(cols)

    def _merge_projections(self, parent_exprs: List[LogicalExpr], child_exprs: List[LogicalExpr], child_plan: LogicalPlan) -> List[LogicalExpr]:
        """Merge two projections, keeping only what parent needs."""
        # For simplicity, return parent expressions
        # In a more sophisticated implementation, we'd map child aliases
        return parent_exprs


class FilterPushdown:
    """Pushes filters down to scan operations to reduce data processing."""
    
    def optimize(self, plan: LogicalPlan) -> LogicalPlan:
        """Apply filter pushdown optimization."""
        if isinstance(plan, Filter):
            optimized_child = self.optimize(plan.child)
            # Push filter down if child is a Scan or another Filter
            if isinstance(optimized_child, Scan):
                # For now, we keep the filter above scan
                # In a more advanced implementation, we'd push it to the datasource
                return Filter(optimized_child, plan.expr)
            elif isinstance(optimized_child, Filter):
                # Combine filters - could optimize further
                return Filter(optimized_child.child, plan.expr)
            else:
                return Filter(optimized_child, plan.expr)
        elif isinstance(plan, Projection):
            return Projection(self.optimize(plan.child), plan.expr)
        elif isinstance(plan, GroupBy):
            return GroupBy(self.optimize(plan.child), plan.group_exprs, plan.agg_exprs)
        else:
            return plan


class ExpressionSimplification:
    """Simplifies expressions (e.g., x AND true -> x, x OR false -> x)."""
    
    def optimize(self, plan: LogicalPlan) -> LogicalPlan:
        """Apply expression simplification."""
        if isinstance(plan, Projection):
            exprs = [self.simplify(expr) for expr in plan.expr]
            return Projection(self.optimize(plan.child), exprs)
        elif isinstance(plan, Filter):
            expr = self.simplify(plan.expr)
            # Remove filters that are always true
            if isinstance(expr, Literal) and expr.value is True:
                return self.optimize(plan.child)
            # Reject filters that are always false
            if isinstance(expr, Literal) and expr.value is False:
                # Return empty result - for now, keep the filter
                pass
            return Filter(self.optimize(plan.child), expr)
        elif isinstance(plan, GroupBy):
            group_exprs = [self.simplify(expr) for expr in plan.group_exprs]
            agg_exprs = [self.simplify(expr) for expr in plan.agg_exprs]
            return GroupBy(self.optimize(plan.child), group_exprs, agg_exprs)
        else:
            return plan

    def simplify(self, expr: LogicalExpr) -> LogicalExpr:
        """Simplify an expression."""
        if isinstance(expr, Binary):
            left = self.simplify(expr.left)
            right = self.simplify(expr.right)
            
            # Boolean simplifications
            if expr.op == "AND":
                if isinstance(left, Literal) and left.value is False:
                    return Literal(False)
                if isinstance(right, Literal) and right.value is False:
                    return Literal(False)
                if isinstance(left, Literal) and left.value is True:
                    return right
                if isinstance(right, Literal) and right.value is True:
                    return left
            elif expr.op == "OR":
                if isinstance(left, Literal) and left.value is True:
                    return Literal(True)
                if isinstance(right, Literal) and right.value is True:
                    return Literal(True)
                if isinstance(left, Literal) and left.value is False:
                    return right
                if isinstance(right, Literal) and right.value is False:
                    return left
            
            return Binary(expr.name, left, expr.op, right)
        elif isinstance(expr, Alias):
            return Alias(self.simplify(expr.expr), expr.alias)
        elif isinstance(expr, Aggregate):
            return Aggregate(expr.name, self.simplify(expr.expr))
        else:
            return expr


class Optimizer:
    """Main optimizer that applies all optimization rules."""
    
    def __init__(self) -> None:
        # Apply rules in order: simplification -> constant folding -> pushdowns
        self.rules = [
            ExpressionSimplification(),
            ConstantFolding(),
            FilterPushdown(),
            ProjectionPushdown(),
        ]

    def optimize(self, plan: LogicalPlan) -> LogicalPlan:
        """Apply all optimization rules to the plan."""
        # Apply rules multiple times until no more changes
        max_iterations = 10
        for iteration in range(max_iterations):
            new_plan = plan
            for rule in self.rules:
                new_plan = rule.optimize(new_plan)
            # Check if plan changed by comparing string representation
            # (since plan objects don't have __eq__ implemented)
            if repr(new_plan) == repr(plan):
                break
            plan = new_plan
        return plan
