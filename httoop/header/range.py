# -*- coding: utf-8 -*-

from os import SEEK_END, SEEK_SET

from httoop.header.element import HeaderElement
from httoop.exceptions import InvalidHeader


class ContentRange(HeaderElement):
	__name__ = 'Content-Range'


class IfRange(HeaderElement):
	__name__ = 'If-Range'


class Range(HeaderElement):

	def __init__(self, value, params=None):
		bytesunit, _, byteranges = value.partition(b'=')
		ranges = HeaderElement.split(byteranges)
		self.ranges = set()
		for brange in ranges:
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
			self.ranges.add((start, stop))
		self.ranges = list(sorted(self.ranges))
		super(Range, self).__init__(bytesunit, params)

	def sanitize(self):
		super(Range, self).sanitize()
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
			yield fd.read(length)
