# -*- coding: utf-8 -*-

from httoop.status.types import StatusException
from httoop.util import Unicode


class RedirectStatus(StatusException):
	u"""REDIRECTIONS = 3xx
		A redirection to other URI(s) which are set in the Location-header.
	"""

	location = None

	def __init__(self, location, *args, **kwargs):
		if location is not None:
			kwargs.setdefault('headers', {})['Location'] = location
		super(RedirectStatus, self).__init__(*args, **kwargs)

	def to_dict(self):
		dct = super(RedirectStatus, self).to_dict()
		if self.headers.get('Location'):
			dct.update(dict(Location=self.headers['Location']))
		return dct


class MULTIPLE_CHOICES(RedirectStatus):
	u"""The server has multiple representations of the requested resource.
		And the client e.g. did not specify the Accept-header or
		the requested representation does not exists.
	"""

	code = 300

	def __init__(self, locations, *args, **kwargs):
		if isinstance(locations, (bytes, Unicode)):
			locations = [locations]
		locations = ', '.join(locations)
		super(MULTIPLE_CHOICES, self).__init__(locations, *args, **kwargs)


class MOVED_PERMANENTLY(RedirectStatus):
	u"""The the server knows the target resource but the URI
		is incorrect (wrong domain, trailing slash, etc.).
		It can also be send if a resource have moved or
		renamed to prevent broken links."""

	code = 301


class FOUND(RedirectStatus):

	code = 302


class SEE_OTHER(RedirectStatus):
	u"""The request has been processed but instead of serving a
		representation of the result or resource it links to another
		document which contains a static status message, etc. so
		the client is not forced to download the data.
		This is also useful for links like
		/release-latest.tar.gz -> /release-1.2.tar.gz"""

	code = 303


class NOT_MODIFIED(RedirectStatus):
	u"""The client already has the data which is provided through the
		information in the Etag or If-Modified-Since-header.
		The Date-header is required, the ETag-header and
		Content-Location-header are useful.
		Also the caching headers Expires, Cache-Control and Vary are
		required if they differ from those sent previously.
		TODO: what to do if the representation format has
		changed but not the representation itself?
		The response body has to be empty."""

	code = 304
	body = None

	def __init__(self, *args, **kwargs):
		# don't set location
		super(NOT_MODIFIED, self).__init__(self, None, *args, **kwargs)

	header_to_remove = ("Allow", "Content-Encoding", "Content-Language",
						"Content-Length", "Content-MD5", "Content-Range",
						"Content-Type", "Expires", "Location")


class USE_PROXY(RedirectStatus):

	code = 305

# Unused, HTTP1.0
#SWITCH_PROXY = class (RedirectStatus):
#
#	code = 306


class TEMPORARY_REDIRECT(RedirectStatus):
	u"""The request has not processed because the requested
		resource is located at a different URI.
		The client should resent the request to the URI given in the Location-header.
		for GET this is the same as 303 but for POST, PUT and DELETE it is
		important that the request was not processed."""

	code = 307

class PERMANENT_REDIRECT(RedirectStatus):

	code = 308



