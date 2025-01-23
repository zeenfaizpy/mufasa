from mufasa.core import ExecutionContext
from mufasa.functions import col, eq, lit


def main():
    ctx = ExecutionContext()
    df = (
        ctx.csv("employee.csv")
        .filter(eq(col("state"), lit("TN")))
        .project([col('state')])
    )
    df.show_plan()

if __name__ == '__main__':
    main()