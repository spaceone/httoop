
class Protocol(object):
	def __get__(self, message, cls=None):
		if message is None:
			return self
		return message._Message__protocol

	def __set__(self, message, protocol):
		if not isinstance(protocol, Protocol):
			protocol = Protocol(protocol)
		message._Message__protocol = protocol

class Method(object):
	def __get__(self, request, cls=None):
		if request is None:
			return self
		return request._Request__method

	def __set__(self, request, method):
		request._Request__method = bytes(method)

class Status(object):
	def __get__(self, response, cls=None):
		if response is None:
			return self
		return response._Response__status

	def __set__(self, response, status):
		if response is status:
			return

		_self = response.status
		if isinstance(status, int):
			_self.status, _self.reason = status, REASONS.get(status, ('', ''))[0]
		elif isinstance(status, tuple):
			_self.status, _self.reason = status
		elif isinstance(status, bytes): # FIXME: python3
			_status, _reason = status.split(None, 1)
			_self.status, _self.reason = int(_status), _reason
		elif isinstance(status, Status):
			_self.status, _self.reason = status.status, status.reason
		else:
			raise ValueError('invalid type for an HTTP status code')

class URI(object):
	def __get__(self, request, cls=None):
		if request is None:
			return self
		return request._Request__uri

	def __set__(self, request, uri):
		if request is uri:
			return

		_self = request.uri
		if not isinstance(uri, URI):
			_self.parse(uri)
		else:
			# don't parse again because it might was sanitize()d
			_self.__dict__.update(dict(
				uri=uri.uri,
				scheme=uri.scheme,
				netloc=uri.netloc,
				username=uri.username,
				password=uri.password,
				host=uri.host,
				port=uri.port,
				path=uri.path,
				query_string=uri.query_string,
				fragment=uri.fragment
			))

class Headers(object):
	def __get__(self, message, cls=None):
		if message is None:
			return self
		return message._Message__headers

	def __set__(self, message, value):
		if message is value:
			return
		headertype = type(message._Message__headers)
		if not isinstance(value, headertype):
			value = headertype(value)
		message._Message__headers = value

class Body(object):
	def __get__(self, message, cls=None):
		if message is None:
			return self
		return message._Message__body

	def __set__(self, message, body):
		if message is body:
			return

		message.body.set(body)
