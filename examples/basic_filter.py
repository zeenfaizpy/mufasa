from mufasa.core import ExecutionContext
from mufasa.functions import *


def main():
    ctx = ExecutionContext()
    # SELECT state, first_name, salary FROM employees WHERE state = 'TN
    df = (
        ctx.csv("examples/employees.csv", has_headers=True)
        .filter(eq(col("state"), lit("TN")))
        .select(col('state'), col('first_name'), col('salary'))
    )

    df.show_plan()
    df.collect()

if __name__ == '__main__':
    main()