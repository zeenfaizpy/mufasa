from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Dict, Optional, Tuple
from tabulate import tabulate
from mufasa.logical_plan.operators import Projection, Filter, GroupBy
from mufasa.functions import col, count, lit, sum, avg, min, max

if TYPE_CHECKING:
    from ..execution.context import ExecutionContext
    from ..logical_plan.operators import LogicalPlan
    from ..logical_plan.expressions import LogicalExpr


class DataFrame:
    """
    A DataFrame represents a distributed collection of data organized into named columns.
    It provides a domain-specific language for structured data manipulation.
    """

    def __init__(self, ctx: ExecutionContext, plan: LogicalPlan) -> None:
        """
        Initialize a DataFrame.

        Args:
            ctx: The execution context.
            plan: The logical plan representing the operations on this DataFrame.
        """
        self.ctx = ctx
        self.plan = plan

    def create_or_replace_table(self, name: str) -> DataFrame:
        """
        Register this DataFrame as a table in the catalog.

        Args:
            name: The name of the table.

        Returns:
            A new DataFrame representing the registered table.
        """
        self.ctx.register_table(name, self)
        return DataFrame(self.ctx, self.plan)

    def select(self, *args: LogicalExpr) -> DataFrame:
        """
        Project a set of expressions and return a new DataFrame.

        Args:
            *args: Column expressions to select.

        Returns:
            A new DataFrame with the selected columns.
        """
        logical_plan = Projection(self.plan, list(args))
        return DataFrame(self.ctx, logical_plan)

    def filter(self, expr: LogicalExpr) -> DataFrame:
        """
        Filter rows using the given condition.

        Args:
            expr: The condition expression.

        Returns:
            A filtered DataFrame.
        """
        logical_plan = Filter(self.plan, expr)
        return DataFrame(self.ctx, logical_plan)

    def group_by(self, *group_exprs: LogicalExpr) -> GroupedDataFrame:
        """
        Group the DataFrame using the specified columns.

        Args:
            *group_exprs: Expressions to group by.

        Returns:
            A GroupedDataFrame object.
        """
        return GroupedDataFrame(self, list(group_exprs))

    def schema(self) -> Any:
        """
        Returns the schema of this DataFrame.
        """
        return self.plan.schema()

    def logical_plan(self) -> LogicalPlan:
        """
        Returns the logical plan of this DataFrame.
        """
        return self.plan

    def show_plan(self) -> None:
        """
        Prints the logical plan to the console.
        """
        plan_str = self.plan.format()
        print(plan_str)

    def collect(self) -> List[Dict[str, Any]]:
        """
        Execute the query and return the results as a list of dictionaries.

        Returns:
            A list of dictionaries representing the rows.
        """
        data = self.ctx.execute(self)
        # Assuming execute returns a list of batches or similar, and we want the first one converted
        # This logic mimics the original but returns instead of printing
        if not data:
            return []
        
        # Depending on what ctx.execute returns (likely pyarrow tables/batches based on imports in other files)
        # The original code did: data = data[0]; data = data.to_pylist()
        # We'll stick to that logic but make it safer
        result_data = data[0]
        return result_data.to_pylist()

    def show(self) -> None:
        """
        Execute the query and print the results to the console.
        """
        data = self.collect()
        print(tabulate(data, headers="keys", tablefmt="pretty"))


class GroupedDataFrame:
    """
    A DataFrame that has been grouped by one or more columns.
    """

    def __init__(self, df: DataFrame, group_exprs: List[LogicalExpr]) -> None:
        """
        Initialize a GroupedDataFrame.

        Args:
            df: The source DataFrame.
            group_exprs: The expressions used for grouping.
        """
        self.df = df
        self.group_exprs = group_exprs

    def agg(self, *agg_exprs: LogicalExpr) -> DataFrame:
        """
        Compute aggregates and return the result as a DataFrame.

        Args:
            *agg_exprs: Aggregate expressions.

        Returns:
            A new DataFrame with the aggregated results.
        """
        logical_plan = GroupBy(self.df.plan, self.group_exprs, list(agg_exprs))
        return DataFrame(self.df.ctx, logical_plan)

    def show_plan(self) -> None:
        """
        Prints the logical plan to the console.
        """
        self.df.show_plan()

    def collect(self) -> List[Dict[str, Any]]:
        """
        Execute the query and return the results.
        """
        return self.df.collect()

    def count(self) -> DataFrame:
        """
        Count the number of rows in each group.
        """
        return self.agg(count(lit(1)))

    def sum(self, col_name: str) -> DataFrame:
        """
        Compute the sum for each group.
        """
        return self.agg(sum(col(col_name)))

    def avg(self, col_name: str) -> DataFrame:
        """
        Compute the average for each group.
        """
        return self.agg(avg(col(col_name)))

    def min(self, col_name: str) -> DataFrame:
        """
        Compute the min for each group.
        """
        return self.agg(min(col(col_name)))

    def max(self, col_name: str) -> DataFrame:
        """
        Compute the max for each group.
        """
        return self.agg(max(col(col_name)))
