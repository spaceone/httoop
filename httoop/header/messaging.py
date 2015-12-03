# -*- coding: utf-8 -*-
# TODO: Via, Server, User-Agent can contain comments → parse them
import re

from httoop.header.element import HeaderElement, _AcceptElement, _CookieElement, _HopByHopElement, _ListElement, MimeType
from httoop.util import Unicode
from httoop.exceptions import InvalidHeader, InvalidDate
from httoop.codecs import lookup


class CodecElement(object):

	CODECS = None

	raise_on_missing_codec = True

	def sanitize(self):
		super(CodecElement, self).sanitize()
		if self.value and self.codec is None and self.raise_on_missing_codec:
			raise InvalidHeader(u'Unknown %s: %r' % (self.__name__, self.value))

	@property
	def codec(self):
		try:
			mimetype = self.mimetype
		except AttributeError:
			mimetype = self.value

		for encoding in (self.value, mimetype):
			if self.CODECS is not None:
				encoding = self.CODECS.get(encoding)
				if not isinstance(encoding, (bytes, Unicode)):
					return encoding
			try:
				return lookup(encoding.lower())
			except KeyError:
				pass


class Accept(_AcceptElement, MimeType):

	def sanitize(self):
		super(Accept, self).sanitize()
		if self.value == '*':
			self.value = '*/*'


class AcceptCharset(_AcceptElement):
	__name__ = 'Accept-Charset'


class AcceptEncoding(_AcceptElement):
	__name__ = 'Accept-Encoding'


class AcceptLanguage(_AcceptElement):
	__name__ = 'Accept-Language'


class AcceptRanges(_AcceptElement):
	__name__ = 'Accept-Ranges'


class Allow(HeaderElement):
	pass


class Connection(_HopByHopElement, HeaderElement):

	priority = '\xff'


class ContentDisposition(HeaderElement):

	__name__ = 'Content-Disposition'

	from httoop.date import Date

	@property
	def filename(self):
		return self.params.get('filename')

	@property
	def attachment(self):
		return self.value == 'attachment'

	@property
	def form_data(self):
		return self.value == 'form-data'

	@property
	def inline(self):
		return self.value == 'inline'

	@property
	def creation_date(self):
		if 'creation-date' in self.params:
			return self.Date(self.params['creation-date'])

	@property
	def modification_date(self):
		if 'modification-date' in self.params:
			return self.Date(self.params['modification-date'])

	def sanitize(self):
		self.value = self.value.lower()
		if self.attachment:
			if b'inline' in self.params:
				raise InvalidHeader('Mixed Content-Disposition')
		elif self.inline:
			if b'attachment' in self.params:
				raise InvalidHeader('Mixed Content-Disposition')
		elif self.form_data:
			if b'form-data' in self.params:
				raise InvalidHeader('Mixed Content-Disposition')
		else:
			raise InvalidHeader(u'Unknown Content-Disposition: %r' % (self.value,))


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


class ContentType(HeaderElement, MimeType, CodecElement):

	__name__ = 'Content-Type'

	raise_on_missing_codec = False

	@property
	def charset(self):
		return self.params.get('charset', '')

	@charset.setter
	def charset(self, charset):
		self.params['charset'] = charset

	VALID_BOUNDARY = re.compile('^[ -~]{0,200}[!-~]$')

	def sanitize(self):
		super(ContentType, self).sanitize()
		if 'boundary' in self.params:
			self.sanitize_boundary()

	def sanitize_boundary(self):
		boundary = self.params['boundary'] = self.params['boundary'].strip('"')
		if not self.VALID_BOUNDARY.match(boundary):
			raise InvalidHeader(u'Invalid boundary in multipart form: %r' % (boundary,))

	@property
	def boundary(self):
		return self.params.get('boundary')

	@boundary.setter
	def boundary(self, boundary):
		self.params['boundary'] = boundary


class Cookie(_CookieElement):

	RE_SPLIT = re.compile(r'; ')

	@classmethod
	def join(cls, values):
		return b'; '.join(values)


class Date(HeaderElement):

	priority = '\x01'


class Expect(HeaderElement):
	pass


class From(HeaderElement):
	pass


# TODO: add case insensitve HeaderElement
class Host(HeaderElement):

	priority = '\x03'
	RE_HOSTNAME = re.compile(r'^([^\x00-\x1F\x7F()^\'"<>@,;:/\[\]={} \t\\\\"]+)$')
	HOSTPORT = re.compile(r'^(.*?)(?::(\d+))?$')

	@property
	def is_ip4(self):
		from socket import inet_pton, AF_INET, error
		try:
			inet_pton(AF_INET, self.host)
			return True
		except error:
			return False

	@property
	def is_ip6(self):
		from socket import inet_pton, AF_INET6, error
		try:
			inet_pton(AF_INET6, self.host)
			return True
		except error:
			return False

	@property
	def is_fqdn(self):
		return not self.is_ip4 and not self.is_ip6 and self.RE_HOSTNAME.match(self.host) is not None

	@property
	def fqdn(self):
		if self.is_fqdn:
			return self.host

	@property
	def hostname(self):
		return self.ip6address or self.ip4address or self.fqdn

	@property
	def ip6address(self):
		if self.is_ip6:
			return self.host

	@property
	def ip4address(self):
		if self.is_ip4:
			return self.host

	def sanitize(self):
		self.value = self.value.lower()
		self.host, self.port = self.HOSTPORT.match(self.value).groups()
		if self.host.endswith(']') and self.host.startswith('['):
			self.host = self.host[1:-1]
		if self.port:
			self.port = int(self.port)
		if not self.hostname:
			raise InvalidHeader('Invalid Host header')


class XForwardedHost(Host):
	__name__ = 'X-Forwarded-Host'


class Location(HeaderElement):
	pass


class MaxForwards(HeaderElement):

	__name__ = 'Max-Forwards'


class Referer(HeaderElement):
	pass


class RetryAfter(HeaderElement):

	__name__ = 'Retry-After'


class Server(HeaderElement):

	priority = '\x02'


class SetCookie(_ListElement, _CookieElement):

	__name__ = 'Set-Cookie'

	from httoop.date import Date

	@classmethod
	def split(cls, fieldvalue):
		fieldvalue = re.sub(b'(expires)=([^"][^;]+)', b'\\1="\\2"', fieldvalue, flags=re.I)
		return super(SetCookie, cls).split(fieldvalue)

	@property
	def httponly(self):
		return 'httponly' in self.params

	@property
	def secure(self):
		return 'secure' in self.params

	@property
	def path(self):
		return self.params.get('path')

	@property
	def domain(self):
		return self.params.get('domain')

	@property
	def persistent(self):
		return 'max-age' in self.params or 'expires' in self.params

	@property
	def max_age(self):
		if self.params.get('max-age'):
			try:
				return int(self.params['max-age'])
			except ValueError:
				raise InvalidHeader('Cookie: max-age is not a number: %r' % (self.params['max-age'],))

	@property
	def expires(self):
		if self.params.get('expires'):
			try:
				return self.Date(self.params['expires'])
			except InvalidDate:
				raise InvalidHeader('Cookie: expires is not a valid date: %r' % (self.params['expires'],))


class TE(_HopByHopElement, _AcceptElement):

	pass


class Trailer(_HopByHopElement, HeaderElement):

	forbidden_headers = ('Transfer-Encoding', 'Content-Length', 'Trailer')

	def sanitize(self):
		if self.value.title() in self.forbidden_headers:
			raise InvalidHeader(u'A Trailer header MUST NOT contain %r field' % self.value.title())


class TransferEncoding(_HopByHopElement, CodecElement, HeaderElement):
	__name__ = 'Transfer-Encoding'

	# IANA assigned HTTP Transfer-Encoding values
	CODECS = {
		'chunked': False,
		'compress': NotImplementedError,
		'deflate': 'application/zlib',
		'gzip': 'application/gzip',
		'identity': NotImplementedError,
	}


class Upgrade(_HopByHopElement, HeaderElement):
	pass


class UserAgent(HeaderElement):
	__name__ = 'User-Agent'


class Via(HeaderElement):
	pass


class HTTP2Settings(HeaderElement):
	__name__ = 'HTTP2-Settings'
