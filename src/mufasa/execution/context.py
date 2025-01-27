from mufasa.dataframe.dataframe import DataFrame
from mufasa.datasource.csv import CSVDataSource
from mufasa.logical_plan.operators import Scan
from mufasa.query_planner.planner import QueryPlanner
from mufasa.sql.parser import SQLParser
from .catalog import Catalog



class ExecutionContext:
    def __init__(self):
        self.catalog = Catalog()

    def csv(self, filename, has_headers=False, batch_size=4):
        datasource = CSVDataSource(filename, has_headers, batch_size)
        plan = Scan(filename, datasource, [])
        df = DataFrame(self, plan)
        return df

    def execute(self, df):
        logical_plan = df.logical_plan()
        planner = QueryPlanner(logical_plan)
        physical_plan = planner.create_physical_plan()
        result = physical_plan.execute()
        return result

    def register_table(self, name, df):
        self.catalog.register_table(name, df)
    
    def sql(self, query):
        parser = SQLParser(self.catalog)
        return parser.parse(query)