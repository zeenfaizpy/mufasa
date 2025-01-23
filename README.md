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
    .project([col('state')])
)
df.show_plan()
```
