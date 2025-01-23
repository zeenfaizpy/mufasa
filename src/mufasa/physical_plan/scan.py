from mufasa.physical_plan.base import PhysicalPlan


class ScanExec(PhysicalPlan):
    def __init__(self, datasource, projection):
        self.datasource = datasource
        self.projection = projection
        self.plan = None

    def schema(self):
        return self.datasource.schema()

    def children(self):
        return []
    
    def execute(self):
        return self.datasource.scan()

    def __repr__(self):
        return f"Scan: schema={self.schema()}; projection={self.projection}"