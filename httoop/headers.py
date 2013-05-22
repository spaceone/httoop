# -*- coding: utf-8 -*-
"""HTTP headers

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""

__all__ = ['Headers', 'HeaderElement']

# FIXME: python3?

import re

from httoop.util import CaseInsensitiveDict, ByteString, iteritems
from httoop.exceptions import InvalidHeader

# a mapping of all headers to HeaderElement classes
headerfields = CaseInsensitiveDict()

class Headers(ByteString, CaseInsensitiveDict):
	# disallowed bytes for HTTP header field names
	HEADER_RE = re.compile(b"[\x00-\x1F\x7F()<>@,;:\\\\\"/\[\]?={} \t\x80-\xFF]")

	# Regular expression that matches `special' characters in parameters, the
	# existance of which force quoting of the parameter value.
	RE_TSPECIALS = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')

	def elements(self, fieldname):
		u"""Return a sorted list of HeaderElements from the given comma-separated header string."""

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
				k = k.replace('_', '-') # TODO: find out why this is done
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
				raise InvalidHeader(u"Invalid header line: %s" % curr.strip().decode('ISO8859-1'))

			name, value = curr.split(":", 1)
			name = name.rstrip(" \t")

			if self.HEADER_RE.search(name):
				raise InvalidHeader(u"Invalid header name: %s" % name.decode('ISO8859-1'))

			name, value = name.strip(), [value.lstrip()]

			# Consume value continuation lines
			while lines and lines[0].startswith((" ", "\t")):
				value.append(lines.pop(0)[1:])
			value = b''.join(value).rstrip()

			# store new header value
			self.append(name, value)

	def compose(self):
		return b'%s\r\n' % b''.join(b'%s: %s\r\n' % (k.encode('ascii', 'ignore'), v.encode('ISO8859-1', 'replace')) for k, v in iteritems(self))

	def __unicode__(self):
		return self.compose().decode('ISO8859-1')

	def __bytes__(self):
		return self.compose()

	def __repr__(self):
		return "<HTTP Headers(%s)>" % repr(list(self.items()))

	@staticmethod
	def _formatparam(param, value=None, quote=1):
		"""Convenience function to format and return a key=value pair.

		This will quote the value if needed or if quote is true.
		"""
		if value:
			if quote or self.RE_TSPECIALS.search(value):
				value = value.replace('\\', '\\\\').replace('"', r'\"')
				return '%s="%s"' % (param, value)
			else:
				return '%s=%s' % (param, value)
		else:
			return param

class HeaderElement(object):
	"""An element (with parameters) from an HTTP header's element list."""

	def __init__(self, value, params=None):
		self.value = value
		self.params = params or {}

	def __cmp__(self, other):
		return cmp(self.value, other.value)

	def __lt__(self, other):
		return self.value < other.value

	def __str__(self):
		params = ["; %s=%s" % (k, v) for k, v in iteritems(self.params)]
		return "%s%s" % (self.value, "".join(params))

	@staticmethod
	def parse(elementstr):
		"""Transform 'token;key=val' to ('token', {'key': 'val'})."""
		# Split the element into a value and parameters. The 'value' may
		# be of the form, "token=token", but we don't split that here.
		# FIXME: elementstr = 'name; =value'
		atoms = [x.strip() for x in elementstr.split(";") if x.strip()]

		if not atoms:
			initial_value = ''
		else:
			initial_value = atoms.pop(0).strip()

		params = {}
		for atom in atoms:
			if '=' not in atom:
				params[atom] = ''
			else:
				key, val = atom.split("=", 1)
				params[key.strip()] = val.strip()

		return initial_value, params

	@classmethod
	def from_str(cls, elementstr):
		"""Construct an instance from a string of the form 'token;key=val'."""
		ival, params = cls.parse(elementstr)
		return cls(ival, params)

	def __repr__(self):
		return '<%s(%r)>' % (self.__class__.__name__, self.value)

class AcceptElement(HeaderElement):
	"""An Accept element with quality value

		.. seealso:: :rfc:`2616#section-3.9`

	"""

	# RFC 2616 Section 3.9
	RE_Q_SEPARATOR = re.compile(r'; *q *= *(?:(?:0(?:\.[0-9]{3})?)|(?:1(?:\.00?0?)?))')

	def __init__(self, value, params):
		super(AcceptElement, self).__init__(value, params)
		try:
			self.quality
		except ValueError:
			raise InvalidHeader(u'quality value must be float')

	@classmethod
	def from_str(cls, elementstr):
		qvalue = None
		# The first "q" parameter (if any) separates the initial
		# media-range parameter(s) (if any) from the accept-params.
		atoms = cls.RE_Q_SEPARATOR.split(elementstr, 1)
		media_range = atoms.pop(0).strip()
		if atoms:
			# The qvalue for an Accept header can have extensions. The other
			# headers cannot, but it's easier to parse them as if they did.
			qvalue = HeaderElement.from_str(atoms[0].strip())

		media_type, params = cls.parse(media_range)
		if qvalue is not None:
			params["q"] = qvalue

		return cls(media_type, params)

	@property
	def quality(self):
		"""The quality of this value."""
		val = self.params.get("q", "1")
		if isinstance(val, HeaderElement):
			val = val.value
		return float(val)

	def __cmp__(self, other):
		diff = cmp(self.quality, other.quality)
		if diff == 0:
			diff = cmp(str(self), str(other))
		# reverse
		return {-1: 1, 0: 0, 1: -1}.get(diff, diff)

	def __lt__(self, other):
		if self.quality == other.quality:
			return str(self) < str(other)
		else:
			return self.quality < other.quality

class Accept(AcceptElement):
	@property
	def version(self):
		return self.params.get('version', '')

	@version.setter
	def version(self, version):
		self.params['version'] = version

class AcceptCharset(AcceptElement):
	pass

class AcceptEncoding(AcceptElement):
	pass

class AcceptLanguage(AcceptElement):
	pass

class AcceptRanges(AcceptElement):
	pass

class Age(HeaderElement):
	pass

class Allow(HeaderElement):
	pass

class Authorization(HeaderElement):
	pass

class CacheControl(HeaderElement):
	pass

class Connection(HeaderElement):
	pass

class ContentEncoding(HeaderElement):
	pass

class ContentLanguage(HeaderElement):
	pass

class ContentLength(HeaderElement):
	pass

class ContentLocation(HeaderElement):
	pass

class ContentMD5(HeaderElement):
	pass

class ContentRange(HeaderElement):
	pass

class ContentType(HeaderElement):
	@property
	def charset(self):
		return self.params.get('charset', '')

	@charset.setter
	def charset(self, charset):
		self.params['charset'] = charset

	@property
	def version(self):
		return self.params.get('version', '')

	@version.setter
	def version(self, version):
		self.params['version'] = version

class Date(HeaderElement):
	pass

class ETag(HeaderElement):
	pass

class Expect(HeaderElement):
	pass

class Expires(HeaderElement):
	pass

class From(HeaderElement):
	pass

class Host(HeaderElement):
	pass

class IfMatch(HeaderElement):
	pass

class IfModifiedSince(HeaderElement):
	pass

class IfNoneMatch(HeaderElement):
	pass

class IfRange(HeaderElement):
	pass

class IfUnmodifiedSince(HeaderElement):
	pass

class LastModified(HeaderElement):
	pass

class Location(HeaderElement):
	pass

class MaxForwards(HeaderElement):
	pass

class Pragma(HeaderElement):
	pass

class ProxyAuthenticate(HeaderElement):
	pass

class ProxyAuthorization(HeaderElement):
	pass

class Range(HeaderElement):
	pass

class Referer(HeaderElement):
	pass

class RetryAfter(HeaderElement):
	pass

class Server(HeaderElement):
	pass

class TE(HeaderElement):
	pass

class Trailer(HeaderElement):
	def __init__(self, value, params):
		super(HeaderElement, self).__init__(value, params)
		if value.title() in ('Transfer-Encoding', 'Content-Length', 'Trailer'):
			raise InvalidHeader(u'A Trailer header MUST NOT contain %r field' % value.title())

class TransferEncoding(HeaderElement):
	pass

class Upgrade(HeaderElement):
	pass

class UserAgent(HeaderElement):
	pass

class Vary(HeaderElement):
	pass

class Via(HeaderElement):
	pass

class Warning(HeaderElement):
	pass

class WWWAuthenticate(HeaderElement):
	pass

headerfields.update({
	'TE': AcceptElement,
	'Accept': AcceptElement,
	'Accept-Charset': AcceptCharset,
	'Accept-Language': AcceptLanguage,
	'Accept-Encoding': AcceptEncoding,
	'Accept-Ranges': AcceptRanges,
	'Age': Age,
	'Allow': Allow,
	'Authorization': Authorization,
	'Cache-Control': CacheControl,
	'Connection': Connection,
	'Content-Encoding': ContentEncoding,
	'Content-Language': ContentLanguage,
	'Content-Length': ContentLength,
	'Content-Location': ContentLocation,
	'Content-MD5': ContentMD5,
	'Content-Range': ContentRange,
	'Content-Type': ContentType,
	'Date': Date,
	'ETag': ETag,
	'Expect': Expect,
	'Expires': Expires,
	'From': From,
	'Host': Host,
	'If-Match': IfMatch,
	'If-Modified-Since': IfModifiedSince,
	'If-None-Match': IfNoneMatch,
	'If-Unmodified-Since': IfUnmodifiedSince,
	'LastModified': LastModified,
	'Location': Location,
	'Max-Forwards': MaxForwards,
	'Pragma': Pragma,
	'Proxy-Authenticate': ProxyAuthenticate,
	'Proxy-Authorization': ProxyAuthorization,
	'Range': Range,
	'Referer': Referer,
	'Retry-After': RetryAfter,
	'Server': Server,
	'Trailer': Trailer,
	'Transfer-Encoding': TransferEncoding,
	'Upgrade': Upgrade,
	'User-Agent': UserAgent,
	'Vary': Vary,
	'Via': Via,
	'Warning': Warning,
	'WWW-Authenticate': WWWAuthenticate
})
