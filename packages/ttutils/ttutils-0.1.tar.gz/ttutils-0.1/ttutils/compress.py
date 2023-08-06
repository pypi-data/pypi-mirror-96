"""
Integer, dict integers, list integers compression/decompression functions

```python
from ttutils import compress

compress.encode(11232423)  # 'GSiD'
compress.decode('GSi')  # 175506

compress.encode_list([12312, 34535, 12323])  # '30o-8rD-30z'
compress.decode_list('30o-8rD-30z--30C')  # [12312, 34535, 12323, 12324, 12325, 12326]

compress.encode_dict({12: [234, 453], 789: [12, 98, 99, 100, 101]})
    # 'c-3G-75/cl-c-1y-1z-1A-1B'
compress.decode_dict('c-3G-75/cl-c-1y--1B')
    # {12: [234, 453], 789: [12, 98, 99, 100, 101]}
```
"""

from typing import List, Dict, Iterable, Generator, Optional

CODE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.'


def encode(value: int, res: str = '') -> str:
    """ Encode value """
    res = CODE[value % len(CODE)] + res
    return encode(value // len(CODE), res) if value // len(CODE) > 0 else res


def decode(value: str) -> int:
    """ Decode value """
    return sum(CODE.index(y) * len(CODE) ** x for x, y in list(enumerate(reversed(value))))


def encode_list(value: List[Optional[int]]) -> str:
    """ Convert int list to encoded string """
    value = value if None in value else make_ranges(value)
    return '-'.join(encode(x) if x else '' for x in value)


def decode_list(value: str) -> List[int]:
    """ Convert encoded string to int list """
    return list(breaking_range(list(decode(x) if x else None for x in value.split('-'))))


def encode_dict(value: Dict[int, Iterable[Optional[int]]]) -> str:
    """ Convert dict of int's to encoded string """
    return '/'.join(encode_list([key, *val]) for key, val in value.items())


def decode_dict(value: str) -> Dict[int, Iterable[int]]:
    """ Convert encoded string to dict of int's """
    _decoded = (decode_list(x) for x in value.split('/')) if value else []
    return {x[0]: x[1:] for x in _decoded}


def breaking_range(values: Iterable[int]) -> Generator[int, None, None]:
    """ Convert int list with ranges to consistent int list """
    cur = 0

    while True:
        try:
            _cur = values.pop(0)
            if _cur is None:
                yield from range(cur + 1, values.pop(0) + 1)
            else:
                cur = _cur
                yield cur

        except IndexError:
            return None


def make_ranges(values: Iterable[int]) -> Generator[Optional[int], None, None]:
    pre_value, start_range = None, None

    for value in values:
        if pre_value and pre_value + 1 == value:
            if not start_range:
                start_range = pre_value
            pre_value = value
            continue

        if start_range:
            if start_range + 1 != pre_value:
                yield None
            start_range = None
            yield pre_value

        yield value

        pre_value = value

    if start_range:
        if start_range + 1 != pre_value:
            yield None
        yield pre_value
