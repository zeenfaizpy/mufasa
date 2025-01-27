from mufasa.datatypes.schema import Schema


class LogicalPlan:
    def schema(self):
        raise NotImplementedError()

    def children(self):
        raise NotImplementedError()

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


class Scan(LogicalPlan):
    def __init__(self, filepath, datasource, projection):
        self.filepath = filepath
        self.datasource = datasource
        self.projection = projection
        self.child = None

    def schema(self):
       return self.datasource.schema()

    def children(self):
        return []

    def __repr__(self):
        return f"Scan: {self.filepath}; projection={self.projection}"


class Projection(LogicalPlan):
    def __init__(self, child, expr):
        self.child = child
        self.expr = expr

    def schema(self):
        return Schema([e.to_field(self.child) for e in self.expr])

    def children(self):
        return [self.child]

    def __repr__(self):
        proj_str = ", ".join([repr(e) for e in self.expr])
        return f"Projection {proj_str}"


class Filter(LogicalPlan):
    def __init__(self, child, expr):
        self.child = child
        self.expr = expr

    def schema(self):
        return self.child.schema()

    def children(self):
        return [self.child]

    def __repr__(self):
        return f"Filter {self.expr}"


class GroupBy(LogicalPlan):
    def __init__(self, child, group_exprs, agg_exprs):
        self.child = child
        self.group_exprs = group_exprs
        self.agg_exprs = agg_exprs

    def schema(self):
        group_fields = [e.to_field(self.child) for e in self.group_exprs]
        agg_fields = [e.to_field(self.child) for e in self.agg_exprs]
        fields = group_fields + agg_fields
        return Schema(fields)

    def children(self):
        return [self.child]

    def __repr__(self):
        group_str = ", ".join([repr(e) for e in self.group_exprs])
        agg_str = ", ".join([repr(e) for e in self.agg_exprs])
        return f"GroupBy(group_cols=[{group_str}], agg_exprs=[{agg_str}])"