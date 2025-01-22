

class Scan:
    def __init__(self, filepath, datasource, projection):
        self.filepath = filepath
        self.datasource = datasource
        self.projection = projection

    def schema(self):
        pass

    def children(self):
        return []

    def __repr__(self):
        if self.projection:
            return f"Scan: {self.filepath}; projection=None"
        else:
            return f"Scan: {self.filepath}; projection={self.projection}"