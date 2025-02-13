# mufasa
Musafa is simple Query Processing Engine (aka dataframe library)


WIP: It is still in development.

## Installation

```bash
pip install git+https://github.com/zeenfaizpy/mufasa.git@main
```

## Usage

```python
from mufasa.core import ExecutionContext
from mufasa.functions import col, eq, lit

ctx = ExecutionContext()
df = (
    ctx.csv("employee.csv")
    .select(col('state'), col('first_name'), col('last_name'))
)

# where
df = df.filter(col("salary").gt(lit(12000)))

# group by and aggregations
df = (
    df.group_by(col('dept'))
    .agg(sum(col('salary')))
)

# save it to temp table, then query using sql
df.create_or_replace_table('employees')
new_df = ctx.sql("select first_name, salary from employees where salary > 10000")


# print the logical plan
df.show_plan()

# print the final data
df.collect()
```

## Features

- Dataframe API
- Full SQL Support with catalog
- Pyspark Compatible API

## License
The GNU license. Please check `LICENSE` for more details.