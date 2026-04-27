from typing import Any

from httoop.date import Date
from httoop.exceptions import InvalidDate
from httoop.header.element import HeaderElement


class _DateComparable:

    Date = Date

    def sanitize(self) -> None:
        super().sanitize()
        self.value = self.Date.parse(self.value.encode('ASCII', 'replace'))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Date):
            if isinstance(other, _DateComparable):
                other = int(other)
            try:
                other = Date(other)
            except InvalidDate:
                return False
        return self.value == other

    def __int__(self) -> int:
        return int(self.value)


class _MatchElement:

    def __eq__(self, other: Any) -> bool:
        return self.value == other or self.value == '*'

    def matches(self, etag):
        return self == etag

    def matches_etag(self, etag, *, strong: bool = True):
        value = self.value

        if value == '*':
            return True

        is_weak = value.startswith('W/')
        if is_weak:
            if strong:
                return False
            value = value[2:]

        if not (value.startswith('"') and value.endswith('"')):
            return False

        return value[1:-1] == etag


class ETag(HeaderElement):

    is_response_header = True

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ETag):
            other = self.__class__(other)
        return other.value == self.value or other.value == '*'


class LastModified(_DateComparable, HeaderElement):
    __name__ = 'Last-Modified'
    is_response_header = True


class IfMatch(_MatchElement, HeaderElement):
    __name__ = 'If-Match'
    is_request_header = True


class IfModifiedSince(_DateComparable, HeaderElement):
    __name__ = 'If-Modified-Since'
    is_request_header = True


class IfNoneMatch(_MatchElement, HeaderElement):
    __name__ = 'If-None-Match'
    is_request_header = True


class IfUnmodifiedSince(_DateComparable, HeaderElement):
    __name__ = 'If-Unmodified-Since'
    is_request_header = True
