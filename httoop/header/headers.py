# -*- coding: utf-8 -*-
import re

from httoop.exceptions import InvalidHeader
from httoop.header.element import HEADER, HeaderElement
from httoop.meta import HTTPSemantic
from httoop.six import with_metaclass
from httoop.util import CaseInsensitiveDict, Unicode, _, iteritems, to_unicode


class Headers(with_metaclass(HTTPSemantic, CaseInsensitiveDict)):

	__slots__ = ()

	# disallowed bytes for HTTP header field names
	HEADER_RE = re.compile(br"[\x00-\x1F\x7F()<>@,;:\\\\\"/\[\]?={} \t\x80-\xFF]")

	@staticmethod
	def formatvalue(value):
		if isinstance(value, Unicode):
			return HeaderElement.encode_rfc2047(value)
		return bytes(value)

	def __getitem__(self, key):
		Element = HEADER.get(key, HeaderElement)
		return Element.decode_rfc2047(super(Headers, self).__getitem__(key))

	def get(self, key, default=None):
		Element = HEADER.get(key, HeaderElement)
		try:
			return Element.decode_rfc2047(super(Headers, self).__getitem__(key))
		except KeyError:
			return default

	def getbytes(self, key, default=None):
		try:
			return super(Headers, self).__getitem__(key)
		except KeyError:
			return default

	@classmethod
	def formatkey(cls, key):
		key = CaseInsensitiveDict.formatkey(key)
		if cls.HEADER_RE.search(key.encode('utf-8')):
			raise InvalidHeader(_(u"Invalid header name: %r"), key)
		try:
			return to_unicode(HEADER[key].__name__)
		except KeyError:
			return key

	def elements(self, fieldname):
		u"""Return a sorted list of HeaderElements from
		the given comma-separated header string.
		"""
		fieldvalue = self.getbytes(fieldname)
		if not fieldvalue:
			return []

		Element = HEADER.get(fieldname, HeaderElement)
		return Element.sorted([Element.parse(element) for element in Element.split(fieldvalue)])

	def element(self, fieldname, default=None):
		u"""Treat the field as single element."""
		if fieldname in self:
			Element = HEADER.get(fieldname, HeaderElement)
			return Element.parse(super(Headers, self).__getitem__(fieldname))
		return default

	def get_element(self, fieldname, which=None, default=None):
		for element in self.elements(fieldname):
			if which is None or element == which:
				return element
		return default

	def set_element(self, fieldname, *args, **kwargs):
		self[fieldname] = bytes(self.create_element(fieldname, *args, **kwargs))

	def append_element(self, fieldname, *args, **kwargs):
		self.append(fieldname, bytes(self.create_element(fieldname, *args, **kwargs)))

	def create_element(self, fieldname, *args, **kwargs):
		Element = HEADER.get(fieldname, HeaderElement)
		return Element(*args, **kwargs)

	def values(self, *key):
		if not key:
			return super(Headers, self).values()
		# if key is set return a ordered list of element values
		return [e.value for e in self.elements(*key)]

	def append(self, _name, _value, **params):
		_value = self.formatvalue(_value)
		if params:
			Element = HEADER.get(_name, HeaderElement)
			parts = [_value or b''] + [Element.formatparam(k.encode(), v) for k, v in iteritems(params)]
			_value = b'; '.join(parts)

		if _name not in self or not self[_name]:
			self[_name] = _value
		else:
			Element = HEADER.get(_name, HeaderElement)
			self[_name] = Element.join([super(Headers, self).__getitem__(_name), _value])

	def merge(self, other):
		other = self.__class__(other)
		for key in other:
			Element = HEADER.get(key, HeaderElement)
			self[key] = Element.merge(self.elements(key), other.elements(key))

	def set(self, headers):
		self.clear()
		self.update(headers)

	def parse(self, data):
		r"""parses HTTP headers.

		:param data:
		the header string containing headers separated by "\r\n"
		without trailing "\r\n"
		:type  data: bytes
		"""
		lines = data.split(b'\r\n')

		while lines:
			curr = lines.pop(0)
			name, __, value = curr.partition(b':')
			if __ != b':':
				raise InvalidHeader(_(u"Invalid header line: %r"), curr.decode('ISO8859-1'))

			if self.HEADER_RE.search(name):
				raise InvalidHeader(_(u"Invalid header name: %r"), name.decode('ISO8859-1'))

			name, value = name.strip(), [value.lstrip()]

			# continuation lines
			while lines and lines[0].startswith((b' ', b'\t')):
				value.append(lines.pop(0)[1:])
			value = b''.join(value).rstrip()
			Element = HEADER.get(name, HeaderElement)
			name = name.decode('ascii')

			if name in self:
				value = Element.join([super(Headers, self).__getitem__(name), value])
			super(Headers, self).__setitem__(name, value)

	def compose(self):
		return b'%s\r\n' % b''.join(b'%s: %s\r\n' % (k, v) for k, v in self.__items())

	def __items(self):
		return sorted(self.__encoded_items(), key=lambda x: HEADER.get(x[0], HeaderElement).priority or x[0])

	def __encoded_items(self):
		for key, values in iteritems(self):
			Element = HEADER.get(key, HeaderElement)
			if Element is not HeaderElement:
				key = Element.__name__
			key = key.encode('ascii', 'ignore')
			if Element.list_element:
				for value in Element.split(values):
					yield key, value
			else:
				yield key, values

	def __repr__(self):
		return "<HTTP Headers(%s)>" % repr(list(self.items()))
