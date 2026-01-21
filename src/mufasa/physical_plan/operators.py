import pyarrow as pa


class PhysicalPlan:
    def schema(self):
        raise NotImplementedError()

    def children(self):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()

    def format(self, plan=None, indent=0):
        if plan is None:
            plan = self
        plan_string = []
        for _ in range(indent):
            plan_string.append("\t".expandtabs(2))
        plan_string.append(repr(plan))
        plan_string.append("\n")
        for child_plan in plan.children():
            plan_string.append(self.format(child_plan, indent + 1))
        return "".join(plan_string)


class PhysicalScan(PhysicalPlan):
    def __init__(self, datasource, projection):
        self.datasource = datasource
        self.projection = projection
        self.plan = None

    def schema(self):
        schema = self.datasource.schema()
        # Apply projection to schema if specified
        if self.projection:
            arrow_schema = schema.to_arrow()
            projected_fields = [
                field for field in arrow_schema
                if field.name in self.projection
            ]
            return pa.schema(projected_fields)
        return schema.to_arrow()

    def children(self):
        return []

    def execute(self):
        result = []
        # Pass projection to scan if datasource supports it
        scan_method = getattr(self.datasource, 'scan', None)
        if scan_method:
            try:
                # Try to pass projection if the method supports it
                for chunk in scan_method(self.projection):
                    if chunk is not None and chunk.num_rows > 0:
                        result.append(chunk)
            except TypeError:
                # Fallback if scan doesn't accept projection
                for chunk in scan_method():
                    if chunk is not None and chunk.num_rows > 0:
                        result.append(chunk)
        return result  # returns list of record_batches

    def __repr__(self):
        proj_str = f", projection={self.projection}" if self.projection else ""
        return f"Scan: schema={self.schema()}{proj_str}"


class PhysicalProjection(PhysicalPlan):
    def __init__(self, child, expr):
        self.child = child
        self.expr = expr
        self._schema = None  # Cache schema

    def schema(self):
        if self._schema is None:
            # Build schema from expressions
            child_schema = self.child.schema()
            fields = []
            for expr in self.expr:
                # Get the name from the expression
                name = getattr(expr, 'name', None) or getattr(expr, 'alias', None)
                if name is None:
                    name = str(expr)
                # Try to infer type from child schema or default to string
                field_type = pa.string()
                if hasattr(expr, 'evaluate'):
                    # We'd need to evaluate on a sample, but for now use string
                    pass
                fields.append(pa.field(name, field_type))
            self._schema = pa.schema(fields)
        return self._schema

    def children(self):
        return [self.child]

    def execute(self):
        batches = self.child.execute()
        result_batches = []
        for batch in batches:
            if batch.num_rows == 0:
                continue
            cols = {}
            for expr in self.expr:
                result = expr.evaluate(batch)
                # Get the name for this expression
                name = getattr(expr, 'name', None) or getattr(expr, 'alias', None)
                if name is None:
                    name = str(expr)
                cols[name] = result
            if cols:
                record_batch = pa.RecordBatch.from_arrays(
                    list(cols.values()), names=list(cols.keys())
                )
                result_batches.append(record_batch)
        return result_batches  # returns list of record_batches

    def __repr__(self):
        proj_str = ", ".join([repr(e) for e in self.expr])
        return f"Projection {proj_str}"


class PhysicalFilter(PhysicalPlan):
    def __init__(self, child, expr):
        self.child = child
        self.expr = expr

    def schema(self):
        return self.child.schema()

    def children(self):
        return [self.child]

    def execute(self):
        batches = self.child.execute()
        result_batches = []
        for batch in batches:
            if batch.num_rows == 0:
                continue
            cond_result = self.expr.evaluate(batch)
            # Filter the batch using the condition
            filtered = batch.filter(cond_result)
            if filtered.num_rows > 0:
                result_batches.append(filtered)
        return result_batches  # returns list of record_batch

    def __repr__(self):
        return f"Filter {self.expr}"


class PhysicalGroupBy(PhysicalPlan):
    def __init__(self, child, group_exprs, agg_exprs):
        self.child = child
        self.group_exprs = group_exprs
        self.agg_exprs = agg_exprs
        self._schema = None

    def schema(self):
        if self._schema is None:
            # Build schema from group and agg expressions
            child_schema = self.child.schema()
            fields = []
            # Add group columns
            for expr in self.group_exprs:
                name = getattr(expr, 'name', None) or str(expr)
                # Try to find type in child schema
                field_type = pa.string()
                try:
                    field = child_schema.field(name)
                    field_type = field.type
                except KeyError:
                    pass
                fields.append(pa.field(name, field_type))
            # Add aggregate columns
            for expr in self.agg_exprs:
                name = getattr(expr, 'name', None) or str(expr)
                # Aggregates typically return numeric types
                field_type = pa.float64()
                fields.append(pa.field(name, field_type))
            self._schema = pa.schema(fields)
        return self._schema

    def children(self):
        return [self.child]

    def execute(self):
        batches = self.child.execute()
        if not batches:
            return []
        
        # Optimized: Combine all batches into a single table for efficient aggregation
        # This is more efficient than processing batches separately
        table = pa.Table.from_batches(batches)

        # Get group column names
        group_exprs_names = [getattr(expr, 'name', None) or str(expr) for expr in self.group_exprs]
        
        # Validate that group columns exist
        table_cols = set(table.column_names)
        valid_group_cols = [col for col in group_exprs_names if col in table_cols]
        if not valid_group_cols:
            raise ValueError(f"Group columns {group_exprs_names} not found in table")
        
        # Group the table
        grouped_table = table.group_by(valid_group_cols)

        # Build aggregation expressions for PyArrow
        agg_exprs_list = []
        for agg_expr in self.agg_exprs:
            expr_name = getattr(agg_expr.expr, 'name', None) or str(agg_expr.expr)
            if expr_name not in table_cols:
                continue
            
            agg_name = getattr(agg_expr, 'name', None) or 'UNKNOWN'
            # Map our aggregate names to PyArrow function names
            agg_func_map = {
                'MAX': 'max',
                'MIN': 'min',
                'SUM': 'sum',
                'AVG': 'mean',
                'COUNT': 'count',
            }
            pyarrow_func = agg_func_map.get(agg_name.upper(), 'sum')
            agg_exprs_list.append((expr_name, pyarrow_func))

        if not agg_exprs_list:
            # If no valid aggregates, just return grouped keys
            result_table = grouped_table.aggregate([])
        else:
            # Perform aggregation in a single call
            result_table = grouped_table.aggregate(agg_exprs_list)

        # Convert back to batches
        result_batches = result_table.to_batches(max_chunksize=8192)
        return result_batches  # returns list of record_batches

    def __repr__(self):
        group_str = ", ".join([repr(e) for e in self.group_exprs])
        agg_str = ", ".join([repr(e) for e in self.agg_exprs])
        return f"GroupBy(group_cols=[{group_str}], agg_exprs=[{agg_str}])"
