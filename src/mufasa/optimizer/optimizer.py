from mufasa.logical_plan.operators import (
    Projection
)
from mufasa.logical_plan.expressions import (
    Literal, Binary
)


class ConstantFolding:
    def optimize(self, plan):
        if isinstance(plan, Projection):
            exprs = [self.fold_constants(expr) for expr in plan.expr]
            return Projection(plan.child, exprs)
        else:
            return plan
    
    def fold_constants(self, expr):
        if isinstance(expr, Binary):
            left = self.fold_constants(expr.left)
            right = self.fold_constants(expr.right)
            if isinstance(left, Literal) and isinstance(right, Literal):
                if expr.op == "+":
                    return Literal(left.value + right.value)
                elif expr.op == "-":
                    return Literal(left.value - right.value)
                elif expr.op == "*":
                    return Literal(left.value * right.value)
                elif expr.op == "/":
                    return Literal(left.value / right.value)
                else:
                    raise Exception(f"Unsupported binary operation: {expr.op}")
            return Binary(expr.name, left, expr.op, right)
        else:
            return expr


class Optimizer:
    def __init__(self):
        self.rules = [
            ConstantFolding()
        ]
    
    def optimize(self, plan):
        for rule in self.rules:
            plan = rule.optimize(plan)
        return plan