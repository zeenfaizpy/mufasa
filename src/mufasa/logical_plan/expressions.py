from functools import singledispatch
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


class col(Column):
    pass


@singledispatch
def lit(value):
    return LiteralString(value)

class LiteralString:
    def __init__(self, value):
        self.value = value
    
    def to_field(self, input):
        return Field(self.value, pa.string())
    
    def __repr__(self):
        return f"'{self.value}'"

@lit.register(str)
def lit_string(value):
    return LiteralString(value)


class LiteralFloat:
    def __init__(self, value):
        self.value = value
    
    def to_field(self, input):
        return Field(self.value, pa.float32())
    
    def __repr__(self):
        return f"'{self.value}'"

@lit.register(float)
def lit_float(value):
    return LiteralFloat(value)



