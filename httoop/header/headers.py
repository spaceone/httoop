# -*- coding: utf-8 -*-
import re

from httoop.util import CaseInsensitiveDict, iteritems, to_unicode
from httoop.meta import HTTPSemantic
from httoop.header.element import HEADER, HeaderElement
from httoop.exceptions import InvalidHeader


class Headers(CaseInsensitiveDict):

	__metaclass__ = HTTPSemantic

	# disallowed bytes for HTTP header field names
	HEADER_RE = re.compile(br"[\x00-\x1F\x7F()<>@,;:\\\\\"/\[\]?={} \t\x80-\xFF]")

	@staticmethod
	def formatvalue(value):
		return to_unicode(value)  # TODO: using unicode here is not good if processed via HeaderElement

	@classmethod
	def formatkey(cls, key):
		key = CaseInsensitiveDict.formatkey(key)
		if cls.HEADER_RE.search(key):
			raise InvalidHeader(u"Invalid header name: %r" % key.decode('ISO8859-1'))
		return key  # TODO: do we want bytes here?

	def elements(self, fieldname):
		u"""Return a sorted list of HeaderElements from
			the given comma-separated header string."""

		fieldvalue = self.get(fieldname)
		if not fieldvalue:
			return []

		Element = HEADER.get(fieldname, HeaderElement)
		return Element.sorted([Element.parse(element) for element in Element.split(fieldvalue)])

	def element(self, fieldname, default=None):
		u"""Treat the field as single element"""
		if fieldname in self:
			Element = HEADER.get(fieldname, HeaderElement)
			return Element.parse(self[fieldname])
		return default

#	# TODO: a really nice alternative method would be:
#	def element(self, fieldname, which=None, default=None):
#		for element in self.elements(fieldname):
#			if which is None or element == which:
#				return element
#		return default

	def set_element(self, fieldname, *args, **kwargs):
		self[fieldname] = bytes(self.create_element(fieldname, *args, **kwargs))

	def append_element(self, fieldname, *args, **kwargs):
		self.append(fieldname, bytes(self.create_element(fieldname, *args, **kwargs)))

	def create_element(self, fieldname, *args, **kwargs):
		Element = HEADER.get(fieldname, HeaderElement)
		return Element(*args, **kwargs)

	def values(self, key=None):  # FIXME: overwrites dict.values()
		if key is None:
			return super(Headers, self).values()
		# if key is set return a ordered list of element values
		return [e.value for e in self.elements(key)]

	def append(self, _name, _value, **params):
		if params:
			Element = HEADER.get(_name, HeaderElement)
			parts = [_value or b'']
			for k, v in iteritems(params):
				k = k.replace('_', '-')  # TODO: find out why this is done
				if v is None:
					parts.append(k)
				else:
					parts.append(Element.formatparam(k, v))
			_value = "; ".join(parts)

		if _name not in self or not self[_name]:
			self[_name] = _value
		else:
			Element = HEADER.get(_name, HeaderElement)
			self[_name] = Element.join([self[_name], _value])

	def validate(self):
		u"""validates all header elements

			:raises: InvalidHeader
		"""
		for name in self:
			self.elements(name)

	def merge(self, other):
		other = self.__class__(other)
		for key in other:
			Element = HEADER.get(key, HeaderElement)
			self[key] = Element.merge(self.elements(key), other.elements(key))

	def set(self, headers):
		self.clear()
		self.update(headers)

	def parse(self, data):
		r"""parses HTTP headers

			:param data:
				the header string containing headers separated by "\r\n"
				without trailing "\r\n"
			:type  data: bytes
		"""

		lines = data.split(b'\r\n')

		while lines:
			curr = lines.pop(0)
			name, _, value = curr.partition(b':')
			if _ != b':':
				raise InvalidHeader(u"Invalid header line: %r" % curr.decode('ISO8859-1'))
			name = name.rstrip(' \t')

			if self.HEADER_RE.search(name):
				raise InvalidHeader(u"Invalid header name: %r" % name.decode('ISO8859-1'))

			name, value = name.strip(), [value.lstrip()]

			# continuation lines
			while lines and lines[0].startswith((' ', '\t')):
				value.append(lines.pop(0)[1:])
			value = b''.join(value).rstrip()
			Element = HEADER.get(name, HeaderElement)
			value = Element.decode(value)

			self.append(name, value)

	def compose(self):
		return b'%s\r\n' % b''.join(b'%s: %s\r\n' % (k, v) for k, v in self.__items())

	def __items(self):
		return sorted(self.__encoded_items(), key=lambda x: HEADER.get(x[0], HeaderElement).priority or x[0])

	def __encoded_items(self):
		for key, values in iteritems(self):
			Element = HEADER.get(key, HeaderElement)
			if Element.list_element:
				for value in Element.split(values):
					yield key, Element.encode(value)
			else:
				yield key, Element.encode(values)

	def __repr__(self):
		return "<HTTP Headers(%s)>" % repr(list(self.items()))
