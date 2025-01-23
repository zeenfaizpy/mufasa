


class ColumnExpr:
    def __init__(self, name):
        self.name = name
    
    def evaluate(self, record_batch):
        return record_batch.select([self.name])

    def __repr__(self):
        return f"#{self.name}"