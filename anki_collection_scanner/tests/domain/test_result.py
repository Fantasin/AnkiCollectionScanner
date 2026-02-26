
import pytest 

from anki_collection_scanner.domain.result import Result

def test_ok_result():
    r = Result.ok(42)
    assert r.is_ok()
    assert not r.is_err()
    assert r.unwrap() == 42


def test_err_result():
    r = Result.err("fail")
    assert r.is_err()
    assert not r.is_ok()
    assert r.unwrap_err() == "fail"


def test_invalid_construction():
    with pytest.raises(ValueError):
        Result()

    with pytest.raises(ValueError):
        Result(value=1, error="fail")

def test_result_is_immutable():
    r = Result.ok(42)

    with pytest.raises(AttributeError):
        r._value = 100