from functools import singledispatch
from mufasa.logical_plan.expressions import (
    Column, LiteralString, LiteralFloat, BooleanBinaryExpr
)

def col(value):
    return Column(value)

@singledispatch
def lit(value):
    return LiteralString(value)

@lit.register(str)
def lit_string(value):
    return LiteralString(value)

@lit.register(float)
def lit_float(value):
    return LiteralFloat(value)

def eq(left, right):
    return BooleanBinaryExpr("eq", "=", left, right)