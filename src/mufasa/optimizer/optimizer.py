
def optimize_plan(plan):
    pass


class Optimizer:
    def __init__(self, logical_plan):
        self.logical_plan = logical_plan
    
    def optimize(self):
        plan = optimize_plan(self.logical_plan)
        return plan