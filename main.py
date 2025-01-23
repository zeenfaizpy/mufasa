from mufasa.core import ExecutionContext
from mufasa.functions import col, eq, lit


def main():
    ctx = ExecutionContext()
    df = (
        ctx.csv("employee.csv")
        .filter(eq(col("state"), lit("TN")))
        .select(col('state'), col('first_name'), col('last_name'))
    )
    df.show_plan()

if __name__ == '__main__':
    main()