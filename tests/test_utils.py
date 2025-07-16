from app.engine.utils import Position, string_to_position, position_to_string

def test_string_to_position():
    assert string_to_position("a1") == Position(0, 7)
    assert string_to_position("h8") == Position(7, 0)
    assert string_to_position("e4") == Position(4, 4)
    assert string_to_position("d5") == Position(3, 3)
    assert string_to_position("z9") is None
    assert string_to_position("a9") is None
    assert string_to_position("i1") is None
    assert string_to_position("") is None
    assert string_to_position("a") is None
    assert string_to_position("11") is None

def test_position_to_string():
    assert position_to_string(Position(0, 7)) == "a1"
    assert position_to_string(Position(7, 0)) == "h8"
    assert position_to_string(Position(4, 4)) == "e4"
    assert position_to_string(Position(3, 3)) == "d5"