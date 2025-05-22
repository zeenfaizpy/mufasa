class Catalog:
    def __init__(self):
        self.tables = {}

    def register_table(self, name, df):
        self.tables[name] = df

    def get_table(self, name):
        return self.tables.get(name)

    def list_tables(self):
        return list(self.tables.keys())

    def is_table_exists(self, name):
        return name in self.tables
