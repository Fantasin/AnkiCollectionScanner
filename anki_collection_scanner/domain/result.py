"""
File: domain/result.py
What: Implement Result[T, E] class with ok(), err(), is_ok(), is_err(), unwrap(), unwrap_err()
Why: Every function will return this instead of throwing exceptions
"""

from typing import Any, Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")

_MISSING = object() #creating a unique object representing a missing parameter

class Result(Generic[T,E]):
    def __init__(self, *, value = _MISSING, error = _MISSING): #setting value and error to missing by default. 

        #enforcing an invariant: only value or error can be present
        if (value is _MISSING and error is _MISSING) or (value is not _MISSING and error is not _MISSING):
            raise ValueError("Either value or error should be present")
        
        self._value = value #stops being missing if a user passed value = something during an instance creation
        self._error = error #same as value
        self._is_ok = error is _MISSING #checking with is for exact same object instead of == for equality

        super().__setattr__("_frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError("Result is immutable")
        super().__setattr__(name, value)

    @classmethod
    def ok(cls, value: T)-> "Result[T, E]":
        return cls(value=value)
    
    @classmethod
    def err(cls, error: E)-> "Result[T, E]":
        return cls(error=error)

    def is_ok(self)-> bool:
        return self._is_ok

    def is_err(self)-> bool:
        return not self._is_ok
    
    def unwrap(self)-> T:
        if not self._is_ok:
            raise RuntimeError(f"Called unwrap on Err: {self._error}")
        return self._value #type: ignore
    
    def unwrap_err(self) -> E:
        if self._is_ok:
            raise RuntimeError("Called unwrap_err on Ok")
        return self._error #type: ignore