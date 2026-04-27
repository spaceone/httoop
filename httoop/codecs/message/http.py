from __future__ import annotations

from typing import TYPE_CHECKING

from httoop.codecs.codec import Codec


if TYPE_CHECKING:
    from httoop.header.messaging import ContentType
    from httoop.messages.request import Request
    from httoop.messages.response import Response


class HTTP(Codec):

    mimetype = 'message/http'

    @classmethod
    def encode(cls, data: Request | Response, charset: str | None = None, mimetype: ContentType | None = None) -> bytes:
        return bytes(data) + bytes(data.headers) + bytes(data.body)

    @classmethod
    def decode(cls, data: bytes, charset: str | None = None, mimetype: ContentType | None = None) -> Request | Response:
        from httoop.messages import Request, Response

        line, data = data.split(b'\r\n', 1)
        message = Request()
        try:
            message.parse(line)
        except ValueError:
            message = Response()
            message.parse(line)
        headers, data = data.split(b'\r\n\r\n', 1)
        message.headers.parse(headers)
        message.body.parse(data)
        return message
