"""Exception classes."""

from httoop.util import _Translateable


class Invalid(_Translateable, ValueError):  # noqa: N818
    """base class for invalid values."""


class InvalidLine(Invalid):
    """error raised when first line is invalid."""


class InvalidHeader(Invalid):
    """error raised when header is invalid."""


class InvalidHeaderSize(InvalidHeader):
    """error raised when maximum header size constraints are reached."""


class InvalidURI(Invalid):
    """error raised when URI is invalid."""


class InvalidDate(Invalid):
    """error raised when Date is invalid."""


class InvalidBody(Invalid):
    """error raised when Body is invalid."""


class InvalidBodySize(InvalidHeader):
    """error raised when maximum body size constraints are reached."""


class EncodeError(_Translateable, ValueError):
    """error raised when encoding failed."""


class DecodeError(_Translateable, ValueError):
    """error raised when decoding failed."""
