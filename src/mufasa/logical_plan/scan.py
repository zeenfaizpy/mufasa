from mufasa.logical_plan.base import LogicalPlan


class Scan(LogicalPlan):
    def __init__(self, filepath, datasource, projection):
        self.filepath = filepath
        self.datasource = datasource
        self.projection = projection
        self.plan = None

    def schema(self):
       return self.datasource.schema()

    def children(self):
        return []

    def __repr__(self):
        return f"Scan: {self.filepath}; projection={self.projection}"