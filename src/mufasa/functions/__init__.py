from mufasa.logical_plan.expressions import Column, Literal, Binary, Aggregate


def col(value):
    return Column(value)


def lit(value):
    return Literal(value)


def eq(left, right):
    return Binary("eq", left, "=", right)


def not_eq(left, right):
    return Binary("not_eq", left, "!=", right)


def gt(left, right):
    return Binary("gt", left, ">", right)


def gte(left, right):
    return Binary("gte", left, ">=", right)


def lt(left, right):
    return Binary("lt", left, "<", right)


def lte(left, right):
    return Binary("lte", left, "<=", right)


def and_op(left, right):
    return Binary("and_op", left, "AND", right)


def or_op(left, right):
    return Binary("or_op", left, "OR", right)


def max(expr):
    return Aggregate("MAX", expr)


def min(expr):
    return Aggregate("MIN", expr)


def count(expr):
    return Aggregate("COUNT", expr)


def sum(expr):
    return Aggregate("SUM", expr)


def avg(expr):
    return Aggregate("AVG", expr)
