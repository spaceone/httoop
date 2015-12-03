# -*- coding: utf-8 -*-

from os import SEEK_END, SEEK_SET

from httoop.header.element import HeaderElement
from httoop.exceptions import InvalidHeader


class ContentRange(HeaderElement):

	__name__ = 'Content-Range'

	def __init__(self, value, range_, length):
		self.range = range_
		if self.range:
			start, end = self.range
			start = start or 0
			end = end or int(length)
			self.range = (start, end)
		self.length = length if length is None else int(length)
		super(ContentRange, self).__init__(value)

	def compose(self):
		length = b'*' if self.length is None else self.length
		byte_range = b'%d-%d' % tuple(self.range) if self.range else b'*'
		return b'%s %s/%s' % (self.value, byte_range, length)

	@classmethod
	def parse(cls, elementstr):
		value, start, end, complete_length = None, None, None, None
		try:
			value, content_range = elementstr.split(None, 1)
			if value != b'bytes':
				raise InvalidHeader('Only "bytes" Content-Range supported')
			byte_range, complete_length = content_range.split(b'/')
			if complete_length != b'*':
				complete_length = int(complete_length)
				if complete_length < 0:
					raise ValueError
			else:
				complete_length = None
			if byte_range != b'*':
				start, end = byte_range.split(b'-', 1)
				start, end = int(start), int(end)
				if start >= end or start < 0 or end < 0:
					raise ValueError
			if complete_length is None and start is None:
				raise ValueError
		except ValueError:
			raise InvalidHeader('Content-Range: %r' % (elementstr,))
		return cls(value, (start, end), complete_length)


class IfRange(HeaderElement):
	__name__ = 'If-Range'


class Range(HeaderElement):

	def __init__(self, value, ranges, params=None):
		self.ranges = ranges
		super(Range, self).__init__(value, params)

	@classmethod
	def parse(cls, elementstr):
		bytesunit, _, byteranges = elementstr.partition(b'=')
		byteranges = cls.split(byteranges)
		ranges = set()
		for brange in byteranges:
			start, _, stop = (x.strip() for x in brange.partition(b'-'))
			if (not start and not stop) or not _:
				raise InvalidHeader
			try:
				start = int(start) if start else None
				stop = int(stop) if stop else None
				if start and start < 0 or stop and stop < 0:
					raise ValueError
			except ValueError:
				raise InvalidHeader
			if start is not None and stop is not None and stop < start:
				raise InvalidHeader
			ranges.add((start, stop))
		return cls(bytesunit, list(sorted(ranges)))

	def sanitize(self):
		super(Range, self).sanitize()
		self.prevent_denial_of_service()

	def prevent_denial_of_service(self):
		if len([x for x in self.ranges if x[0] is None]) > 1 or len([x for x in self.ranges if x[1] is None]) > 1:
			raise InvalidHeader
		byterange = set()
		for start, stop in ((x, y) for x, y in self.ranges if x is not None and y is not None):
			range_ = set(range(start, stop))
			if any(x in byterange for x in range_):
				raise InvalidHeader
			byterange.update(range_)

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
			length = () if length is None else (length,)
			yield fd.read(*length)
