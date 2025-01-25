from tabulate import tabulate
from mufasa.logical_plan.operators import Projection, Filter


class DataFrame:
    def __init__(self, ctx, plan):
        self.ctx = ctx
        self.plan = plan
    
    def select(self, *args):
        logical_plan = Projection(self.plan, args)
        return DataFrame(self.ctx, logical_plan)

    def filter(self, expr):
        logical_plan = Filter(self.plan, expr)
        return DataFrame(self.ctx, logical_plan)

    def schema(self):
        return self.plan.schema()

    def logical_plan(self):
        return self.plan
    
    def show_plan(self):
        plan_str = self.plan.format()
        print(plan_str)
    
    def collect(self):
        data = self.ctx.execute(self)
        # print(data)
        # print(type(data))
        data = data[0]
        data = data.to_pylist()
        print(tabulate(data, headers='keys', tablefmt='pretty'))