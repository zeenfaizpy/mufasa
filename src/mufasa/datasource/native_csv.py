import csv
import pyarrow as pa
from mufasa.datatypes.schema import Field, Schema

class CSVDataSource:
    def __init__(self, filename, has_headers=False, batch_size=10):
        self.filename = filename
        self.has_headers = has_headers
        self.batch_size = batch_size
    
    def schema(self):
        return self.infer_schema()
    
    def scan(self, projection=None):
        schema = self.schema().to_arrow()
        with open(self.filename) as csvfile:
            reader = csv.reader(csvfile)
            
            chunk = []
            for index, line in enumerate(reader):
                if index == 0 and self.has_headers:
                    continue
                if index > 0 and (index % self.batch_size == 0):
                    yield pa.record_batch(line, schema=schema)
                    chunk = []
                chunk.append(line)
            yield chunk
    
    def infer_schema(self):
        with open(self.filename) as csvfile:
            reader = csv.reader(csvfile)
            schema = None
            for index, line in enumerate(reader):
                if index == 0:
                    if self.has_headers:
                        fields = [Field(col_name, pa.string()) for col_name in line]
                    else:
                        fields = [Field(f"_{index}", pa.string()) for index, _ in enumerate(line)]
                    schema = Schema(fields)
                    break
            return schema