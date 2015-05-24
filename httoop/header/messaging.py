# -*- coding: utf-8 -*-
# TODO: Via, Server, User-Agent can contain comments → parse them
import re

from httoop.header.element import HeaderElement, AcceptElement, MimeType, CodecElement
from httoop.exceptions import InvalidHeader


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


class Allow(HeaderElement):
	pass


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
		return self.ip6address or \
			self.ip4address or \
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


class Location(HeaderElement):
	pass


class MaxForwards(HeaderElement):
	__name__ = 'Max-Forwards'


class Pragma(HeaderElement):
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


class Via(HeaderElement):
	pass


class HTTP2Settings(HeaderElement):
	__name__ = 'HTTP2-Settings'
