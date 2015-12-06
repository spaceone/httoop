# -*- coding: utf-8 -*-
"""HTTP header elements

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""
__all__ = ['HEADER', 'HeaderElement']

import re

from httoop.util import CaseInsensitiveDict, iteritems, decode_rfc2231, Unicode, decode_header, sanitize_encoding, _
from httoop.exceptions import InvalidHeader
from httoop.uri.percent_encoding import Percent

# a mapping of all headers to HeaderElement classes
HEADER = CaseInsensitiveDict()


class HeaderType(type):

	def __new__(mcs, name, bases, dict_):
		__all__.append(name)
		name = dict_.get('__name__', name)
		return super(HeaderType, mcs).__new__(mcs, name, bases, dict_)


class HeaderElement(object):
	u"""An element (with parameters) from an HTTP header's element list."""

	__metaclass__ = HeaderType

	priority = None
	hop_by_hop = False
	list_element = False

	# Regular expression that matches `special' characters in parameters, the
	# existance of which force quoting of the parameter value.
	RE_TSPECIALS = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')
	RE_SPLIT = re.compile(',(?=(?:[^"]*"[^"]*")*[^"]*$)')
	RE_PARAMS = re.compile(';(?=(?:[^"]*"[^"]*")*[^"]*$)')

	def __init__(self, value, params=None):
		self.value = bytes(value)
		self.params = params or {}
		self.sanitize()

	def sanitize(self):
		pass

	def __lt__(self, other):
		return self.value < getattr(other, 'value', other)

	def __gt__(self, other):
		return self.value > getattr(other, 'value', other)

	def __eq__(self, other):
		return self.value == getattr(other, 'value', other)

	def __ne__(self, other):
		return not self == other

	def __bytes__(self):
		return self.compose()

	def __unicode__(self):
		return self.decode(bytes(self))

	if str is bytes:
		__str__ = __bytes__
	else:  # pragma: no cover
		__str__ = __unicode__

	def compose(self):
		params = [b'; %s' % self.formatparam(k, v) for k, v in iteritems(self.params)]
		return b'%s%s' % (self.value, ''.join(params))

	@classmethod
	def parseparams(cls, elementstr):
		"""Transform 'token;key=val' to ('token', {'key': 'val'})."""
		# Split the element into a value and parameters. The 'value' may
		# be of the form, "token=token", but we don't split that here.
		atoms = [x.strip() for x in cls.RE_PARAMS.split(elementstr) if x.strip()] or ['']

		value = atoms.pop(0)
		params = (cls.parseparam(atom) for atom in atoms)
		params = cls._rfc2231_and_continuation_params(params)
		# TODO: prefer foo* parameter when both are provided

		return value, dict(params)

	@classmethod
	def parseparam(cls, atom):
		key, __, val  = atom.partition(b'=')
		try:
			val, quoted = cls.unescape_param(val.strip())
		except InvalidHeader:
			raise InvalidHeader(_(u'Unquoted parameter %r in %r containing TSPECIALS: %r'), key, cls.__name__, val)
		return cls.unescape_key(key), val, quoted

	@classmethod
	def unescape_key(cls, key):
		return key.strip().lower()

	@classmethod
	def unescape_param(cls, value):
		quoted = value.startswith(b'"') and value.endswith(b'"')
		if quoted:
			value = re.sub(r'\\(?!\\)', '', value.strip(b'"'))
		else:
			if cls.RE_TSPECIALS.search(value):
				raise InvalidHeader(_(u'Unquoted parameter in %r containing TSPECIALS: %r'), cls.__name__, value)
		return value, quoted

	@classmethod
	def _rfc2231_and_continuation_params(cls, params):  # TODO: complexity
		count = set()
		continuations = dict()
		for key, value, quoted in params:
			if key in count:
				raise InvalidHeader(_(u'Parameter given twice: %r'), key.decode('ISO8859-1'))
			count.add(key)
			if '*' in key:
				if key.endswith('*') and not quoted:
					charset, language, value_ = decode_rfc2231(value.encode('ISO8859-1'))
					if not charset:
						yield key, value
						continue
					encoding = sanitize_encoding(charset)
					if encoding is None:
						raise InvalidHeader(_(u'Unknown encoding: %r'), charset)
					key, value = key[:-1], Percent.decode(value_, encoding)
				key_, asterisk, num = key.rpartition('*')
				if asterisk:
					try:
						if num != '0' and num.startswith('0'):
							raise ValueError
						num = int(num)
					except ValueError:
						yield key, value
						continue
					continuations.setdefault(key_, {})[num] = value
					continue
			yield key, value

		for key, lines in iteritems(continuations):
			value = b''
			for i in xrange(len(lines)):
				try:
					value += lines.pop(i)
				except KeyError:
					break
			if not key:
				raise InvalidHeader(_(u'...'))
			if value:
				yield key, value
			for k, v in iteritems(lines):
				yield '%s*%d' % (key, k), v

	@classmethod
	def parse(cls, elementstr):
		"""Construct an instance from a string of the form 'token;key=val'."""
		ival, params = cls.parseparams(elementstr)
		return cls(ival, params)

	@classmethod
	def split(cls, fieldvalue):
		return cls.RE_SPLIT.split(fieldvalue)

	@classmethod
	def join(cls, values):
		return b', '.join(values)

	@classmethod
	def sorted(cls, elements):
		return elements

	@classmethod
	def merge(cls, elements, others):
		return cls.join([bytes(x) for x in cls.sorted(elements + others)])

	@classmethod
	def formatparam(cls, param, value=None, quote=False):
		"""Convenience function to format and return a key=value pair.

		This will quote the value if needed or if quote is true.
		"""
		if value:
			value = bytes(value)
			if quote or cls.RE_TSPECIALS.search(value):
				value = value.replace(b'\\', b'\\\\').replace(b'"', br'\"')
				return b'%s="%s"' % (param, value)
			else:
				return b'%s=%s' % (param, value)
		else:
			return param

	@classmethod
	def decode(cls, value):
		if b'=?' in value:
			# FIXME: must not parse encoded_words in unquoted ('Content-Type', 'Content-Disposition') header params
			return u''.join(atom.decode(charset or 'ISO8859-1') for atom, charset in decode_header(value))
		return value.decode('ISO8859-1')

	@classmethod
	def encode(cls, value):
		try:
			return value.encode('ISO8859-1')
		except UnicodeEncodeError:
			return value.encode('ISO8859-1', 'replace')  # FIXME: if value contains UTF-8 chars encode them in MIME; =?UTF-8?B?…?= (RFC 2047); seealso quopri

	def __repr__(self):
		params = ', %r' % (self.params,) if self.params else ''
		return '<%s(%r%s)>' % (self.__class__.__name__, self.value, params)


class MimeType(object):
	u"""
		.. seealso:: rfc:`2046`

		.. seealso:: rfc:`3023`
	"""

	@property
	def mimetype(self):
		return '%s/%s' % (self.type, self.subtype_wo_vendor)

	@property
	def type(self):
		return self.value.split('/', 1)[0]

	@type.setter
	def type(self, type_):
		self.value = '%s/%s' % (type_, self.subtype)

	@property
	def subtype(self):
		return (self.value.split('/', 1) + [b''])[1]

	@subtype.setter
	def subtype(self, subtype):
		self.value = '%s/%s' % (self.type, subtype)

	# TODO: official name
	@property
	def subtype_wo_vendor(self):
		return self.subtype.split('+', 1).pop()

	@subtype_wo_vendor.setter
	def subtype_wo_vendor(self, subtype_wo_vendor):
		self.subtype = '%s+%s' % (self.vendor, subtype_wo_vendor)

	@property
	def vendor(self):
		if b'+' in self.subtype:
			return self.subtype.split('+', 1)[0]
		return b''

	@vendor.setter
	def vendor(self, vendor):
		self.subtype = '%s+%s' % (vendor, self.subtype_wo_vendor)

	@property
	def version(self):
		return self.params.get('version', '')

	@version.setter
	def version(self, version):
		self.params['version'] = version


class _AcceptElement(HeaderElement):
	"""An Accept element with quality value

		.. seealso:: :rfc:`2616#section-3.9`

	"""

	# RFC 2616 Section 3.9
	RE_Q_SEPARATOR = re.compile(r';\s*q\s*=\s*')

	@property
	def quality(self):
		"""The quality of this value."""
		val = self.params.get("q", "1")
		if isinstance(val, HeaderElement):
			val = val.value
		if val:
			return float(val)

	def sanitize(self):
		super(_AcceptElement, self).sanitize()
		try:
			self.quality
		except ValueError:
			raise InvalidHeader(_(u'Quality value must be float.'))

	@classmethod
	def parse(cls, elementstr):
		qvalue = None
		# The first "q" parameter (if any) separates the initial
		# media-range parameter(s) (if any) from the accept-params.
		atoms = cls.RE_Q_SEPARATOR.split(elementstr, 1)
		media_range = atoms.pop(0).strip()
		if atoms:
			# The qvalue for an Accept header can have extensions. The other
			# headers cannot, but it's easier to parse them as if they did.
			qvalue = HeaderElement.parse(atoms[0].strip())

		media_type, params = cls.parseparams(media_range)
		if qvalue is not None:
			params["q"] = qvalue

		return cls(media_type, params)

	@classmethod
	def sorted(cls, elements):
		return list(sorted(elements, reverse=True))

	def __eq__(self, other):
		if not isinstance(other, _AcceptElement):
			other = _AcceptElement(other)
		return other.value == self.value and other.quality == self.quality

	def __lt__(self, other):
		if not isinstance(other, _AcceptElement):
			other = _AcceptElement(other)
		if self.quality == other.quality:
			return str(self) < str(other)
		else:
			return self.quality < other.quality


class _CookieElement(HeaderElement):

	#RE_TSPECIALS = re.compile(r'[ \(\)<>@,;:\\"\[\]\?=]')
	RE_TSPECIALS = re.compile(r'(?!)')

	def __init__(self, cookie_name, cookie_value, params=None):
		self.cookie_name = Unicode(cookie_name)
		self.cookie_value = Unicode(cookie_value)
		super(_CookieElement, self).__init__(self.value, params)

	@classmethod
	def parse(cls, elementstr):
		value, params = cls.parseparams(elementstr)
		cookie_name, cookie_value, __ = cls.parseparam(value)
		return cls(cookie_name, cookie_value, params)

	@classmethod
	def unescape_key(cls, key):
		key = key.strip()
		if key.lower() in ('httponly', 'secure', 'path', 'domain', 'max-age', 'expires'):
			return key.lower()
		return key

	@property
	def value(self):
		return b'%s=%s' % (self.cookie_name.encode('ISO8859-1'), self.cookie_value.encode('ISO8859-1'))

	@value.setter
	def value(self, value):
		self.cookie_name, self.cookie_value, __ = self.parseparam(value)


class _HopByHopElement(object):
	hop_by_hop = True

class _ListElement(object):
	list_element = True
