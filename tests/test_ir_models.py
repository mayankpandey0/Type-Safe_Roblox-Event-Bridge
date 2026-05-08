from core.ir_models import TypeRef, FieldIR, EventIR

def test_typeref_creation():
    ref = TypeRef(name="string", is_array=True, is_optional=False)
    assert ref.name == "string"
    assert ref.is_array is True
    assert ref.is_optional is False

def test_fieldir_creation():
    ref = TypeRef(name="number")
    field = FieldIR(name="health", type_ref=ref, default_value=100)
    assert field.name == "health"
    assert field.type_ref.name == "number"
    assert field.default_value == 100

def test_eventir_creation():
    ref = TypeRef(name="string")
    field = FieldIR(name="playerId", type_ref=ref)
    event = EventIR(name="PlayerJoin", identifier="ev_1", fields=[field], direction="ClientToServer")
    
    assert event.name == "PlayerJoin"
    assert event.direction == "ClientToServer"
    assert len(event.fields) == 1
    assert event.fields[0].name == "playerId"
