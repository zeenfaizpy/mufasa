from tabulate import tabulate
from mufasa.logical_plan.operators import Projection, Filter, GroupBy
from mufasa.functions import col, count, lit, sum, avg, min, max


class DataFrame:
    def __init__(self, ctx, plan):
        self.ctx = ctx
        self.plan = plan
    
    def create_or_replace_table(self, name):
        self.ctx.register_table(name, self)
        return DataFrame(self.ctx, self.plan)
    
    def select(self, *args):
        logical_plan = Projection(self.plan, args)
        return DataFrame(self.ctx, logical_plan)

    def filter(self, expr):
        logical_plan = Filter(self.plan, expr)
        return DataFrame(self.ctx, logical_plan)
    
    def group_by(self, *group_exprs):
        return GroupedDataFrame(self, group_exprs)

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


class GroupedDataFrame:
    def __init__(self, df, group_exprs):
        self.df = df
        self.group_exprs = group_exprs

    def agg(self, *agg_exprs):
        logical_plan = GroupBy(self.df.plan, self.group_exprs, agg_exprs)
        return DataFrame(self.df.ctx, logical_plan)
    
    def count(self):
        return self.agg(count(lit(1)))

    def sum(self, col_name):
        return self.agg(sum(col(col_name)))

    def avg(self, col_name):
        return self.agg(avg(col(col_name)))

    def min(self, col_name):
        return self.agg(min(col(col_name)))

    def max(self, col_name):
        return self.agg(max(col(col_name)))