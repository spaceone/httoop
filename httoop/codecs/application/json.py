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
        data = json_encode(data)
        if not isinstance(data, bytes):  # python3
            data = data.encode(charset or 'UTF-8')
        return data

    @classmethod
    def decode(cls, data: bytes, charset: str | None = None, mimetype: ContentType | None = None) -> dict[str, Any]:
        return json_decode(data.decode(charset or 'ASCII'))
