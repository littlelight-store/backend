import typing as t


def map_by_key(iterable: t.List[t.Any], key: str):
    res = dict()

    for i in iterable:
        if hasattr(i, key):
            res[getattr(i, key)] = i

    return res
