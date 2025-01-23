from mufasa.logical_plan.projection import *
from mufasa.logical_plan.filter import *


class DataFrame:
    def __init__(self, plan):
        self.plan = plan
    
    def project(self, expr):
        logical_plan = Projection(self.plan, expr)
        return DataFrame(logical_plan)

    def filter(self, expr):
        logical_plan = Filter(self.plan, expr)
        return DataFrame(logical_plan)

    def schema(self):
        return self.plan.schema()

    def logical_plan(self):
        return self.plan
    
    def show_plan(self):
        plan_str = self.format(self.plan)
        print(plan_str)
    
    def format(self, plan, indent=0):
        plan_string = []
        for _ in range(indent):
            plan_string.append("\t".expandtabs(2))
        plan_string.append(repr(plan))
        plan_string.append("\n")
        for child_plan in plan.children():
            plan_string.append(self.format(child_plan, indent+1))
        return "".join(plan_string)