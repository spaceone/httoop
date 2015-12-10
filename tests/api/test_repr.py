from httoop.messages import Message
from httoop import Date


def test_repr(request_, response):
	to_test = (
		request_, request_.body, request_.method,
		request_.protocol, response, Message(),
		response.status, response.headers, Date())
	for e in to_test:
		assert repr(e).startswith('<HTTP')
		assert repr(e).endswith('>')

	assert repr(request_.uri).startswith('<URI')
	assert repr(request_.uri).endswith('>')

