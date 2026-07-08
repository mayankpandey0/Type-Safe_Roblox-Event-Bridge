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

def test_fieldir_type_property():
    ref_simple = TypeRef(name="string")
    assert FieldIR(name="x", type_ref=ref_simple).type == "string"
    
    ref_int = TypeRef(name="int")
    assert FieldIR(name="x", type_ref=ref_int).type == "number"
    
    ref_optional = TypeRef(name="number", is_optional=True)
    assert FieldIR(name="x", type_ref=ref_optional).type == "number?"
    
    ref_array = TypeRef(name="boolean", is_array=True)
    assert FieldIR(name="x", type_ref=ref_array).type == "{boolean}"
    
    ref_both = TypeRef(name="string", is_array=True, is_optional=True)
    assert FieldIR(name="x", type_ref=ref_both).type == "{string}?"

def test_eventir_creation():
    ref = TypeRef(name="string")
    field = FieldIR(name="playerId", type_ref=ref)
    event = EventIR(name="PlayerJoin", identifier="ev_1", fields=[field], direction="ClientToServer")
    
    assert event.name == "PlayerJoin"
    assert event.direction == "ClientToServer"
    assert len(event.fields) == 1
    assert event.fields[0].name == "playerId"
    assert event.encoding == "dict"
