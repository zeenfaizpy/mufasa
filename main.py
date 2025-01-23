from mufasa.core import ExecutionContext
from mufasa.functions import col, eq, lit


def main():
    ctx = ExecutionContext()
    df = (
        ctx.csv("employees.csv", has_headers=True, batch_size=4)
        # .filter(eq(col("state"), lit("TN")))
        .select(col('state'), col('first_name'))
    )
    # df.show_plan()
    print(df.collect())

if __name__ == '__main__':
    main()