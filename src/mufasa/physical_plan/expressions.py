from itertools import repeat
import pyarrow as pa
import pyarrow.compute as pc


class PhysicalExpr:
    def evaluate(self):
        raise NotImplementedError()


class ColumnExpr(PhysicalExpr):
    def __init__(self, name):
        self.name = name

    def evaluate(self, record_batch): # return pa.array
        if self.name in record_batch.schema.names:
            return record_batch.column(self.name)
        else:
            raise Exception(f"Column name {self.name} doesn't exist")

    def __repr__(self):
        return f"#{self.name}"


class LiteralExpr(PhysicalExpr):
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


class AliasExpr(PhysicalExpr):
    def __init__(self, expr, alias):
        self.expr = expr
        self.alias = alias
        self.name = alias

    def evaluate(self, record_batch): # return pa.array
        pa_arr = self.expr.evaluate(record_batch)
        return pa_arr

    def __repr__(self):
        return f"#{self.alias}"


class BinaryExpr(PhysicalExpr):
    def __init__(self, name, left, op, right):
        self.name = name
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, record_batch): # return pa.array
        left = self.left.evaluate(record_batch)
        right = self.right.evaluate(record_batch)

        if isinstance(self.left, ColumnExpr) and isinstance(self.right, LiteralExpr):
            left_type = left.type
            right = pc.cast(right, target_type=left_type)

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
        elif self.op == "AND":
            return pc.and_(left, right)
        elif self.op == "OR":
            return pc.or_(left, right)
        else:
            raise Exception(f"UnSupported Operation {self.op}")

    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"


class AggregateExpr(PhysicalExpr):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def evaluate(self, record_batch): # return pa.array
        result = self.expr.evaluate(record_batch)

        allowed_funs = ['MAX', 'MIN', 'SUM', 'AVG']
        if self.name in allowed_funs and pa.types.is_string(result.type):
            raise Exception(f"{self.name} operation on String Column is not Supported")

        if self.name == 'MAX':
            final_val = pc.max(result)
        elif self.name == 'MIN':
            final_val = pc.min(result)
        elif self.name == 'SUM':
            final_val = pc.sum(result)
        elif self.name == 'AVG':
            final_val = pc.mean(result)
        elif self.name == 'COUNT':
            final_val = pc.count(result)
        else:
            raise Exception(f"UnSupported Aggregate Operation: {self.name}")
        return pa.array(repeat(final_val, record_batch.num_rows), type=final_val.type)

    def __repr__(self):
        return f"{self.name}({self.expr})"