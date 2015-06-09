# -*- coding: utf-8 -*-

from httoop.status.types import StatusType, HTTPStatusException
from httoop.util import Unicode


class MULTIPLE_CHOICES(object):
	u"""The server has multiple representations of the requested resource.
		And the client e.g. did not specify the Accept-header or
		the requested representation does not exists.
	"""
	__metaclass__ = StatusType
	code = 300

	def __init__(self, locations, *args, **kwargs):
		if isinstance(locations, (bytes, Unicode)):
			locations = [locations]
		locations = ', '.join(locations)
		super(MULTIPLE_CHOICES, self).__init__(locations, *args, **kwargs)


class MOVED_PERMANENTLY(object):
	u"""The the server knows the target resource but the URI
		is incorrect (wrong domain, trailing slash, etc.).
		It can also be send if a resource have moved or
		renamed to prevent broken links."""
	__metaclass__ = StatusType
	code = 301


class FOUND(object):
	__metaclass__ = StatusType
	code = 302


class SEE_OTHER(object):
	u"""The request has been processed but instead of serving a
		representation of the result or resource it links to another
		document which contains a static status message, etc. so
		the client is not forced to download the data.
		This is also useful for links like
		/release-latest.tar.gz -> /release-1.2.tar.gz"""
	__metaclass__ = StatusType
	code = 303


class NOT_MODIFIED(object):
	u"""The client already has the data which is provided through the
		information in the Etag or If-Modified-Since-header.
		The Date-header is required, the ETag-header and
		Content-Location-header are useful.
		Also the caching headers Expires, Cache-Control and Vary are
		required if they differ from those sent previously.
		TODO: what to do if the representation format has
		changed but not the representation itself?
		The response body has to be empty."""
	__metaclass__ = StatusType
	code = 304
	body = None

	def __init__(self, *args, **kwargs):
		# don't set location
		HTTPStatusException.__init__(self, *args, **kwargs)

	header_to_remove = ("Allow", "Content-Encoding", "Content-Language",
						"Content-Length", "Content-MD5", "Content-Range",
						"Content-Type", "Expires", "Location")


class USE_PROXY(object):
	__metaclass__ = StatusType
	code = 305

# Unused, HTTP1.0
#SWITCH_PROXY = class (object):
#	__metaclass__ = StatusType
#	code = 306


class TEMPORARY_REDIRECT(object):
	u"""The request has not processed because the requested
		resource is located at a different URI.
		The client should resent the request to the URI given in the Location-header.
		for GET this is the same as 303 but for POST, PUT and DELETE it is
		important that the request was not processed."""
	__metaclass__ = StatusType
	code = 307

class PERMANENT_REDIRECT(object):
	__metaclass__ = StatusType
	code = 308



