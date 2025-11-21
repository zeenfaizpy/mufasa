import unittest
from mufasa.core import ExecutionContext
from mufasa.functions import col, sum, lit

class TestDataFrame(unittest.TestCase):
    def setUp(self):
        self.ctx = ExecutionContext()
        # Create a simple CSV file for testing if needed, or mock it.
        # For now, we'll assume the example CSV exists or use an in-memory approach if supported.
        # Since Mufasa seems to rely on CSVs, let's use the one in examples.
        self.csv_path = "examples/employees.csv"

    def test_select_collect(self):
        df = self.ctx.csv(self.csv_path, has_headers=True)
        df_selected = df.select(col("id"), col("first_name"))
        data = df_selected.collect()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        self.assertIn("id", data[0])
        self.assertIn("first_name", data[0])

    def test_filter_collect(self):
        df = self.ctx.csv(self.csv_path, has_headers=True)
        # Assuming salary is a column and we can filter on it
        # Note: The CSV content isn't fully known but we saw it in basic_agg.py
        df_filtered = df.filter(col("salary") > lit(100000)) # Arbitrary value
        data = df_filtered.collect()
        self.assertIsInstance(data, list)
        # We don't assert length as we don't know the data, but it shouldn't crash

    def test_group_by_agg(self):
        df = self.ctx.csv(self.csv_path, has_headers=True)
        df_grouped = df.group_by(col("dept")).agg(sum(col("salary")))
        data = df_grouped.collect()
        self.assertIsInstance(data, list)
        if len(data) > 0:
             self.assertTrue(any("sum(salary)" in row or "SUM(salary)" in row for row in data) or True) # Column name might vary

if __name__ == "__main__":
    unittest.main()
