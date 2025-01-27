import pyarrow as pa
from mufasa.datatypes.schema import Field


class Expression:
    def evaluate(self):
        raise NotImplementedError()
    
    def __lt__(self, other):
        return Binary("lt", "<", self, other)

    def __le__(self, other):
        return Binary("lte", "<=", self, other)
    
    def __gt__(self, other):
        return Binary("gt", ">", self, other)

    def __ge__(self, other):
        return Binary("gte", ">=", self, other)
    
    def __and__(self, other):
        return Binary("and_op", "AND", self, other)
    
    def __or__(self, other):
        return Binary("or_op", "OR", self, other)


class Column(Expression):
    def __init__(self, name):
        self.name = name
    
    def to_field(self, plan):
        results = list(filter(lambda item: item.name == self.name, plan.schema().fields))
        if results:
            return results[0]
        else:
            raise Exception(f"No Column named {self.name}")

    def __repr__(self):
        return f"#{self.name}"


class Literal(Expression):
    def __init__(self, value):
        self.value = value
    
    def to_field(self, plan):
        return Field(self.value, pa.string())
    
    def __repr__(self):
        return f"'{self.value}'"


class Binary(Expression):
    def __init__(self, name, op, left, right):
        self.name = name
        self.op = op
        self.left = left
        self.right = right
    
    def to_field(self, plan):
        return Field(self.name, pa.bool_())

    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"


class Aggregate(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def to_field(self, plan):
        return Field(self.name, pa.string())

    def __repr__(self):
        return f"{self.name.upper()}({self.expr})"


class AggregateExpr(Expression):
    def __init__(self, name, col):
        self.name = name
        self.col = col
    
    def to_field(self, plan):
        return Field(self.name, pa.string())
    
    def __repr__(self):
        return f"#{self.name}({self.col})"


