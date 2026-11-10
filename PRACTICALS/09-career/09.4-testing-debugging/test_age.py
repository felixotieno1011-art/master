import pytest
from age_checker import can_vote

def test_valid_adult():
    assert can_vote(20) == True

def test_valid_child():
    assert can_vote(10) == False

def test_boundary_18():
    assert can_vote(18) == True

def test_boundary_17():
    assert can_vote(17) == False

def test_string_age():
    # Now we EXPECT it to raise a TypeError
    with pytest.raises(TypeError):
        can_vote("twenty")

def test_none_age():
    with pytest.raises(TypeError):
        can_vote(None)

def test_negative_age():
    with pytest.raises(ValueError):
        can_vote(-5)

def test_extremely_high_age():
    with pytest.raises(ValueError):
        can_vote(500)
