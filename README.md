![Mufasa - DataFrame Library](media/banner_new.png)

[![uv](https://img.shields.io/badge/Managed_by-uv-green)](https://github.com/zeenfaizpy/mufasa)
[![license](https://img.shields.io/badge/license-MIT-yellow)](https://github.com/zeenfaizpy/mufasa)
[![license](https://img.shields.io/badge/python-3.13-blue)](https://github.com/zeenfaizpy/mufasa)

# Mufasa

## Overview
Mufasa is a Python-based distributed-like query engine and DataFrame library. It provides a domain-specific language for structured data manipulation and executes queries using an optimized physical plan backed by PyArrow. Mufasa supports a fluent DataFrame API, SQL parsing, and rule-based query optimization.

## Architecture
Mufasa follows a classic query engine architecture:
1. **DataFrame API / SQL Parser**: The front-end for users to build queries programmatically or via SQL.
2. **Logical Plan**: An abstract representation of the query operations (e.g., `Scan`, `Projection`, `Filter`, `GroupBy`).
3. **Optimizer**: Applies rule-based optimizations to the logical plan (e.g., Constant Folding, Projection Pushdown).
4. **Physical Plan**: An executable representation of the query that maps logical operations to PyArrow compute functions.
5. **Execution Context**: Manages query execution, optimization settings, and table registration (Catalog).

## Installation

```bash
pip install git+https://github.com/zeenfaizpy/mufasa.git@main
```

## Core Components

### ExecutionContext
The entry point for using Mufasa. It manages the catalog of registered tables and coordinates query execution.

```python
from mufasa.core import ExecutionContext

# Create a context (optimizations are enabled by default)
ctx = ExecutionContext(optimize=True)
```

### DataFrame
Represents a collection of data organized into named columns. DataFrames are lazy; they build a logical plan and only execute when an action like `collect()` or `show()` is called.

```python
# Create a DataFrame from a CSV file
df = ctx.csv("data.csv", has_headers=True)
```

### Catalog
Manages registered tables, allowing you to query DataFrames using standard SQL.

```python
# Register a DataFrame as a table named "my_table"
df.create_or_replace_table("my_table")

# Alternatively, using the context:
ctx.register_table("my_table", df)
```

## DataFrame API

Mufasa provides a robust API for data manipulation:

### Projections
Use `select(*args)` to project a set of expressions.

```python
from mufasa.functions import col

df.select(col("name"), col("age"))
```

### Filtering
Use `filter(expr)` to filter rows based on a boolean condition.

```python
df.filter(col("age") >= 18)
```

### Grouping and Aggregation
Use `group_by(*group_exprs)` to group the DataFrame by specified columns. This returns a `GroupedDataFrame` on which you can perform aggregations.

```python
from mufasa.functions import count, sum, avg

grouped = df.group_by(col("department"))

# Single aggregations
grouped.count()
grouped.sum("salary")

# Multiple aggregations
grouped.agg(count(col("id")), sum(col("salary")))
```

### Actions
Actions trigger the execution of the query plan:
- `show()`: Executes the query and prints the results to the console in a nicely formatted table.
- `collect()`: Executes the query and returns the results as a list of Python dictionaries.
- `show_plan()`: Prints the logical plan of the DataFrame to the console.

## SQL Support

Mufasa supports executing SQL queries against registered tables, utilizing `sqlglot` for robust SQL parsing.

```python
# 1. Load data and register it as a table
df = ctx.csv("employees.csv", has_headers=True)
df.create_or_replace_table("employees")

# 2. Execute a SQL query
result_df = ctx.sql("""
    SELECT department, AVG(salary) 
    FROM employees 
    WHERE age > 30 
    GROUP BY department
""")

# 3. Show the results
result_df.show()
```

## Optimizations

Mufasa includes a rule-based query optimizer that applies several techniques to improve query performance before physical execution:

1. **Expression Simplification**: Simplifies boolean expressions early on (e.g., `x AND True` becomes `x`).
2. **Constant Folding**: Evaluates constant expressions at compile time to save execution cycles (e.g., `1 + 2` becomes `3`).
3. **Filter Pushdown**: Pushes filters as close to the data source as possible, significantly reducing the amount of data processed in subsequent steps.
4. **Projection Pushdown**: Prunes unused columns early in the query plan to minimize data transfer overhead and memory usage during execution.

## Supported Data Types & Functions

### Expressions
Expressions are the building blocks of queries.
- `col(name)`: References a column by its name.
- `lit(value)`: Wraps a literal value (string, int, float, boolean).

### Binary Operations
Mufasa supports standard comparison and logical operators: `=`, `!=`, `>`, `>=`, `<`, `<=`, `AND`, `OR`.
These can be constructed directly using operator overloading on column expressions or via dedicated functions.

```python
# Using operator overloading
col("age") >= 18
col("department") == "Engineering"
```

### Aggregate Functions
- `count(expr)`
- `sum(expr)`
- `avg(expr)`
- `min(expr)`
- `max(expr)`

## Data Sources
Currently, Mufasa natively supports CSV files. It leverages PyArrow's optimized CSV reader (`mufasa.datasource.csv.CSVDataSource`) for fast and memory-efficient data loading, with built-in support for chunked batch reading, projection pushdown, and fast schema inference.

```python
# Load a CSV file in batches of 8192 rows
df = ctx.csv("data.csv", has_headers=True, batch_size=8192)
```

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