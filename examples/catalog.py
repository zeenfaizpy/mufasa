from mufasa.core import ExecutionContext
from mufasa.functions import *


def main():
    ctx = ExecutionContext()
    df = ctx.csv("examples/employees.csv", has_headers=True, batch_size=4)
    # df = df.filter(gt(col('salary'), lit(10000)))
    df.create_or_replace_table('employees')

    # df.show_plan()
    # df.collect()

    # new_df = ctx.sql("select first_name, salary from employees where salary > 10000")
    new_df = ctx.sql("select dept, sum(salary) from employees where salary > 10000 group by dept")
    new_df.show_plan()
    new_df.collect()

if __name__ == '__main__':
    main()