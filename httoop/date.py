"""
HTTP Date.

.. seealso:: :rfc:`2616#section-3.3`
"""

from __future__ import annotations

import time

# import calendar
from datetime import datetime
from email.utils import parsedate_tz
from typing import Any, Self

from httoop.exceptions import InvalidDate
from httoop.meta import Semantic
from httoop.util import _


__all__ = ['Date']


class Date(Semantic):
    """
    A HTTP Date string.

    It provides a API to multiple time representations:

    * datetime
    * time struct
    * UNIX timestamp

    Supported HTTP date string formats:

    :example:
    Sun, 06 Nov 1994 08:49:37 GMT  ; RFC 822, updated by RFC 1123
    Sunday, 06-Nov-94 08:49:37 GMT ; RFC 850, obsoleted by RFC 1036
    Sun Nov  6 08:49:37 1994       ; ANSI C's asctime() format
    """

    __slots__ = ('__composed', '__datetime', '__time_struct', '__timestamp')

    def __init__(self, timeval: Any | None = None) -> None:
        """
        :param timeval:
        :type  timeval:
        either seconds since epoch in float
        or a datetime object
        or a timetuple
        """
        self.__composed = None
        self.__timestamp: float = 0.0
        self.__datetime = None
        self.__time_struct = None

        if timeval is None:
            self.__timestamp = time.time()
        elif isinstance(timeval, (float, int)):
            self.__timestamp = float(timeval)
        elif isinstance(timeval, (tuple, time.struct_time)):
            # self.__timestamp = calendar.timegm(timeval)
            self.__timestamp = time.mktime(timeval) - time.timezone
        elif isinstance(timeval, datetime):
            self.__datetime = timeval
            # self.__timestamp = calendar.timegm(self.datetime.utctimetuple())
            self.__timestamp = time.mktime(self.datetime.utctimetuple()) - time.timezone
        elif isinstance(timeval, (bytes, str)):
            if isinstance(timeval, str):
                timeval = timeval.encode('ascii', 'ignore')
            self.__timestamp = float(Date.parse(timeval))
        elif isinstance(timeval, Date):
            self.__timestamp = float(timeval)
        else:
            raise TypeError('Date(): got invalid argument')

    @property
    def datetime(self) -> datetime:
        if self.__datetime is None:
            self.__datetime = datetime.utcfromtimestamp(int(self))
        return self.__datetime

    @property
    def gmtime(self) -> time.struct_time:
        if self.__time_struct is None:
            self.__time_struct = time.gmtime(int(self))
        return self.__time_struct

    def compose(self) -> bytes:
        if self.__composed is None:
            self.__composed = self.__compose()
        return self.__composed

    def __compose(self) -> bytes:
        d = self.gmtime
        return b'%s, %02d %s %04d %02d:%02d:%02d GMT' % (
            (b'Mon', b'Tue', b'Wed', b'Thu', b'Fri', b'Sat', b'Sun')[d.tm_wday],
            d.tm_mday,
            (b'Jan', b'Feb', b'Mar', b'Apr', b'May', b'Jun', b'Jul', b'Aug', b'Sep', b'Oct', b'Nov', b'Dec')[d.tm_mon - 1],
            d.tm_year,
            d.tm_hour,
            d.tm_min,
            d.tm_sec,
        )

    @classmethod
    def parse(cls, data: bytes) -> Date:
        """
        Parses a HTTP date string and returns a :class:`Date` object.

        :param timestr: the time string in one of the HTTP formats
        :type  timestr: str

        :returns: the HTTP Date object
        :rtype  : :class:`Date`

        """
        timestr = data.decode('ISO8859-1')

        # parse the most common HTTP Date formats (RFC 2822, RFC 1036, C's asctime)
        date = parsedate_tz(timestr)
        if date is None:
            raise InvalidDate(_('Invalid date: %r'), timestr)

        return cls(date[:9])

    def __int__(self) -> int:
        return int(float(self))

    def __float__(self) -> float:
        return float(self.__timestamp)

    def __eq__(self, other: object) -> bool:
        try:
            return int(self) == int(self.__other(other))
        except NotImplementedError:  # pragma: no cover
            return NotImplemented

    def __gt__(self, other: Date | str | None) -> bool:
        try:
            return int(self) > int(self.__other(other))
        except NotImplementedError:  # pragma: no cover
            return NotImplemented

    def __lt__(self, other: Date | str | None) -> bool:
        try:
            return int(self) < int(self.__other(other))
        except NotImplementedError:  # pragma: no cover
            return NotImplemented

    @staticmethod
    def __other(other) -> Self:
        if other is None:
            return Date(0)
            # raise NotImplementedError()
        if isinstance(other, Date):
            return other
        try:
            return Date(other)
        except (InvalidDate, TypeError):
            return Date(0)
            # raise NotImplementedError()

    def __repr__(self) -> str:
        return '<HTTP Date(%d)>' % (int(self),)
