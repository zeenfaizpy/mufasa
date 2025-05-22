[![uv](https://img.shields.io/badge/Managed_by-uv-green)](https://github.com/zeenfaizpy/mufasa)
[![license](https://img.shields.io/badge/license-MIT-yellow)](https://github.com/zeenfaizpy/mufasa)
[![license](https://img.shields.io/badge/python-3.13-blue)](https://github.com/zeenfaizpy/mufasa)

# mufasa

Musafa is simple Query Processing Engine (aka dataframe library)


WIP: It is still in development.

<img src="not-by-ai.png" alt="not-by-ai" width="150"/>

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
- SQL Support with catalog
- Pyspark Compatible API


## SQL Operations

- [x] FROM
- [x] WHERE
- [x] SELECT
- [x] GROUP BY
- [ ] HAVING
- [ ] JOIN
- [ ] SubQueries
- [ ] CTE
- [ ] Window Functions
- [ ] CASE


## License
The GNU license. Please check `LICENSE` for more details.