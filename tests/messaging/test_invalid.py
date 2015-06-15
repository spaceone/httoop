import pytest
from httoop.exceptions import InvalidLine, InvalidURI


def test_invalid_request_startline(request):
	for token in (b'GET /', b'GET / foo HTTP/1.1', b'foo bar baz blah'):
		with pytest.raises(InvalidLine):
			request.parse(token)
	for token in (b'GET // HTTP/1.1', 'GET //example.com/ HTTP/1.1'):
		with pytest.raises(InvalidURI):
			request.parse(token)

def test_invalid_response_startline(response):
	for token in (b'HTTP/1.1', b'foo', b'FOOO/1.1 200 OK'):
		with pytest.raises(InvalidLine):
			response.parse(token)
