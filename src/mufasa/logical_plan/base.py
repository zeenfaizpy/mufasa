
class LogicalPlan:
    def schema(self):
        raise NotImplemented

    def children(self):
        raise NotImplemented

    def format(self, plan=None, indent=0):
        if plan is None:
            plan = self
        plan_string = []
        for _ in range(indent):
            plan_string.append("\t".expandtabs(2))
        plan_string.append(repr(plan))
        plan_string.append("\n")
        for child_plan in plan.children():
            plan_string.append(self.format(child_plan, indent+1))
        return "".join(plan_string)