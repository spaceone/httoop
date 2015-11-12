# -*- coding: utf-8 -*-

from httoop.status.types import StatusException


class SuccessStatus(StatusException):
	u"""SUCCESS = 2xx
		indicates that an operation was successful.
	"""


class OK(SuccessStatus):
	u"""The request was successful.
		On GET requests the entity body will be a
		representation of the requested resource.
		For other methods the entity body contains a representation of
		the current state of the resource or a description of the performed action
	"""

	code = 200


class CREATED(SuccessStatus):
	u"""A new resource was created.
		This should only be send on POST and PUT requests.
		The Location-Header should contain the URI to the created resource.
		The entity-body should describe and link to the created resource.
	"""

	code = 201

	def __init__(self, location, *args, **kwargs):
		kwargs.setdefault('headers', {})['Location'] = location
		super(CREATED, self).__init__(*args, **kwargs)

	def to_dict(self):
		dct = super(CREATED, self).to_dict()
		dct.update(dict(Location=self.headers['Location']))
		return dct


class ACCEPTED(SuccessStatus):
	u"""The request looks valid but will be procecced later.
		It is an asynchronous action.
		The Location-Header should contain a URI where
		the status of processing can be found.
		If this is not possible it should give an estimate
		time when the request will be processed."""

	code = 202


class NON_AUTHORITATIVE_INFORMATION(SuccessStatus):
	u"""Everything is OK but the response headers
		may be altered by a third party."""

	code = 203


class NO_CONTENT(SuccessStatus):
	u"""GET: The representation of the resource is empty.
		other request methods: the status message or representation is not needed.
		This is useful for ajax requests.
		It is also useful for making series of edits
		to a single record (a HTML POST form)."""

	code = 204
	body = None


class RESET_CONTENT(SuccessStatus):
	u"""The same as 204 but this indicated that the client should
		reset the view of its data structure.
		This is useful for entering a series of records
		in succession (a HTML POST form).
	"""

	code = 205
	body = None


class PARTIAL_CONTENT(SuccessStatus):
	u"""Partial GET:
		The response does not contain the full representation of a resource
		but only the bytes requested in the Content-Range-header.
		It is often use to resume an interrupted download.
		The Date-header is required, the ETag-header
		and Content-Location-header are useful.
	"""

	code = 206


class MULTI_STATUS(SuccessStatus):
	"""This status code indicated that the entity-body contains information
	about the states of the batch request.
	It is not an official HTTP-Status-Code: WebDAV
	It is not realy RESTful to use.
	The entity-body is descripted in RFC 2518."""

	code = 207


class ALREADY_REPORTED(SuccessStatus):

	code = 208


class IM_USED(SuccessStatus):

	code = 226
