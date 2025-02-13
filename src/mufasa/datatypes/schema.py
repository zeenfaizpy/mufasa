import pyarrow as pa

class Field:
    def __init__(self, name: str, data_type):
        self.name = name
        self.data_type = data_type
    
    def to_arrow(self):
        return pa.field(self.name, self.data_type, nullable=False)


class Schema:
    def __init__(self, fields):
        self.fields = fields

    def to_arrow(self):
        return pa.schema([field.to_arrow() for field in self.fields])