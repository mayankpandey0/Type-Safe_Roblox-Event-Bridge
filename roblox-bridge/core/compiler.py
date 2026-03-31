class FieldIR:
    def __init__(self, name: str, field_type: str):
        self.name = name
        self.type = field_type

class EventIR:
    def __init__(self, name: str, fields: list[FieldIR]):
        self.name = name
        self.fields = fields
        self.encoding = None

def build_ir(registry, schema) -> list[EventIR]:
    ir_list = []
    for event in schema.get("events", []):
        fields = [FieldIR(k, v) for k, v in event.get("payload", {}).items()]
        ir_list.append(EventIR(event["name"], fields))
    return ir_list
