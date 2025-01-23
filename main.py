from mufasa.core import ExecutionContext
from mufasa.core.functions import col, eq, lit


def main():
    ctx = ExecutionContext()
    df = (
        ctx.csv("employee.csv")
        .filter(eq(col("state"), lit("CO")))
        .select(col("id"), col("first_name"), col("first_name"))
    )
    df.logical_plan()