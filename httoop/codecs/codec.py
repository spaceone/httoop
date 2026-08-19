from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from httoop.header.messaging import ContentType


class Codec:

    mimetype: str

    @classmethod
    def decode(cls, data: bytes, charset: str | None = None, mimetype: ContentType | None = None, **kwargs) -> str:  # pragma: no cover
        if isinstance(data, bytes):
            data = data.decode(charset or 'ascii')
        return data

    @classmethod
    def encode(cls, data: bytes, charset: None = None, mimetype: ContentType | None = None) -> bytes:  # pragma: no cover
        if isinstance(data, str):
            data = data.encode(charset or 'ascii')
        return data

    @classmethod
    def iterencode(cls, data: Any, charset: str | None = None, mimetype: ContentType | None = None) -> None:  # pragma: no cover
        yield cls.encode(data, charset, mimetype)

    @classmethod
    def iterdecode(cls, data: Any, charset=None, mimetype: ContentType | None = None):  # pragma: no cover
        yield cls.decode(data, charset, mimetype)
