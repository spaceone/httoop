from httoop.messages import Message


def test_repr(request, response):
	to_test = (
		request, request.body, request.method,
		request.protocol, response, Message(),
		response.status, response.headers)
	for e in to_test:
		assert repr(e).startswith('<HTTP')
		assert repr(e).endswith('>')

	assert repr(request.uri).startswith('<URI')
	assert repr(request.uri).endswith('>')

