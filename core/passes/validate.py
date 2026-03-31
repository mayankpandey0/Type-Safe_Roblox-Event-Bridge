from typing import List, Dict, Any
from ..ir_models import EventIR, FieldIR, MiddlewareIR
from ..registry import TypeRegistry

class ValidatePass:
    def __init__(self, registry: TypeRegistry):
        self.registry = registry

    def execute(self, ir_list: List[EventIR]) -> List[EventIR]:
        seen_events = set()
        seen_ids = set()

        for event in ir_list:
            if event.name in seen_events:
                 raise ValueError(f"Duplicate event name detected: {event.name}")
            if event.identifier in seen_ids:
                 raise ValueError(f"Duplicate deterministic identifier detected: {event.identifier}")

            seen_events.add(event.name)
            seen_ids.add(event.identifier)
            
            # Validate Fields
            seen_fields = set()
            for field in event.fields:
                 if field.name in seen_fields:
                     raise ValueError(f"Duplicate field name '{field.name}' in event '{event.name}'")
                 seen_fields.add(field.name)

                 # Validate Type (redundant with resolve_type, but ensures safety)
                 if field.type_ref.name not in ["string", "number", "boolean", "int", "float"]:
                     if field.type_ref.name not in self.registry.types:
                          raise ValueError(f"Unknown type '{field.type_ref.name}' in field '{field.name}' of event '{event.name}'")
            
            # Validate Middleware (basic structure check)
            for mw in event.middleware:
                if not isinstance(mw.name, str) or not mw.name:
                    raise ValueError(f"Invalid middleware name in event '{event.name}'")

        return ir_list
