# -*- coding: utf-8 -*-
"""HTTP header elements

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""
__all__ = ['HEADER', 'HeaderElement']

import re
# TODO: Via, Server, User-Agent can contain comments → parse them
# TODO: parse encoded words like =?UTF-8?B?…?= (RFC 2047); seealso quopri; '=?utf-8?q?=E2=86=92?='.decode('quopri')
# TODO: unify the use of unicode / bytes

from httoop.util import CaseInsensitiveDict, iteritems, Unicode
from httoop.exceptions import InvalidHeader
from httoop.codecs import lookup

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

	def __init__(self, value, params=None):
		self.value = value
		self.params = params or {}
		self.sanitize()

	def sanitize(self):
		pass

	def __cmp__(self, other):
		return cmp(self.value, getattr(other, 'value', other))

	def __lt__(self, other):
		return self.value < getattr(other, 'value', other)

	def __str__(self):
		params = ["; %s=%s" % (k, v) for k, v in iteritems(self.params)]
		return "%s%s" % (self.value, "".join(params))

	@staticmethod
	def parse(elementstr):
		"""Transform 'token;key=val' to ('token', {'key': 'val'})."""
		# Split the element into a value and parameters. The 'value' may
		# be of the form, "token=token", but we don't split that here.
		atoms = [x.strip() for x in elementstr.split(";") if x.strip()] or ['']

		initial_value = atoms.pop(0)
		params = dict((key.strip(), value.strip()) for key, _, value in (atom.partition('=') for atom in atoms))

		return initial_value, params

	@classmethod
	def from_str(cls, elementstr):
		"""Construct an instance from a string of the form 'token;key=val'."""
		ival, params = cls.parse(elementstr)
		return cls(ival, params)

	@classmethod
	def split(cls, fieldvalue):
		# FIXME: quoted strings
		# TODO: elements which aren't comma separated
		return fieldvalue.split(',')

	def __repr__(self):
		return '<%s(%r)>' % (self.__class__.__name__, self.value)


class MimeType(object):
	u"""
		.. seealso:: rfc:`2046`

		.. seealso:: rfc:`3023`
	"""

	@property
	def codec(self):
		return lookup(self.mimetype.value, False) or lookup(self.mimetype.mimetype, False)

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


class AcceptElement(HeaderElement):
	"""An Accept element with quality value

		.. seealso:: :rfc:`2616#section-3.9`

	"""

	# RFC 2616 Section 3.9
	RE_Q_SEPARATOR = re.compile(r'; *q *= *(?:(?:0(?:\.[0-9]{3})?)|(?:1(?:\.00?0?)?))')

	@property
	def quality(self):
		"""The quality of this value."""
		val = self.params.get("q", "1")
		if isinstance(val, HeaderElement):
			val = val.value
		return float(val)

	def sanitize(self):
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

	def __cmp__(self, other):
		if not isinstance(other, AcceptElement):
			other = AcceptElement(other)
		diff = cmp(self.quality, other.quality)
		if diff == 0:
			diff = cmp(str(self), str(other))
		# reverse
		return {-1: 1, 0: 0, 1: -1}.get(diff, diff)

	def __eq__(self, other):
		if not isinstance(other, AcceptElement):
			other = AcceptElement(other)
		return other.value == self.value and other.quality == self.quality

	def __lt__(self, other):
		if not isinstance(other, AcceptElement):
			other = AcceptElement(other)
		if self.quality == other.quality:
			return str(self) < str(other)
		else:
			return self.quality < other.quality


class CodecElement(object):
	@property
	def codec(self):
		encoding = self.value
		try:
			encoding = self.CODECS[encoding]
			if not isinstance(encoding, (bytes, Unicode)):
				return encoding
			return lookup(encoding)
		except KeyError:
			raise InvalidHeader(u'Unknown %s: %r' % (self.__name__, encoding.decode('ISO8859-1')))

	def __init__(self, value, params=None):
		super(CodecElement, self).__init__(value.lower(), params)

	def sanitize(self):
		self.codec


class Accept(AcceptElement, MimeType):
	def __init__(self, value, params):
		if value == '*':
			value = '*/*'
		super(Accept, self).__init__(value, params)


class AcceptCharset(AcceptElement):
	__name__ = 'Accept-Charset'


class AcceptEncoding(AcceptElement):
	__name__ = 'Accept-Encoding'


class AcceptLanguage(AcceptElement):
	__name__ = 'Accept-Language'


class AcceptRanges(AcceptElement):
	__name__ = 'Accept-Ranges'


class Age(HeaderElement):
	pass


class Allow(HeaderElement):
	pass


class Authorization(HeaderElement):
	pass


class CacheControl(HeaderElement):
	__name__ = 'Cache-Control'


class Connection(HeaderElement):
	pass


class ContentEncoding(CodecElement, HeaderElement):
	__name__ = 'Content-Encoding'

	# IANA assigned HTTP Content-Encoding values
	CODECS = {
		'gzip': 'application/gzip',
		'deflate': 'application/zlib',
		# TODO: implement the following
		'compress': NotImplementedError,
		'identity': NotImplementedError,
		'exi': NotImplementedError,
		'pack200-gzip': NotImplementedError,
	}


class ContentLanguage(HeaderElement):
	__name__ = 'Content-Language'


class ContentLength(HeaderElement):
	__name__ = 'Content-Length'


class ContentLocation(HeaderElement):
	__name__ = 'Content-Location'


class ContentMD5(HeaderElement):
	__name__ = 'Content-MD5'


class ContentRange(HeaderElement):
	__name__ = 'Content-Range'


class ContentType(HeaderElement, MimeType):
	__name__ = 'Content-Type'

	@property
	def charset(self):
		return self.params.get('charset', '')

	@charset.setter
	def charset(self, charset):
		self.params['charset'] = charset

	VALID_BOUNDARY = re.compile('^[ -~]{0,200}[!-~]$')

	@property
	def boundary(self):
		if 'boundary' not in self.params:
			return

		boundary = self.params['boundary'].strip('"')  # FIXME: ? remove this generic?
		if not self.VALID_BOUNDARY.match(boundary):
			raise InvalidHeader('Invalid boundary in multipart form: %r' % (boundary))
		return boundary

	@boundary.setter
	def boundary(self, boundary):
		if not self.VALID_BOUNDARY.match(boundary):
			raise InvalidHeader('Invalid boundary in multipart form: %r' % (boundary))
		self.params['boundary'] = boundary


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


# TODO: add case insensitve HeaderElement
# TODO: integrate ipaddr.IP4/6Address which parses every form of ip addresses
class Host(HeaderElement):
	RE_HOSTNAME = re.compile(r'^([^\x00-\x1F\x7F()<>@,;:/\[\]={} \t\\\\"]+)(?::\d+)?$')
	RE_IP4 = re.compile(r'^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})(?::\d+)?$')
	# FIXME: implement IP parse, this matches 999.999.999.999
	RE_IP6 = re.compile(r'^\[([0-9a-fA-F:]+)\](?::\d+)?$')
	# FIXME: implement IP6 parse

	@property
	def is_ip4(self):
		return self.RE_IP4.match(self.value) is not None

	@property
	def is_ip6(self):
		return self.RE_IP6.match(self.value) is not None

	@property
	def hostname(self):
		return self.ip6address or\
			self.ip4address or\
			self.RE_HOSTNAME.match(self.value).group(1).lower()

	@property
	def ip6address(self):
		# removes IPv6 brackets and port
		if self.is_ip6:
			return self.RE_IP6.match(self.value).group(1)

	@property
	def ip4address(self):
		# removes port
		if self.is_ip4:
			return self.RE_IP4.match(self.value).group(1)

	def sanitize(self):
		if not self.RE_HOSTNAME.match(self.value):
			raise InvalidHeader('Invalid Host header')
		self.value = self.value.lower()


class XForwardedHost(Host):
	__name__ = 'X-Forwarded-Host'


class IfMatch(HeaderElement):
	__name__ = 'If-Match'


class IfModifiedSince(HeaderElement):
	__name__ = 'If-Modified-Since'


class IfNoneMatch(HeaderElement):
	__name__ = 'If-None-Match'


class IfRange(HeaderElement):
	pass


class IfUnmodifiedSince(HeaderElement):
	__name__ = 'If-Unmodified-Since'


class LastModified(HeaderElement):
	__name__ = 'Last-Modified'


class Location(HeaderElement):
	pass


class MaxForwards(HeaderElement):
	__name__ = 'Max-Forwards'


class Pragma(HeaderElement):
	pass


class ProxyAuthenticate(HeaderElement):
	__name__ = 'Proxy-Authenticate'


class ProxyAuthorization(HeaderElement):
	__name__ = 'Proxy-Authorization'


class Range(HeaderElement):
	pass


class Referer(HeaderElement):
	pass


class RetryAfter(HeaderElement):
	__name__ = 'Retry-After'


class Server(HeaderElement):
	pass


class TE(AcceptElement):
	pass


class Trailer(HeaderElement):
	forbidden_headers = ('Transfer-Encoding', 'Content-Length', 'Trailer')

	def __init__(self, value, params=None):
		super(Trailer, self).__init__(value, params)
		if value.title() in self.forbidden_headers:
			raise InvalidHeader(u'A Trailer header MUST NOT contain %r field' % value.title())


class TransferEncoding(CodecElement, HeaderElement):
	__name__ = 'Transfer-Encoding'

	# IANA assigned HTTP Transfer-Encoding values
	CODECS = {
		'chunked': None,
		'compress': NotImplementedError,
		'deflate': 'application/zlib',
		'gzip': 'application/gzip',
		'identity': NotImplementedError,
	}


class Upgrade(HeaderElement):
	pass


class UserAgent(HeaderElement):
	__name__ = 'User-Agent'


class Vary(HeaderElement):
	pass


class Via(HeaderElement):
	pass


class Warning(HeaderElement):
	pass


class WWWAuthenticate(HeaderElement):
	__name__ = 'WWW-Authenticate'


for member in locals().copy().values():
	if isinstance(member, HeaderType) and member is not HeaderElement:
		HEADER[member.__name__] = member
