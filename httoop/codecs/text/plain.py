from __future__ import annotations

from typing import TYPE_CHECKING

from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError, EncodeError


if TYPE_CHECKING:
    from httoop.header.messaging import ContentType


class PlainText(Codec):

    mimetype = 'text/plain'

    @classmethod
    def decode(cls, data: bytes, charset: str | None = None, mimetype: ContentType | None = None) -> str:
        try:
            assert isinstance(data, bytes)
            return data.decode(charset or 'UTF-8')
        except UnicodeDecodeError:
            raise DecodeError('Wrong encoding.')

    @classmethod
    def encode(cls, data: str, charset: str | None = None, mimetype: ContentType | None = None) -> bytes:
        try:
            assert not isinstance(data, bytes)
            return data.encode(charset or 'UTF-8')
        except UnicodeEncodeError:
            raise EncodeError('Wrong encoding.')
