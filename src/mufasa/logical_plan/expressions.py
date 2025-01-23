import pyarrow as pa
from mufasa.datatypes.schema import Field


class Column:
    def __init__(self, name):
        self.name = name
    
    def to_field(self, input):
        results = input.schema().fields.filter(lambda item: item.name == self.name)
        if results:
            return results[0]
        else:
            raise Exception(f"No Column named {self.name}")

    def __repr__(self):
        return f"#{self.name}"


class LiteralString:
    def __init__(self, value):
        self.value = value
    
    def to_field(self, input):
        return Field(self.value, pa.string())
    
    def __repr__(self):
        return f"'{self.value}'"


class LiteralFloat:
    def __init__(self, value):
        self.value = value
    
    def to_field(self, input):
        return Field(self.value, pa.float32())
    
    def __repr__(self):
        return f"'{self.value}'"


class BooleanBinaryExpr:
    def __init__(self, name, op, left, right):
        self.name = name
        self.op = op
        self.left = left
        self.right = right
    
    def to_field(self, input):
        return Field(self.name, pa.bool_())

    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"


