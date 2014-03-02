# -*- coding: utf-8 -*-

from httoop.header.element import HeaderElement


class ContentRange(HeaderElement):
	__name__ = 'Content-Range'


class IfRange(HeaderElement):
	pass


class Range(HeaderElement):
	@classmethod
	def from_str(cls, elementstr):
		pass

#	def __get_ranges(self):
#		bytesunit, _, byteranges = self.value.partition('=')
#		for brange in byteranges.split(','):
#			start, _, stop = (x.strip() for x in brange.partition('-'))
#			if start:
#				if not stop:
#					stop = content_length - 1
#				start, stop = list(map(int, (start, stop)))
#				if start >= content_length:
#					# From rfc 2616 sec 14.16:
#					# "If the server receives a request (other than one
#					# including an If-Range request-header field) with an
#					# unsatisfiable Range request-header field (that is,
#					# all of whose byte-range-spec values have a first-byte-pos
#					# value greater than the current length of the selected
#					# resource), it SHOULD return a response code of 416
#					# (Requested range not satisfiable)."
#					continue
#				if stop < start:
#					# From rfc 2616 sec 14.16:
#					# "If the server ignores a byte-range-spec because it
#					# is syntactically invalid, the server SHOULD treat
#					# the request as if the invalid Range header field
#					# did not exist. (Normally, this means return a 200
#					# response containing the full entity)."
#					return
#				yield start, stop + 1
#			else:
#				if not stop:
#					# See rfc quote above.
#					return
#				# Negative subscript (last N bytes)
#				yield content_length - int(stop), content_length
