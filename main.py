from mufasa.core import ExecutionContext
from mufasa.functions import col, lit, gt


def main():
    ctx = ExecutionContext()
    df = (
        ctx.csv("employees.csv", has_headers=True, batch_size=4)
        # .filter(eq(col("state"), lit("TN")))
        .filter(gt(col("salary"), lit(12000)))
        .select(col('state'), col('first_name'), col('salary'))
    )
    # df.show_plan()
    df.collect()

if __name__ == '__main__':
    main()