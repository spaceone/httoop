# -*- coding: utf-8 -*-

from math import sqrt
from os import SEEK_END, SEEK_SET

from httoop.exceptions import InvalidHeader
from httoop.header.element import HeaderElement
from httoop.util import _, integer

__all__ = ('ContentRange', 'IfRange', 'Range')


class ContentRange(HeaderElement):

	__name__ = 'Content-Range'
	is_response_header = True

	def __init__(self, value, range_, length):
		self.range = range_
		if self.range:
			start, end = self.range
			start = start or 0
			end = end or integer(length)
			self.range = (start, end)
		self.length = length if length is None else integer(length)
		super(ContentRange, self).__init__(value)

	def compose(self):
		length = b'*' if self.length is None else self.length
		byte_range = b'%d-%d' % tuple(self.range) if self.range else b'*'
		return b'%s %s/%s' % (self.value.encode('ISO8859-1'), byte_range, str(length).encode('ASCII') if isinstance(length, int) else length)

	@classmethod
	def parse(cls, elementstr):
		value, start, end, complete_length = None, None, None, None
		try:
			value, content_range = elementstr.split(None, 1)
			if value != b'bytes':
				raise InvalidHeader(_(u'Only "bytes" Content-Range supported'))
			byte_range, complete_length = content_range.split(b'/')
			if complete_length != b'*':
				complete_length = integer(complete_length)
				if complete_length < 0:
					raise ValueError()
			else:
				complete_length = None
			if byte_range != b'*':
				start, end = byte_range.split(b'-', 1)
				start, end = integer(start), integer(end)
				if start >= end or start < 0 or end < 0:
					raise ValueError()
			if complete_length is None and start is None:
				raise ValueError()
		except ValueError:
			raise InvalidHeader(_(u'Content-Range: %r'), elementstr)
		return cls(value.decode('ISO8859-1'), (start, end), complete_length)


class IfRange(HeaderElement):
	__name__ = 'If-Range'
	is_request_header = True


class Range(HeaderElement):

	is_request_header = True

	def __init__(self, value, ranges, params=None):
		self.ranges = ranges
		super(Range, self).__init__(value, params)

	@classmethod
	def split(cls, fieldvalue):
		return [fieldvalue]

	@classmethod
	def parse(cls, elementstr):
		bytesunit, __, byteranges = elementstr.partition(b'=')
		byteranges = super(Range, cls).split(byteranges)
		ranges = set()
		for brange in byteranges:
			start, __, stop = (x.strip() for x in brange.partition(b'-'))
			if (not start and not stop) or not __:
				raise InvalidHeader(_(u'no range start/stop.'))
			try:
				start = integer(start) if start else None
				stop = integer(stop) if stop else None
				if start and start < 0 or stop and stop < 0:
					raise ValueError()
			except ValueError:
				raise InvalidHeader(_(u'no range number.'))
			if start is not None and stop is not None and stop <= start:
				raise InvalidHeader(_(u'range start must be smaller than end.'))
			if not start and not stop:
				raise InvalidHeader(_(u'full range requested.'))
			ranges.add((start, stop))
		return cls(bytesunit.decode('ISO8859-1'), list(sorted(ranges, key=lambda x: x[0] if x[0] is not None else -1)))

	def sanitize(self):
		super(Range, self).sanitize()
		self.prevent_denial_of_service()

	def prevent_denial_of_service(self):
		if len([x for x in self.ranges if x[0] is None]) > 1 or len([x for x in self.ranges if x[1] is None]) > 1:
			raise InvalidHeader(_(u'too many overlapping ranges.'))
		byterange = set()
		for start, stop in ((x or 0, y or max((m[1] or 0) + 1 for m in self.ranges)) for x, y in self.ranges):
			range_ = set(range(start, stop))
			if any(x in byterange for x in range_):
				raise InvalidHeader(_(u'duplicated range.'))
			byterange.update(range_)

		if self.stddev([(x[1] or float('inf')) - (x[0] or 0) for x in self.ranges]) > 2.0:
			raise InvalidHeader(_('ranges exceeding high standard deviation'))

	def stddev(self, xs):
		def average(xs):
			return sum(xs) * 1.0 / len(xs)

		def variance(xs):
			avg = average(xs)
			return [(x - avg) ** 2 for x in xs]

		return sqrt(average(variance(xs)))

	@property
	def positions(self):
		for start, end in self.ranges:
			if start is None:
				yield -end, SEEK_END, None
			elif end is None:
				yield start, SEEK_SET, None
			else:
				yield start, SEEK_SET, end + 1 - start

	def get_range_content(self, fd):
		for offset, whence, length in self.positions:
			fd.seek(offset, whence)
			length = () if length is None else (length, )
			yield fd.read(*length)
