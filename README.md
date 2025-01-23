# mufasa
Musafa is simple Query Processing Engine (aka dataframe library)


It is still in development.

## Try out

```bash
pip install git+https://github.com/zeenfaizpy/mufasa.git@main
```

```python
from mufasa.core import ExecutionContext
from mufasa.functions import col, eq, lit

ctx = ExecutionContext()
df = (
    ctx.csv("employee.csv")
    .filter(eq(col("state"), lit("TN")))
    .select(col('state'), col('first_name'), col('last_name'))
)
df.show_plan()
```
