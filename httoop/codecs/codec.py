from __future__ import annotations

from typing import Any

from httoop.util import Unicode


class Codec(object):

    @classmethod
    def decode(cls, data: bytes, charset: Optional[str] = None, mimetype: None = None) -> str:  # pragma: no cover
        if isinstance(data, bytes):
            data = data.decode(charset or 'ascii')
        return data

    @classmethod
    def encode(cls, data: bytes, charset: None = None, mimetype: None = None) -> bytes:  # pragma: no cover
        if isinstance(data, Unicode):
            data = data.encode(charset or 'ascii')
        return data

    @classmethod
    def iterencode(cls, data: Any, charset: str | None = None, mimetype: ContentType | None = None) -> None:  # pragma: no cover
        yield cls.encode(data, charset, mimetype)

    @classmethod
    def iterdecode(cls, data: Any, charset=None, mimetype=None):  # pragma: no cover
        yield cls.decode(data, charset, mimetype)
