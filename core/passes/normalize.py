import json
from typing import Dict, Any, List
from ..ir_models import EventIR, FieldIR, TypeRef, MiddlewareIR
from ..registry import TypeRegistry

class NormalizePass:
    def __init__(self, registry: TypeRegistry):
        self.registry = registry

    def execute(self, ast: Dict[str, Any]) -> List[EventIR]:
        # Expand references, identify cycles, flatten objects
        events_ir = []
        events_raw = ast.get("events", {})
        if isinstance(events_raw, list):
            event_items = []
            for item in events_raw:
                if isinstance(item, dict) and "name" in item:
                    item_name = item["name"]
                    event_items.append((item_name, item))
        elif isinstance(events_raw, dict):
            event_items = list(events_raw.items())
        else:
            event_items = []

        for event_name, event_data in event_items:
            fields = []
            fields_data = event_data.get("fields", event_data.get("payload", {}))
            for fname, fdata in (fields_data or {}).items():
                is_array = False
                is_optional = False
                
                type_name = fdata
                if isinstance(fdata, dict):
                    type_name = fdata.get("type", "string")
                    is_array = fdata.get("array", False)
                    is_optional = fdata.get("optional", False)
                elif isinstance(fdata, str) and fdata.endswith("[]"):
                    type_name = fdata[:-2]
                    is_array = True
                elif isinstance(fdata, str) and fdata.endswith("?"):
                    type_name = fdata[:-1]
                    is_optional = True

                # Fully resolve the type_name to confirm it exists and to detect cycles
                try:
                    self.registry.resolve_type(type_name)
                except ValueError as e:
                     # Bubble up the resolution error
                     raise e
                
                type_ref = TypeRef(name=type_name, is_array=is_array, is_optional=is_optional)
                fields.append(FieldIR(name=fname, type_ref=type_ref))

            direction = event_data.get("direction", "Bidirectional")
            
            middleware_list = []
            for mw in event_data.get("middleware", []):
                if isinstance(mw, str):
                    middleware_list.append(MiddlewareIR(name=mw))
                elif isinstance(mw, dict):
                    m_name = list(mw.keys())[0] # assuming single key dict
                    m_args = mw[m_name]
                    middleware_list.append(MiddlewareIR(name=m_name, args=m_args))

            # Generate deterministic ID
            # Use JSON serialization of event definition for hash
            schema_hash_payload = json.dumps(event_data, sort_keys=True)
            identifier = TypeRegistry.generate_identifier(event_name, schema_hash_payload)

            event_ir = EventIR(
                name=event_name,
                identifier=identifier,
                fields=fields,
                direction=direction,
                middleware=middleware_list
            )
            events_ir.append(event_ir)
            
        return events_ir
