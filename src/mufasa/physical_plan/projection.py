import pyarrow as pa
from mufasa.physical_plan.base import PhysicalPlan

class ProjectionExec(PhysicalPlan):
    def __init__(self, plan, expr):
        self.plan = plan
        self.expr = expr

    def schema(self):
        return self.plan.schema

    def children(self):
        return [self.plan]

    def execute(self):
        for chunk in self.plan.execute():
            for expr in self.expr:
                col = expr.evaluate(chunk)
                yield col

    def __repr__(self):
        proj_str = ", ".join([repr(e) for e in self.expr])
        return f"Projection {proj_str}"