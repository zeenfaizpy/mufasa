from dataframe.dataframe import DataFrame
from datasource.csv import CSVDataSource
from logical_plan.scan import Scan

class ExecutionContext:
    def __init__(self):
        pass

    def csv(self, filename):
        schema = ""
        datasource = CSVDataSource(filename, schema, has_headers=False, batch_size=10)
        plan = Scan(filename, datasource, [])
        df = DataFrame(plan)
        return df

    def execute(self, plan):
        return plan
