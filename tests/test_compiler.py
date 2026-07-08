import sys
from pathlib import Path

# Add roblox-bridge to sys.path to enable loading emitters
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "roblox-bridge"))

import pytest
from core.compiler import Compiler
from emitters.luau_emitter import LuauEmitter

def test_compile_and_emit_list_schema():
    schema = {
        "version": "1.0.0",
        "events": [
            {
                "name": "TestEvent",
                "payload": {
                    "player": "string",
                    "score": "number",
                    "tags": "string[]",
                    "metadata": "string?"
                }
            }
        ]
    }
    
    compiler = Compiler()
    ir = compiler.compile_schema(schema)
    
    assert len(ir.events) == 1
    event = ir.events[0]
    assert event.name == "TestEvent"
    
    # Ensure fields are mapped and optimized sorting is applied deterministically
    assert len(event.fields) == 4
    # Fields will be sorted: metadata, player, score, tags
    field_names = [f.name for f in event.fields]
    assert field_names == ["metadata", "player", "score", "tags"]
    
    # Verify field types
    fields_dict = {f.name: f for f in event.fields}
    assert fields_dict["metadata"].type == "string?"
    assert fields_dict["player"].type == "string"
    assert fields_dict["score"].type == "number"
    assert fields_dict["tags"].type == "{string}"
    
    # Emit code
    emitter = LuauEmitter()
    files = emitter.emit(ir)
    
    assert "Types.luau" in files
    assert "ClientBridge.luau" in files
    assert "ServerBridge.luau" in files
    assert "Validators.luau" in files
    
    types_content = files["Types.luau"]
    assert "metadata: string?" in types_content
    assert "player: string" in types_content
    assert "score: number" in types_content
    assert "tags: {string}" in types_content
    
    validators_content = files["Validators.luau"]
    assert "Validators.ValidateTestEvent" in validators_content
    assert "payload.metadata ~= nil" in validators_content
    assert "type(payload.player) ~= 'string'" in validators_content
    assert "type(payload.score) ~= 'number'" in validators_content
