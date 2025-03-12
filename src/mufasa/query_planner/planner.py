from mufasa.logical_plan.operators import Projection, Filter, Scan, GroupBy
from mufasa.physical_plan.operators import PhysicalProjection, PhysicalFilter, PhysicalScan, PhysicalGroupBy
from mufasa.logical_plan.expressions import Column, Literal, Alias, Binary, Aggregate
from mufasa.physical_plan.expressions import (
    ColumnExpr, LiteralExpr, AliasExpr, BinaryExpr, AggregateExpr
)


class QueryPlanner:
    def __init__(self, logical_plan):
        self.logical_plan = logical_plan
    
    def create_physical_plan(self, plan=None):
        if plan is None:
            plan = self.logical_plan
        
        if isinstance(plan, Scan) and type(plan) == Scan:
            return PhysicalScan(plan.datasource, plan.projection)
        elif isinstance(plan, Projection) and type(plan) == Projection:
            child_plan = self.create_physical_plan(plan.child)
            proj_exprs = []
            for expr in plan.expr:
                proj_exprs.append(self.create_physical_expr(expr, plan.child))
            return PhysicalProjection(child_plan, proj_exprs)
        elif isinstance(plan, Filter) and type(plan) == Filter:
            child_plan = self.create_physical_plan(plan.child)
            filter_expr = self.create_physical_expr(plan.expr, plan.child)
            return PhysicalFilter(child_plan, filter_expr)
        elif isinstance(plan, GroupBy) and type(plan) == GroupBy:
            child_plan = self.create_physical_plan(plan.child)
            group_exprs = [self.create_physical_expr(expr, plan.child) for expr in plan.group_exprs]
            agg_exprs = [self.create_physical_expr(expr, plan.child) for expr in plan.agg_exprs]
            return PhysicalGroupBy(child_plan, group_exprs, agg_exprs)
        else:
            raise Exception("No Match in Physical Plan Execution")

    def create_physical_expr(self, expr, plan):
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
