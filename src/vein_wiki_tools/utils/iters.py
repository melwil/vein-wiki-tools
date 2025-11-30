from collections.abc import Generator


def peekable_iter(text: str, sentinel: str = "") -> Generator[tuple[str, str], None, None]:
    it = iter(text.splitlines())
    last = next(it)
    yield sentinel, last
    for val in it:
        yield last, val
        last = val
    yield last, sentinel
