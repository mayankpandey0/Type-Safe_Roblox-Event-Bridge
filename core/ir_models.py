from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class TypeRef:
    name: str
    is_array: bool = False
    is_optional: bool = False

@dataclass
class FieldIR:
    name: str
    type_ref: TypeRef
    default_value: Any = None

@dataclass
class MiddlewareIR:
    name: str
    args: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EventIR:
    name: str
    identifier: str
    fields: List[FieldIR]
    direction: str  # "ClientToServer", "ServerToClient", "Bidirectional"
    middleware: List[MiddlewareIR] = field(default_factory=list)

@dataclass
class SchemaIR:
    version: str
    types: Dict[str, Any]
    events: List[EventIR]
