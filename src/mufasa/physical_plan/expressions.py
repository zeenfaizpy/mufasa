from itertools import repeat
import pyarrow as pa
import pyarrow.compute as pc


class Expression:
    def evaluate(self):
        raise NotImplementedError()


class ColumnExpr(Expression):
    def __init__(self, name):
        self.name = name

    def evaluate(self, record_batch): # return pa.array
        if self.name in record_batch.schema.names:
            return record_batch.column(self.name)
        else:
            raise Exception(f"Coumn name {self.name} doesn't exist")

    def __repr__(self):
        return f"#{self.name}"


class LiteralExpr(Expression):
    def __init__(self, value):
        self.value = value

    def evaluate(self, record_batch): # return pa.array
        data_type= pa.string()
        if isinstance(self.value, int):
            data_type= pa.int64()
        elif isinstance(self.value, float):
            data_type= pa.float64()
        elif isinstance(self.value, str):
            data_type= pa.string()
        elif isinstance(self.value, bool):
            data_type= pa.bool_()
        return pa.array(repeat(self.value, record_batch.num_rows), type=data_type)

    def __repr__(self):
        return f"#{self.value}"


class BinaryExpr(Expression):
    def __init__(self, name, left, op, right):
        self.name = name
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, record_batch): # return pa.array
        left = self.left.evaluate(record_batch)
        right = self.right.evaluate(record_batch)

        if self.op == "=":
            return pc.equal(left, right)
        elif self.op == "!=":
            return pc.not_equal(left, right)
        elif self.op == "<":
            return pc.less(left, right)
        elif self.op == ">":
            return pc.greater(left, right)
        elif self.op == "<=":
            return pc.less_equal(left, right)
        elif self.op == ">=":
            return pc.greater_equal(left, right)
        else:
            raise Exception(f"UnSupported Operation {self.op}")

    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"