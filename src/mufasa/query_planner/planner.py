from mufasa.logical_plan.projection import Projection
from mufasa.logical_plan.scan import Scan
from mufasa.physical_plan.projection import ProjectionExec
from mufasa.physical_plan.scan import ScanExec
from mufasa.logical_plan.expressions import Column
from mufasa.physical_plan.expressions import ColumnExpr


class QueryPlanner:
    def __init__(self, logical_plan):
        self.logical_plan = logical_plan
    
    def create_physical_plan(self, plan=None):
        if plan is None:
            plan = self.logical_plan
        
        if isinstance(plan, Scan) and type(plan) == Scan:
            return ScanExec(plan.datasource, plan.projection)
        elif isinstance(plan, Projection) and type(plan) == Projection:
            phy_plan = self.create_physical_plan(plan.plan)
            projection_expr = list(map(lambda item: self.create_physical_expr(item, plan.plan), plan.expr))
            return ProjectionExec(phy_plan, projection_expr)
        else:
            raise Exception("No Match in QueryPlanner")

    def create_physical_expr(self, expr, plan):
        if isinstance(expr, Column):
            col_names = list(filter(lambda field: field.name == expr.name, plan.schema().fields))
            if col_names:
                return ColumnExpr(col_names[0].name)
            else:
                raise Exception(f"No column named {expr.name}")
        else:
            raise Exception("Not Implemented")
