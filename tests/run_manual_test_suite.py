import sys
from pathlib import Path
import yaml
import json

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.append(str(project_root / "roblox-bridge"))

from core.compiler import Compiler
from core.ir_models import EventIR, FieldIR, TypeRef
from core.passes.validate import ValidatePass
from core.registry import TypeRegistry
from emitters.luau_emitter import LuauEmitter

def run_test_1():
    schema = yaml.safe_load("""
version: '1.0.0'
events:
  TestEvent:
    fields:
      player: string
      score: number
    direction: ClientToServer
""")
    c = Compiler()
    ir = c.compile_schema(schema)
    assert len(ir.events) == 1
    ev = ir.events[0]
    assert ev.name == "TestEvent"
    assert ev.direction == "ClientToServer"
    assert len(ev.fields) == 2
    # Verify deterministic identifier
    assert len(ev.identifier) == 8
    print(f"Test 1 PASS: id={ev.identifier} fields=player({ev.fields[0].type}), score({ev.fields[1].type})")

def run_test_2():
    schema = yaml.safe_load("""
version: "1.0.0"
events:
  PlayerJoin:
    fields:
      playerId: number
      username: string
    direction: ClientToServer
  PlayerLeave:
    fields:
      playerId: number
    direction: ClientToServer
""")
    c = Compiler()
    ir = c.compile_schema(schema)
    assert len(ir.events) == 2
    ev1 = next(e for e in ir.events if e.name == "PlayerJoin")
    ev2 = next(e for e in ir.events if e.name == "PlayerLeave")
    print(f"Test 2 PASS: PlayerJoin id={ev1.identifier}, PlayerLeave id={ev2.identifier}")

def run_test_3():
    schema = yaml.safe_load("""
version: "1.0.0"
events:
  InventoryUpdate:
    fields:
      items: "string[]"
    direction: ServerToClient
""")
    c = Compiler()
    ir = c.compile_schema(schema)
    assert len(ir.events) == 1
    ev = ir.events[0]
    items_field = ev.fields[0]
    assert items_field.type_ref.is_array is True
    print(f"Test 3 PASS: items array={items_field.type_ref.is_array}")

def run_test_4():
    schema = yaml.safe_load("""
version: "1.0.0"
events:
  ChatMessage:
    fields:
      text: string
      channel: "string?"
    direction: Bidirectional
""")
    c = Compiler()
    ir = c.compile_schema(schema)
    assert len(ir.events) == 1
    ev = ir.events[0]
    # Fields order is sorted alphabetically by OptimizePass
    assert ev.fields[0].name == "channel"
    assert ev.fields[1].name == "text"
    assert ev.fields[0].type_ref.is_optional is True
    assert ev.fields[1].type_ref.is_optional is False
    print(f"Test 4 PASS: channel optional={ev.fields[0].type_ref.is_optional}")

def run_test_5():
    schema = yaml.safe_load("""
version: "1.0.0"
types:
  Vector3:
    type: object
    fields:
      x: number
      y: number
      z: number
events:
  PlayerMove:
    fields:
      position: Vector3
    direction: ClientToServer
""")
    c = Compiler()
    ir = c.compile_schema(schema)
    assert len(ir.events) == 1
    ev = ir.events[0]
    assert ev.fields[0].type_ref.name == "Vector3"
    print(f"Test 5 PASS: position type={ev.fields[0].type_ref.name}")

def run_test_6():
    schema = yaml.safe_load("""
version: "1.0.0"
types:
  TeamColor:
    type: enum
    values: [Red, Blue]
events:
  TeamAssign:
    fields:
      team: TeamColor
    direction: ServerToClient
""")
    c = Compiler()
    ir = c.compile_schema(schema)
    assert len(ir.events) == 1
    ev = ir.events[0]
    assert ev.fields[0].type_ref.name == "TeamColor"
    print(f"Test 6 PASS: team type={ev.fields[0].type_ref.name}")

def run_test_7():
    try:
        vp = ValidatePass(TypeRegistry())
        ev1 = EventIR(name="Foo", identifier="id1", fields=[], direction="ClientToServer")
        ev2 = EventIR(name="Foo", identifier="id2", fields=[], direction="ClientToServer")
        vp.execute([ev1, ev2])
        print("Test 7 FAIL: duplicate event name not rejected")
    except ValueError as e:
        print(f"Test 7 PASS: {e}")

def run_test_8():
    try:
        vp = ValidatePass(TypeRegistry())
        ref = TypeRef(name="string")
        ev = EventIR(name="DupFieldEvent", identifier="idX",
                     fields=[FieldIR(name="player", type_ref=ref), FieldIR(name="player", type_ref=ref)],
                     direction="ClientToServer")
        vp.execute([ev])
        print("Test 8 FAIL: duplicate field name not rejected")
    except ValueError as e:
        print(f"Test 8 PASS: {e}")

def run_test_9():
    try:
        schema = yaml.safe_load("""
version: "1.0.0"
events:
  BadEvent:
    fields:
      thing: NotARealType
    direction: ClientToServer
""")
        c = Compiler()
        c.compile_schema(schema)
        print("Test 9 FAIL: undefined type not rejected")
    except ValueError as e:
        print(f"Test 9 PASS: {e}")

def run_test_10():
    try:
        schema = yaml.safe_load("""
version: "1.0.0"
types:
  Node:
    type: object
    fields:
      value: number
      next: Node
events:
  NodeEvent:
    fields:
      node: Node
    direction: ClientToServer
""")
        c = Compiler()
        c.compile_schema(schema)
        print("Test 10 FAIL: circular dependency not rejected")
    except ValueError as e:
        print(f"Test 10 PASS: {e}")

def run_bug_a():
    try:
        schema = yaml.safe_load("""
events:
  - name: TestEvent
    payload:
      player: string
      score: number
""")
        c = Compiler()
        ir = c.compile_schema(schema)
        assert len(ir.events) == 1
        assert ir.events[0].name == "TestEvent"
        print("Bug A PASS: list schema compiled successfully")
    except Exception as e:
        print(f"Bug A FAIL: {e}")

def run_bug_b():
    try:
        # Verify emitter output runs successfully as well
        schema = yaml.safe_load("""
events:
  - name: TestEvent
    payload:
      player: string
      score: number
""")
        c = Compiler()
        ir = c.compile_schema(schema)
        emitter = LuauEmitter()
        files = emitter.emit(ir)
        assert "Types.luau" in files
        assert "Validators.luau" in files
        print("Bug B PASS: emitter completed successfully on list IR")
    except Exception as e:
        print(f"Bug B FAIL: {e}")

if __name__ == "__main__":
    print("=== RUNNING MANUAL TEST SUITE ===")
    run_test_1()
    run_test_2()
    run_test_3()
    run_test_4()
    run_test_5()
    run_test_6()
    run_test_7()
    run_test_8()
    run_test_9()
    run_test_10()
    run_bug_a()
    run_bug_b()
    print("=== RUN COMPLETED ===")
