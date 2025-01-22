from datatypes.schema import Schema

class Projection:
    def __init__(self, input, expr):
        self.input = input
        self.expr = expr

    def schema(self):
        return Schema([e.to_field(self.input) for e in self.expr])

    def children(self):
        return [input]

    def __repr__(self):
        return f"Projection {[repr(e)for e in self.expr].join(",")}"