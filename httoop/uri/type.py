from __future__ import annotations
from typing import Any, Dict, Tuple, Type, Union

from httoop.meta import HTTPSemantic


class URIType(HTTPSemantic):

    def __new__(mcs: Type, name: str, bases: Union[Tuple[Type]], dict_: Dict[str, Union[str, Tuple[()], bytes, int]]) -> Any:
        cls = super().__new__(mcs, name, tuple(bases), dict_)
        if dict_.get('SCHEME'):
            for base in bases:
                if getattr(base, 'SCHEMES', None) is not None:
                    base.SCHEMES.setdefault(dict_['SCHEME'].lower(), cls)
        return cls
