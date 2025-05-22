from mufasa.core import ExecutionContext
from mufasa.functions import *


def main():
    ctx = ExecutionContext()
    # SELECT SUM(salary) FROM employees group by dept
    df = (
        ctx.csv("examples/employees.csv", has_headers=True)
        .group_by(col('dept'))
        .agg(sum(col('salary')))
    )
    df.show_plan()
    df.collect()

if __name__ == '__main__':
    main()