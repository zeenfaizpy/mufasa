from mufasa.physical_plan.base import PhysicalPlan

class FilterExec(PhysicalPlan):
    def __init__(self, plan, expr):
        self.plan = plan
        self.expr = expr

    def schema(self):
        return self.plan.schema

    def children(self):
        return [self.plan]
    
    def execute(self):
        pass

    def __repr__(self):
        proj_str = ", ".join([repr(e) for e in self.expr])
        return f"Projection {proj_str}"