# -*- coding: utf-8 -*-
"""HTTP Header elements

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""
__all__ = ['HEADER', 'HeaderElement']

import re
# TODO: Via, Server, User-Agent can contain comments, parse them

from httoop.util import CaseInsensitiveDict, iteritems
from httoop.exceptions import InvalidHeader

# a mapping of all headers to HeaderElement classes
HEADER = CaseInsensitiveDict()


class HeaderType(type):
	def __new__(mcs, name, bases, dict):
		name = dict.get('__name__', name)
		return type.__new__(mcs, name, bases, dict)


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


class MimeType(object):
	u"""
		.. seealso:: rfc:`2046`

		.. seealso:: rfc:`3023`
	"""
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


class Accept(AcceptElement, MimeType):
	pass


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


class ContentEncoding(HeaderElement):
	__name__ = 'Content-Encoding'


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
	def __init__(self, value, params):
		super(HeaderElement, self).__init__(value, params)
		if value.title() in ('Transfer-Encoding', 'Content-Length', 'Trailer'):
			raise InvalidHeader(u'A Trailer header MUST NOT contain %r field' % value.title())


class TransferEncoding(HeaderElement):
	__name__ = 'Transfer-Encoding'


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


for local in locals().copy().values():
	if isinstance(local, HeaderType) and local is not HeaderElement:
		HEADER[local.__name__] = local
