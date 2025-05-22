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
            plan_string.append(self.format(child_plan, indent+1))
        return "".join(plan_string)


class PhysicalScan(PhysicalPlan):
    def __init__(self, datasource, projection):
        self.datasource = datasource
        self.projection = projection
        self.plan = None

    def schema(self):
        return self.datasource.schema()

    def children(self):
        return []
    
    def execute(self):
        result = []
        for chunk in self.datasource.scan():
            result.append(chunk)
        return result # returns list of record_batches

    def __repr__(self):
        return f"Scan: schema={self.schema()}; projection={self.projection}"


class PhysicalProjection(PhysicalPlan):
    def __init__(self, child, expr):
        self.child = child
        self.expr = expr

    def schema(self):
        return self.child.schema

    def children(self):
        return [self.child]

    def execute(self):
        batches = self.child.execute()
        result_batches = []
        for batch in batches:
            cols = {}
            for expr in self.expr:
                result = expr.evaluate(batch)
                cols[expr.name] = result
            record_batch = pa.RecordBatch.from_arrays(list(cols.values()), names=list(cols.keys()))
            result_batches.append(record_batch)
        return result_batches # returns list of record_batches

    def __repr__(self):
        proj_str = ", ".join([repr(e) for e in self.expr])
        return f"Projection {proj_str}"


class PhysicalFilter(PhysicalPlan):
    def __init__(self, child, expr):
        self.child = child
        self.expr = expr

    def schema(self):
        return self.child.schema

    def children(self):
        return [self.child]
    
    def execute(self):
        batches = self.child.execute()
        result_batches = []
        for batch in batches:
            cond_result = self.expr.evaluate(batch)
            result = batch.filter(cond_result)
            result_batches.append(result)
        return result_batches # returns list of record_batch

    def __repr__(self):
        proj_str = ", ".join([repr(e) for e in self.expr])
        return f"Projection {proj_str}"


class PhysicalGroupBy(PhysicalPlan):
    def __init__(self, child, group_exprs, agg_exprs):
        self.child = child
        self.group_exprs = group_exprs
        self.agg_exprs = agg_exprs

    def schema(self):
        return self.child.schema

    def children(self):
        return [self.child]

    def execute(self):
        batches = self.child.execute()
        # TODO: record batches have no support for group operations.
        # so converting to table to achieve and then back to batches for 
        # temporary workaround
        table = pa.Table.from_batches(batches)

        # applying group expressions
        group_exprs_names = [expr.name for expr in self.group_exprs]
        grouped_table = table.group_by(group_exprs_names)

        # applying agg expressions
        agg_results = []
        for agg_expr in self.agg_exprs:
            if agg_expr.name not in group_exprs_names: # excluding grouped column
                # print(agg_expr.expr.name, agg_expr.name.lower())
                result = grouped_table.aggregate([(agg_expr.expr.name, agg_expr.name.lower())])
                # print(result)
                agg_results.append(result)
        
        final_table = pa.concat_tables(agg_results)
        result_batches = final_table.to_batches()
        return result_batches # returns list of record_batches

    def __repr__(self):
        group_str = ", ".join([repr(e) for e in self.group_exprs])
        agg_str = ", ".join([repr(e) for e in self.agg_exprs])
        return f"GroupBy(group_cols=[{group_str}], agg_exprs=[{agg_str}])"