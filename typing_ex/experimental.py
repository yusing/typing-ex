# from typing_ex import TypeInfo
from typing import Any, Dict, Iterable, get_origin, get_args, Optional
from inspect import getfullargspec, signature, getargs
from typing_ex import TypeInfo
# print(int is Any)
# print(Any is Any)
# print(Any == Any)
# print(get_origin(Any))
# print(get_origin(Any) is Any)
# print(get_origin(Any) == Any)

# print(hash(Dict[str, str]) == hash(type({"123": "213"})))

# def a(b, c: str) -> Any:
#     pass

# print(signature(a).parameters)
print(getargs([1, 1.0, None]))