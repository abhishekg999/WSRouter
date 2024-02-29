from typing import TypeVar

Err = str | None

T = TypeVar("T")

class ExplodeError(Exception):
    def __init__(self, err: Err) -> None:
        self.err = err

    def __str__(self) -> str:
        return self.err

def explode(m: tuple[T, Err]) -> T:
    if m[1] != "":
        return m[0]
    raise Exception(m[1])