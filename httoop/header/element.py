# -*- coding: utf-8 -*-
"""HTTP header elements

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""

import re
from binascii import b2a_base64
from email.errors import HeaderParseError

from httoop.six import with_metaclass

from httoop.util import CaseInsensitiveDict, iteritems, decode_header, sanitize_encoding, ByteUnicodeDict, integer, _
from httoop.exceptions import InvalidHeader
from httoop.uri.percent_encoding import Percent

__all__ = ['HEADER', 'HeaderElement']
# a mapping of all headers to HeaderElement classes
HEADER = CaseInsensitiveDict()


class HeaderType(type):

	def __new__(cls, name, bases, dict_):
		__all__.append(name)
		name = dict_.get('__name__', name)
		return super(HeaderType, cls).__new__(cls, name, bases, dict_)


class HeaderElement(with_metaclass(HeaderType)):
	u"""An element (with parameters) from an HTTP header's element list."""

	priority = None
	is_request_header = False
	is_response_header = False
	hop_by_hop = False
	list_element = False
	encode_latin1_quoted_printable = False

	# Regular expression that matches `special' characters in parameters, the
	# existance of which force quoting of the parameter value.
	RE_TSPECIALS = re.compile(b'[ \\(\\)<>@,;:\\\\"/\\[\\]\\?=]')
	RE_SPLIT = re.compile(b',(?=(?:[^"]*"[^"]*")*[^"]*$)')
	RE_PARAMS = re.compile(b';(?=(?:[^"]*"[^"]*")*[^"]*$)')

	def __init__(self, value, params=None):
		self.value = value
		self.params = ByteUnicodeDict(params or {})
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
		#return bytes(self).decode('ISO8859-1')
		return self.decode_rfc2047(bytes(self))

	if str is bytes:
		__str__ = __bytes__
	else:  # pragma: no cover
		__str__ = __unicode__

	def compose(self):
		params = [b'; %s' % self.formatparam(k, v) for k, v in iteritems(self.params)]
		return b'%s%s' % (self.encode_rfc2047(self.value), b''.join(params))

	@classmethod
	def parseparams(cls, elementstr):
		"""Transform 'token;key=val' to ('token', {'key': 'val'})."""
		# Split the element into a value and parameters. The 'value' may
		# be of the form, "token=token", but we don't split that here.
		atoms = [x.strip() for x in cls.RE_PARAMS.split(elementstr) if x.strip()] or [b'']

		value = atoms.pop(0)
		params = (cls.parseparam(atom) for atom in atoms)
		params = cls._rfc2231_and_continuation_params(params)
		# TODO: prefer foo* parameter when both are provided

		return value, dict(params)

	@classmethod
	def parseparam(cls, atom):
		key, __, val = atom.partition(b'=')
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
			value = re.sub(b'\\\\(?!\\\\)', b'', value[1:-1])
		else:
			if cls.RE_TSPECIALS.search(value):
				raise InvalidHeader(_(u'Unquoted parameter in %r containing TSPECIALS: %r'), cls.__name__, value)
		return value, quoted

	@classmethod
	def _sanitize_encoding(cls, charset):
		encoding = sanitize_encoding(charset)
		if encoding is None:
			raise InvalidHeader(_(u'Unknown encoding: %r'), charset)
		return encoding

	@classmethod
	def _rfc2231_and_continuation_params(cls, params):  # TODO: complexity
		count = set()
		continuations = dict()
		for key, value, quoted in params:
			if key in count:
				raise InvalidHeader(_(u'Parameter given twice: %r'), key.decode('ISO8859-1'))
			count.add(key)
			if b'*' in key:
				if key.endswith(b'*') and not quoted and not value.startswith(b"'") and value.count(b"'") >= 2:
					charset, language, value_ = value.split(b"'", 2)
					encoding = cls._sanitize_encoding(charset.decode('ASCII', 'replace'))
					try:
						key, value = key[:-1], Percent.unquote(value_).decode(encoding)
					except UnicodeDecodeError as exc:
						raise InvalidHeader(_(u'%s') % (exc,))
				else:
					value = value.decode('ISO8859-1')
				key_, asterisk, num = key.rpartition(b'*')
				if asterisk:
					try:
						if num != b'0' and num.startswith(b'0'):
							raise ValueError()
						num = integer(num)
					except ValueError:
						yield key, value
						continue
					continuations.setdefault(key_, {})[num] = value
					continue
			else:
				value = value.decode('ISO8859-1')
			yield key, value

		for key, lines in iteritems(continuations):
			value = u''
			for i in range(len(lines)):
				try:
					value += lines.pop(i)
				except KeyError:
					break
			if not key:  # pragma: no cover
				raise InvalidHeader(_(u'...'))
			if value:
				yield key, value
			for k, v in iteritems(lines):
				yield b'%s*%d' % (key, k), v

	@classmethod
	def parse(cls, elementstr):
		"""Construct an instance from a string of the form 'token;key=val'."""
		elementstr, encoding = cls.decode_rfc2047_charset(elementstr)
		ival, params = cls.parseparams(elementstr.encode(encoding))
		return cls(ival.decode(encoding), params)

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
			if not isinstance(value, bytes):
				try:
					value = value.encode('ASCII')
				except UnicodeEncodeError:
					param += b'*'
					value = b"utf-8''%s" % (Percent.quote(value.encode('UTF-8')),)
					quote = False

			if quote or cls.RE_TSPECIALS.search(value):
				value = value.replace(b'\\', b'\\\\').replace(b'"', br'\"')
				return b'%s="%s"' % (param, value)
			else:
				return b'%s=%s' % (param, value)
		else:
			return param

	@classmethod
	def decode_rfc2047(cls, value):
		return cls.decode_rfc2047_charset(value)[0]

	@classmethod
	def decode_rfc2047_charset(cls, value):
		if b'=?' in value and b'"=?' not in value and b'==?' not in value:
			# FIXME: must not parse encoded_words in unquoted ('Content-Type', 'Content-Disposition') header params
			try:
				return u''.join(atom.decode(cls._sanitize_encoding(charset or 'ISO8859-1')) for atom, charset in decode_header(value.decode('ISO8859-1'))), 'UTF-8'
			except (UnicodeDecodeError, HeaderParseError) as exc:
				raise InvalidHeader(str(exc))
		try:
			return value.decode('ASCII'), 'ASCII'
		except UnicodeDecodeError:
			return value.decode('ISO8859-1'), 'ISO8859-1'

	@classmethod
	def encode_rfc2047(cls, value):
		try:
			return value.encode('ascii' if cls.encode_latin1_quoted_printable else 'ISO8859-1')
		except UnicodeEncodeError:
			try:
				value.encode('ISO8859-1')
			except UnicodeEncodeError:
				return b'=?utf-8?b?%s?=' % (b2a_base64(value.encode('utf-8')).rstrip(b'\n'),)
			else:  # pragma: no cover
				return b'=?ISO8859-1?b?%s?=' % (b2a_base64(value.encode('ISO8859-1')).rstrip(b'\n'),)

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
		return u'%s/%s' % (self.type, self.subtype_wo_vendor)

	@property
	def type(self):
		return self.value.split(u'/', 1)[0]

	@type.setter
	def type(self, type_):
		self.value = u'%s/%s' % (type_, self.subtype)

	@property
	def subtype(self):
		return (self.value.split(u'/', 1) + [u''])[1]

	@subtype.setter
	def subtype(self, subtype):
		self.value = u'%s/%s' % (self.type, subtype)

	# TODO: official name
	@property
	def subtype_wo_vendor(self):
		return self.subtype.split(u'+', 1).pop()

	@subtype_wo_vendor.setter
	def subtype_wo_vendor(self, subtype_wo_vendor):
		self.subtype = u'%s+%s' % (self.vendor, subtype_wo_vendor)

	@property
	def vendor(self):
		if u'+' in self.subtype:
			return self.subtype.split(u'+', 1)[0]
		return u''

	@vendor.setter
	def vendor(self, vendor):
		self.subtype = u'%s+%s' % (vendor, self.subtype_wo_vendor)

	@property
	def version(self):
		return self.params.get('version', u'')

	@version.setter
	def version(self, version):
		self.params['version'] = str(version)


class _AcceptElement(HeaderElement):
	"""An Accept element with quality value

		.. seealso:: :rfc:`2616#section-3.9`

	"""

	# RFC 2616 Section 3.9
	RE_Q_SEPARATOR = re.compile(br';\s*q\s*=\s*')

	@property
	def quality(self):
		"""The quality of this value."""
		val = self.params.get("q", "1")
		if isinstance(val, HeaderElement):  # pragma: no cover
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
		elementstr, encoding = cls.decode_rfc2047_charset(elementstr)
		qvalue = None
		# The first "q" parameter (if any) separates the initial
		# media-range parameter(s) (if any) from the accept-params.
		atoms = cls.RE_Q_SEPARATOR.split(elementstr.encode(encoding), 1)
		media_range = atoms.pop(0).strip()
		if atoms:
			# The qvalue for an Accept header can have extensions. The other
			# headers cannot, but it's easier to parse them as if they did.
			qvalue = HeaderElement.parse(atoms[0].strip())

		media_type, params = cls.parseparams(media_range)
		if qvalue is not None:
			params["q"] = bytes(qvalue)

		return cls(media_type.decode(encoding), params)

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

	#RE_TSPECIALS = re.compile(br'[ \(\)<>@,;:\\"\[\]\?=]')
	RE_TSPECIALS = re.compile(b'(?!)')

	def __init__(self, cookie_name, cookie_value, params=None):
		self.cookie_name = cookie_name
		self.cookie_value = cookie_value
		super(_CookieElement, self).__init__(self.value, params)

	@classmethod
	def parse(cls, elementstr):
		elementstr, encoding = cls.decode_rfc2047_charset(elementstr)
		value, params = cls.parseparams(elementstr.encode(encoding))
		cookie_name, cookie_value, __ = cls.parseparam(value)
		return cls(cookie_name.decode(encoding), cookie_value.decode(encoding), params)

	@classmethod
	def unescape_key(cls, key):
		key = key.strip()
		if key.lower() in (b'httponly', b'secure', b'path', b'domain', b'max-age', b'expires'):
			return key.lower()
		return key

	@property
	def value(self):
		return u'%s=%s' % (self.cookie_name, self.cookie_value)

	@value.setter
	def value(self, value):
		self.cookie_name, self.cookie_value, __ = self.parseparam(value.encode('ISO8859-1'))
		self.cookie_name, self.cookie_value = self.cookie_name.decode('ISO8859-1'), self.cookie_value.decode('ISO8859-1')


class _HopByHopElement(object):
	hop_by_hop = True


class _ListElement(object):
	list_element = True
