from mufasa.core import ExecutionContext
from mufasa.functions import *


def main():
    ctx = ExecutionContext()
    # df = (
    #     ctx.csv("examples/employees.csv", has_headers=True, batch_size=4)
    #     .filter(eq(col("state"), lit("TN")))
    #     .filter(gt(col("salary"), lit(12000)))
    #     .select(col('state'), col('first_name'), col('salary'))
    #     .select(count(col('state')))
    # )

    # df = (
    #     ctx.csv("examples/employees.csv", has_headers=True, batch_size=4)
    #     .group_by(col('dept'))
    #     .agg(sum(col('salary')))
    # )

    df = (
        ctx.csv("examples/employees.csv", has_headers=True, batch_size=4)
        .filter(col("salary").gt(lit(12000)))
    )
    df.show_plan()
    df.collect()

if __name__ == '__main__':
    main()