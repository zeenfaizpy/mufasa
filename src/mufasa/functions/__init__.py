from mufasa.logical_plan.expressions import (
    Column, Literal, Binary
)

def col(value):
    return Column(value)

def lit(value):
    return Literal(value)

def eq(left, right):
    return Binary("eq", "=", left, right)

def not_eq(left, right):
    return Binary("eq", "!=", left, right)

def gt(left, right):
    return Binary("eq", ">", left, right)

def gte(left, right):
    return Binary("eq", ">=", left, right)

def lt(left, right):
    return Binary("eq", "<", left, right)

def lte(left, right):
    return Binary("eq", "<=", left, right)