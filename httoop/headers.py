# -*- coding: utf-8 -*-
"""HTTP headers

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""

__all__ = ['Headers']

# FIXME: python3?

import re

from httoop.util import CaseInsensitiveDict, ByteString, iteritems
from httoop.exceptions import InvalidHeader
from httoop.header import headerfields, HeaderElement


class Headers(ByteString, CaseInsensitiveDict):
	# disallowed bytes for HTTP header field names
	HEADER_RE = re.compile(b"[\x00-\x1F\x7F()<>@,;:\\\\\"/\[\]?={} \t\x80-\xFF]")

	# Regular expression that matches `special' characters in parameters, the
	# existance of which force quoting of the parameter value.
	RE_TSPECIALS = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')

	def elements(self, fieldname):
		u"""Return a sorted list of HeaderElements from
			the given comma-separated header string."""

		fieldvalue = self.get(fieldname)
		if not fieldvalue:
			return []

		Element = headerfields.get(fieldname, HeaderElement)

		# FIXME: quoted strings
		result = []
		for element in fieldvalue.split(","):
			result.append(Element.from_str(element))

		return list(reversed(sorted(result)))
		# TODO: remove the reversed() (fix in AcceptElement)

	def element(self, fieldname):
		u"""Treat the field as single element"""
		if fieldname in self:
			Element = headerfields.get(fieldname, HeaderElement)
			return Element.from_str(self[fieldname])

	def values(self, key=None):
		# if key is set return a ordered list of element values
		# TODO: may move this into another method because values is a dict name
		if key is None:
			return super(Headers, self).values()
		return [e.value for e in self.elements(key)]

	def append(self, _name, _value, **params):
		if params:
			parts = [_value or b'']
			for k, v in iteritems(params):
				k = k.replace('_', '-')  # TODO: find out why this is done
				if v is None:
					parts.append(k)
				else:
					parts.append(Headers._formatparam(k, v))
			_value = "; ".join(parts)

		if not _name in self:
			self[_name] = _value
		else:
			self[_name] = ", ".join([self[_name], _value])

	def validate(self):
		u"""validates all header elements

			:raises: InvalidHeader
		"""
		for name in self:
			self.elements(name)

	def parse(self, data):
		r"""parses HTTP headers

			:param data:
				the header string containing headers separated by "\r\n"
				without trailing "\r\n"
			:type  data: bytes
		"""

		lines = data.split(b'\r\n')

		# parse headers into key/value pairs paying attention
		# to continuation lines.
		while lines:
			# Parse initial header name : value pair.
			curr = lines.pop(0)
			if b':' not in curr:
				raise InvalidHeader(u"Invalid header line: %r" % curr.decode('ISO8859-1'))

			name, value = curr.split(":", 1)
			name = name.rstrip(" \t")

			if self.HEADER_RE.search(name):
				raise InvalidHeader(u"Invalid header name: %s" % name.decode('ISO8859-1'))

			name, value = name.strip(), [value.lstrip()]

			# Consume value continuation lines
			while lines and lines[0].startswith((" ", "\t")):
				value.append(lines.pop(0)[1:])
			value = b''.join(value).rstrip()

			# TODO: parse encoded fields (MIME syntax)

			# store new header value
			self.append(name, value)

	def compose(self):
		# TODO: if value contains UTF-8 chars encode them in MIME
		return b'%s\r\n' % b''.join(b'%s: %s\r\n' % (k, v.encode('ISO8859-1', 'replace')) for k, v in iteritems(self))

	def __bytes__(self):
		return self.compose()

	def __repr__(self):
		return "<HTTP Headers(%s)>" % repr(list(self.items()))

	@classmethod
	def _formatparam(cls, param, value=None, quote=1):
		"""Convenience function to format and return a key=value pair.

		This will quote the value if needed or if quote is true.
		"""
		if value:
			if quote or cls.RE_TSPECIALS.search(value):
				value = value.replace('\\', '\\\\').replace('"', r'\"')
				return '%s="%s"' % (param, value)
			else:
				return '%s=%s' % (param, value)
		else:
			return param
