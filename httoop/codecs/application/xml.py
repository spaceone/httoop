from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn


if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from httoop.header.messaging import ContentType


# TODO: http://docs.python.org/2/library/xml.html#xml-vulnerabilities
# TODO: https://www.owasp.org/index.php/XML_External_Entity_%28XXE%29_Processing
try:
    from defusedxml.ElementTree import ParseError, fromstring, tostring
except ImportError:  # pragma: no cover
    # TODO: emit a warning
    from xml.etree.ElementTree import ParseError, tostring  # noqa: S405

    def fromstring(data) -> NoReturn:
        raise ParseError('Will not parse without defusedxml!')


from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError


class XML(Codec):
    mimetype = 'application/xml'

    @classmethod
    def decode(cls, data: bytes, charset: str | None = None, mimetype: ContentType | None = None) -> Element:
        try:
            return fromstring(data)
        except ParseError as exc:
            raise DecodeError(f'Could not decode as {mimetype}: {exc}') from exc

    @classmethod
    def encode(cls, root: Element, charset: str | None = None, mimetype: ContentType | None = None) -> bytes:
        return tostring(root, charset)
