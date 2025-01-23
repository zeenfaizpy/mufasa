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
    