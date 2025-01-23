from mufasa.logical_plan.base import LogicalPlan
from mufasa.datatypes.schema import Schema

class Projection(LogicalPlan):
    def __init__(self, plan, expr):
        self.plan = plan
        self.expr = expr

    def schema(self):
        return Schema([e.to_field(self.plan) for e in self.expr])

    def children(self):
        return [self.plan]

    def __repr__(self):
        proj_str = ", ".join([repr(e) for e in self.expr])
        return f"Projection {proj_str}"