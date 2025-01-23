

class Filter:
    def __init__(self, plan, expr):
        self.plan = plan
        self.expr = expr

    def schema(self):
        pass

    def children(self):
        return [self.plan]

    def __repr__(self):
        return f"Filter {self.expr}"