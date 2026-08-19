from __future__ import annotations

import zlib

from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError, EncodeError, InvalidBodySize
from httoop.util import _


class Deflate(Codec):
    mimetype = 'application/zlib'

    @classmethod
    def encode(cls, data: bytes, charset: None = None, mimetype: None = None) -> bytes:
        try:
            return zlib.compress(Codec.encode(data, charset))
        except zlib.error:  # pragma: no cover
            raise EncodeError(_('Invalid zlib/deflate data.')) from None

    @classmethod
    def decode(cls, data: bytes, charset: str | None = None, mimetype: None = None, max_size: int = -1) -> str:
        try:
            result = _decompress_limited(data, max_size) if max_size > 0 else zlib.decompress(data)
        except zlib.error:
            raise DecodeError(_('Invalid zlib/deflate data.')) from None

        return Codec.decode(result, charset)


def _decompress_limited(data: bytes, max_size: int) -> bytes:
    decompressor = zlib.decompressobj()
    chunks = []
    size = 0
    pending = data

    while True:
        remaining = max_size - size

        chunk = decompressor.decompress(pending, remaining + 1)
        size += len(chunk)

        if size > max_size:
            raise InvalidBodySize(_('Maximum content size (%d) reached'), max_size)

        chunks.append(chunk)

        if decompressor.eof:
            break

        pending = decompressor.unconsumed_tail

        if not pending:
            # if zlib still hasn't reached EOF the compressed representation is truncated
            raise zlib.error()

    return b''.join(chunks)
