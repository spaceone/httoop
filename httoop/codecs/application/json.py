from __future__ import annotations

from json import dumps as json_encode, loads as json_decode
from typing import TYPE_CHECKING, Any

from httoop.codecs.codec import Codec


if TYPE_CHECKING:
    from httoop.header.messaging import ContentType


class JSON(Codec):
    mimetype = 'application/json'

    @classmethod
    def encode(cls, data: dict[str, str], charset: str | None = None, mimetype: ContentType | None = None) -> bytes:
        doc = json_encode(data)
        return doc.encode(charset or 'UTF-8')

    @classmethod
    def decode(cls, data: bytes, charset: str | None = None, mimetype: ContentType | None = None) -> dict[str, Any]:
        return json_decode(data.decode(charset or 'ASCII'))
