import pytest
from core.registry import TypeRegistry

def test_register_type_success():
    registry = TypeRegistry()
    registry.register_type("Player", {"type": "object", "fields": {"id": "number", "name": "string"}})
    
    assert "Player" in registry.types
    assert "Player" in registry.object_defs
    assert registry.object_defs["Player"]["type"] == "object"

def test_register_type_duplicate():
    registry = TypeRegistry()
    registry.register_type("Vector3", {"type": "object", "fields": {"x": "number", "y": "number", "z": "number"}})
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register_type("Vector3", {"type": "object"})

def test_resolve_type_builtin():
    registry = TypeRegistry()
    # Built-ins should resolve even if not explicitly registered
    resolved = registry.resolve_type("string")
    assert resolved == {"type": "string"}

def test_resolve_type_not_found():
    registry = TypeRegistry()
    with pytest.raises(ValueError, match="not found in registry"):
        registry.resolve_type("UnknownType")

def test_resolve_type_circular_dependency():
    registry = TypeRegistry()
    # Create a circular dependency
    registry.register_type("Node", {
        "type": "object",
        "fields": {
            "value": "number",
            "next": "Node"
        }
    })
    
    with pytest.raises(ValueError, match="Circular dependency detected"):
        registry.resolve_type("Node")

def test_generate_identifier():
    id1 = TypeRegistry.generate_identifier("PlayerJoin", '{"id":"number"}')
    id2 = TypeRegistry.generate_identifier("PlayerJoin", '{"id":"number"}')
    id3 = TypeRegistry.generate_identifier("PlayerLeave", '{"id":"number"}')
    
    assert id1 == id2
    assert id1 != id3
    assert len(id1) == 8
