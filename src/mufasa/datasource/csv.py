import csv


class CSVDataSource:
    def __init__(self, filename, schema, has_headers=False, batch_size=10):
        self.filename = filename
        self.schema = schema
        self.has_headers = has_headers
        self.batch_size = batch_size
    
    def scan(self):
        with open(self.filename) as csvfile:
            reader = csv.reader(csvfile)
            
            chunk = []
            for index, line in enumerate(reader):
                if index % self.batch_size == 0 and index > 0:
                    yield chunk
                    chunk = []
                chunk.append(line)
            yield chunk


