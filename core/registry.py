import json
import hashlib
from typing import Dict, Any, List, Set
from .ir_models import TypeRef

class TypeRegistry:
    def __init__(self):
        self.types: Dict[str, Any] = {}
        self.enum_defs: Dict[str, Any] = {}
        self.object_defs: Dict[str, Any] = {}
        self._resolution_stack: Set[str] = set()

    def register_type(self, name: str, typedef: Any):
        if name in self.types:
            raise ValueError(f"Type '{name}' already registered.")
        
        # Determine kind and validate structure quickly
        if isinstance(typedef, dict):
            if "type" in typedef:
                kind = typedef["type"]
                if kind == "enum":
                     self.enum_defs[name] = typedef
                elif kind == "object":
                     self.object_defs[name] = typedef
                else:
                     # Primitive or primitive wrapper
                     pass
        
        self.types[name] = typedef

    def resolve_type(self, name: str) -> Any:
        # Detects cycles while resolving
        if name in self._resolution_stack:
            raise ValueError(f"Circular dependency detected for type '{name}'. Stack: {self._resolution_stack}")
        
        if name not in self.types:
            # Check built-in primitives. We might consider 'string', 'number', 'boolean' as builtins
            if name in ["string", "number", "boolean", "int", "float"]:
                 return {"type": name}
            raise ValueError(f"Type '{name}' not found in registry.")

        self._resolution_stack.add(name)
        typedef = self.types[name]
        
        # Deep resolve if it's an object with fields
        if isinstance(typedef, dict) and typedef.get("type") == "object":
            resolved_fields = {}
            for fname, ftype in typedef.get("fields", {}).items():
                if isinstance(ftype, str):
                    self.resolve_type(ftype) # Ensure it resolves
                    resolved_fields[fname] = ftype
                elif isinstance(ftype, dict) and "ref" in ftype:
                    ref_name = ftype["ref"]
                    self.resolve_type(ref_name)
                    resolved_fields[fname] = ftype
                else:
                    resolved_fields[fname] = ftype
            typedef["fields"] = resolved_fields
            
        self._resolution_stack.remove(name)
        return typedef

    def clear(self):
        self.types.clear()
        self.enum_defs.clear()
        self.object_defs.clear()
        self._resolution_stack.clear()

    @staticmethod
    def generate_identifier(event_name: str, payload_schema: str) -> str:
        """Generates a deterministic ID for an event/type based on name + schema hash."""
        hasher = hashlib.sha256()
        hasher.update(event_name.encode('utf-8'))
        hasher.update(payload_schema.encode('utf-8'))
        # Take first 8 chars of hex digest for short deterministic ID
        return hasher.hexdigest()[:8]
