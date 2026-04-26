"""Exception classes."""

from httoop.util import _Translateable


class Invalid(_Translateable, ValueError):
    """base class for invalid values."""


class InvalidLine(Invalid):
    """error raised when first line is invalid."""


class InvalidHeader(Invalid):
    """error raised when header is invalid."""


class InvalidURI(Invalid):
    """error raised when URI is invalid."""


class InvalidDate(Invalid):
    """error raised when Date is invalid."""


class InvalidBody(Invalid):
    """error raised when Body is invalid."""


class EncodeError(_Translateable, ValueError):
    """error raised when encoding failed."""


class DecodeError(_Translateable, ValueError):
    """error raised when decoding failed."""
