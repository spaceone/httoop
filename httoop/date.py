# -*- coding: utf-8 -*-
"""HTTP Date

.. seealso:: :rfc:`2616#section-3.3`
"""

from __future__ import absolute_import

__all__ = ['Date']

import time
import locale
#import calendar
from datetime import datetime

from httoop.util import parsedate, Unicode
from httoop.exceptions import InvalidDate
from httoop.meta import HTTPSemantic
from httoop.util import _


class Date(object):
	u"""A HTTP Date string

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
	__metaclass__ = HTTPSemantic

	def __init__(self, timeval=None):
		u"""
			:param timeval:
			:type  timeval:
				either seconds since epoch in float
				or a datetime object
				or a timetuple
		"""

		self.__composed = None
		self.__timestamp = None
		self.__datetime = None
		self.__time_struct = None

		if timeval is None:
			self.__timestamp = time.time()
		elif isinstance(timeval, (float, int)):
			self.__timestamp = float(timeval)
		elif isinstance(timeval, (tuple, time.struct_time)):
#			self.__timestamp = calendar.timegm(timeval)
			self.__timestamp = time.mktime(timeval) - time.timezone
		elif isinstance(timeval, datetime):
			self.__datetime = timeval
#			self.__timestamp = calendar.timegm(self.datetime.utctimetuple())
			self.__timestamp = time.mktime(self.datetime.utctimetuple()) - time.timezone
		elif isinstance(timeval, (bytes, Unicode)):
			if isinstance(timeval, Unicode):
				timeval = timeval.encode('ascii', 'ignore')
			self.__timestamp = float(Date.parse(timeval))
		else:
			raise TypeError('Date(): got invalid argument')

	@property
	def datetime(self):
		if self.__datetime is None:
			self.__datetime = datetime.utcfromtimestamp(int(self))
		return self.__datetime

	@property
	def gmtime(self):
		if self.__time_struct is None:
			self.__time_struct = time.gmtime(int(self))
		return self.__time_struct

	def compose(self):
		if self.__composed is None:
			self.__composed = self.__compose()
		return self.__composed

	def __compose(self):
		d = self.gmtime
		return b'%s, %02d %s %04d %02d:%02d:%02d GMT' % (
			(b'Mon', b'Tue', b'Wed', b'Thu', b'Fri', b'Sat', b'Sun')[d.tm_wday],
			d.tm_mday,
			(b'Jan', b'Feb', b'Mar', b'Apr', b'May', b'Jun', b'Jul', b'Aug', b'Sep', b'Oct', b'Nov', b'Dec')[d.tm_mon - 1],
			d.tm_year, d.tm_hour, d.tm_min, d.tm_sec
		)

	@classmethod
	def parse(cls, timestr=None):
		u"""parses a HTTP date string and returns a :class:`Date` object

			:param timestr: the time string in one of the http formats
			:type  timestr: str

			:returns: the HTTP Date object
			:rtype  : :class:`Date`

		"""

		# parse the most common HTTP Date format (RFC 2822)
		date = parsedate(timestr)
		if date is not None:
			return cls(date[:9])

		old = locale.getlocale(locale.LC_TIME)
		locale.setlocale(locale.LC_TIME, (None, None))
		try:
			# parse RFC 1036 date format
			try:
				date = time.strptime(timestr, '%A, %d-%b-%y %H:%M:%S GMT')
			except ValueError:
				pass
			else:
				return cls(date)

			# parse C's asctime format
			try:
				date = time.strptime(timestr, '%a %b %d %H:%M:%S %Y')
			except ValueError:
				pass
			else:
				return cls(date)
		finally:
			locale.setlocale(locale.LC_TIME, old)

		raise InvalidDate(_(u'Invalid date: %r'), date)

	def __int__(self):
		return int(float(self))

	def __float__(self):
		return float(self.__timestamp)

	def __eq__(self, other):
		try:
			return int(self) == int(self.__other(other))
		except NotImplementedError:
			return NotImplemented

	def __gt__(self, other):
		try:
			return int(self) > int(self.__other(other))
		except NotImplementedError:
			return NotImplemented

	def __lt__(self, other):
		try:
			return int(self) < int(self.__other(other))
		except NotImplementedError:
			return NotImplemented

	def __other(self, other):
		if other is None:
			raise NotImplementedError
		if isinstance(other, Date):
			return other
		try:
			return Date(other)
		except (InvalidDate, TypeError):
			raise NotImplementedError

	def __repr__(self):
		return '<HTTP Date(%d)>' % (int(self),)
