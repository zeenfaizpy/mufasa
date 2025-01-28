from sqlglot import exp, parse_one
from mufasa.logical_plan.expressions import *


# class SQLToPlan:
#     def __init__(self, query):
#         self.query = query
    
#     def parse_query(self):
#         statement = parse_one(self.query)
#         self.sql_to_plan(statement)

#     def sql_to_plan(self, statement):
#         if isinstance(statement, exp.Select):
#             self.convert_select_to_plan(statement)
#         else:
#             raise Exception("Only SELECT statement is supported")


class SQLParser:
    def __init__(self, catalog):
        self.catalog = catalog

    def parse(self, sql):
        ast = parse_one(sql)
        return self.convert_ast_to_logical_plan(ast)

    def convert_ast_to_logical_plan(self, ast):
        if isinstance(ast, exp.Select):
            return self.convert_select(ast)
        else:
            raise Exception("Unsupported SQL statement")

    def convert_select(self, select):
        # FROM clause
        from_clause = select.args.get("from")
        if not from_clause:
            raise Exception("SELECT statement must have a FROM clause")

        table_name = from_clause.this.this.this
        df = self.catalog.get_table(table_name)
        if not df:
            raise Exception(f"Table '{table_name}' not found in catalog")

        # WHERE clause
        where_clause = select.args.get("where")
        if where_clause:
            df = self.apply_filter(df, where_clause)

        # GROUP BY clause
        group_by_clause = select.args.get("group")
        if group_by_clause:
            grouped_df = self.apply_group_by(df, group_by_clause)
            agg_exprs = select.args.get("expressions")
            df = self.apply_agg(grouped_df, agg_exprs)
        else:
            # SELECT clause
            select_exprs = select.args.get("expressions")
            df = self.apply_projection(df, select_exprs)

        return df

    def apply_filter(self, df, where_clause):
        filter_expr = self.convert_expr(where_clause.this)
        return df.filter(filter_expr)

    def apply_group_by(self, df, group_by_clause):
        group_exprs = [self.convert_expr(expr) for expr in group_by_clause.expressions]
        return df.group_by(*group_exprs)
    
    def apply_agg(self, df, agg_exprs):
        projection_exprs = [self.convert_expr(expr) for expr in agg_exprs]
        return df.agg(*projection_exprs)

    def apply_projection(self, df, select_exprs):
        projection_exprs = [self.convert_expr(expr) for expr in select_exprs]
        return df.select(*projection_exprs)

    def convert_expr(self, expr):
        if isinstance(expr, exp.Column):
            return Column(expr.this.name)
        elif isinstance(expr, exp.Literal):
            return Literal(expr.this)
        elif isinstance(expr, exp.Binary):
            left = self.convert_expr(expr.left)
            right = self.convert_expr(expr.right)

            op_map = {
                exp.GT: '>',
                exp.GTE: '>=',
                exp.LT: '<',
                exp.LTE: '<=',
                exp.EQ: '=',
                exp.NEQ: '!=',
            }
            op = op_map.get(type(expr))
            if not op:
                Exception(f"Unsupported expression: {expr}")

            return Binary(expr.key, left, op, right)
        elif isinstance(expr, exp.Alias):
            return self.convert_expr(expr.this).alias(expr.alias)
        elif isinstance(expr, exp.AggFunc):
            return Aggregate(expr.key, self.convert_expr(expr.this))
        else:
            raise Exception(f"Unsupported expression: {expr}")