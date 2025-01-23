

class Filter:
    def __init__(self, input, expr):
        self.input = input
        self.expr = expr

    def schema(self):
        pass

    def children(self):
        return [input]

    def __repr__(self):
        return f"Filter {self.expr}"