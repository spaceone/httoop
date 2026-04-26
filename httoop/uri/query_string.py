from __future__ import annotations

import stringprep

from httoop.codecs.application.x_www_form_urlencoded import FormURLEncoded
from httoop.exceptions import InvalidURI as DecodeError
from httoop.uri.percent_encoding import Percent
from httoop.util import _


class QueryString(FormURLEncoded):

    INVALID = (stringprep.in_table_c21, )
    UNQUOTED = Percent.QUERY.replace(b'+', b'').replace(b'=', b'').replace(b'&', b'')

    @classmethod
    def decode(cls, data: bytes, charset: str | None = None) -> tuple[()] | tuple[tuple[str, str]] | tuple[tuple[str, str], tuple[str, str], tuple[str, str]] | tuple[tuple[str, str], tuple[str, str]]:
        if any(in_table(x) for x in cls.unquote(data, 'ISO8859-1') for in_table in cls.INVALID):
            raise DecodeError(_('Invalid query string: contains invalid token'))
        data = super().decode(data, charset)
        return data
