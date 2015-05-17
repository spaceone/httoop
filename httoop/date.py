# -*- coding: utf-8 -*-
"""HTTP Date

.. seealso:: :rfc:`2616#section-3.3`
"""

__all__ = ['Date']

import time
from datetime import datetime

from httoop.util import formatdate, parsedate, Unicode
from httoop.exceptions import InvalidDate
from httoop.meta import HTTPSemantic


class Date(object):
	u"""HTTP Date

		.. seealso:: :rfc:`2616#section-3.3`

		.. seealso:: :rfc:`2616#section-19.3`
	"""
	__metaclass__ = HTTPSemantic

	def __init__(self, timeval=None):
		u"""
			:param timeval:
			:type  timeval:
				either seconds since epoch in float
				or a datetime object
				or a timetuple
		"""

		self.http_string, self.datetime, self.timestamp = None, None, None

		if timeval is None:
			self.datetime = datetime.now()
			self.timestamp = time.mktime(self.datetime.timetuple())
		elif isinstance(timeval, (float, int)):
			self.timestamp = float(timeval)
		elif isinstance(timeval, tuple):
			self.timestamp = time.mktime(timeval)
		elif isinstance(timeval, datetime):
			self.datetime = timeval
			self.timestamp = time.mktime(self.datetime.timetuple())
		elif isinstance(timeval, (bytes, Unicode)):
			if isinstance(timeval, Unicode):
				timeval = timeval.encode('ascii')
			date = self.parse(timeval)
			self.datetime = date.datetime
			self.timestamp = date.timestamp
		else:
			raise TypeError('Date(): got invalid argument')

	def to_timetuple(self):
		return parsedate(formatdate(self.timestamp))[:7]

	def to_datetime(self):
		if self.datetime is None:
			self.datetime = datetime.fromtimestamp(self.timestamp)
		return self.datetime

	def to_unix_timestamp(self):
		return self.timestamp

	def to_http_string(self):
		if self.http_string is None:
			self.http_string = formatdate(self.to_unix_timestamp())
		return self.http_string

	def compose(self):
		return self.to_http_string()

	# TODO: implement __cmp__, __int__, (__float__), etc.

	@classmethod
	def parse(cls, timestr=None):
		u"""parses a HTTP date string and returns a :class:`Date` object

			:param timestr: the time string in one of the http formats
			:type  timestr: str

			:returns: the HTTP Date object
			:rtype  : :class:`Date`

			:example:
				Sun, 06 Nov 1994 08:49:37 GMT  ; RFC 822, updated by RFC 1123
				Sunday, 06-Nov-94 08:49:37 GMT ; RFC 850, obsoleted by RFC 1036
				Sun Nov  6 08:49:37 1994       ; ANSI C's asctime() format
		"""

		# parse the most common HTTP Date format (RFC 2822)
		date = parsedate(timestr)
		if date is not None:
			return cls(date[:9])

		# propably invalid here (if email.utils is installed)

		# TODO: export locale=C required?
		# parse RFC 1036 date format
		try:
			date = time.strptime(timestr, '%A, %d-%b-%y %H:%M:%S GMT')
		except ValueError:
			pass
		else:
			return cls(date)

		# parse C's asctime format
		# TODO: export locale=C required?
		try:
			date = time.strptime(timestr, '%a %b %d %H:%M:%S %Y')
		except ValueError:
			pass
		else:
			return cls(date)

		raise InvalidDate(date)
