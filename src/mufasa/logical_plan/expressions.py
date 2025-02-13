import pyarrow as pa
from mufasa.datatypes.schema import Field


class LogicalExpr:
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


class Column(LogicalExpr):
    def __init__(self, name):
        self.name = name
    
    def to_field(self, plan):
        results = list(filter(lambda item: item.name == self.name, plan.schema().fields))
        if results:
            return results[0]
        else:
            raise Exception(f"No Column named {self.name}")
    
    def eq(self, right):
        return Binary("eq", self, "=", right)
    
    def neq(self, right):
        return Binary("not_eq", self, "!=", right)
    
    def not_eq(self, right):
        return Binary("not_eq", self, "!=", right)

    def gt(self, right):
        return Binary("gt", self, ">", right)

    def gte(self, right):
        return Binary("gte", self, ">=", right)

    def lt(self, right):
        return Binary("lt", self, "<", right)

    def lte(self, right):
        return Binary("lte", self, "<=", right)

    def and_op(self, right):
        return Binary("and_op", self, "AND", right)

    def or_op(self, right):
        return Binary("or_op", self, "OR", right)

    def __repr__(self):
        return f"#{self.name}"


class Literal(LogicalExpr):
    def __init__(self, value):
        self.value = value
    
    def to_field(self, plan):
        return Field(self.value, pa.string())
    
    def __repr__(self):
        return f"'{self.value}'"


class Binary(LogicalExpr):
    def __init__(self, name, left, op, right):
        self.name = name
        self.left = left
        self.op = op
        self.right = right
    
    def to_field(self, plan):
        return Field(self.name, pa.bool_())

    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"


class Aggregate(LogicalExpr):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def to_field(self, plan):
        return Field(self.name, pa.string())
    
    def __repr__(self):
        return f"{self.name}({self.expr})"


