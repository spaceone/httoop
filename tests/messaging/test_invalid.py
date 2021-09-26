from __future__ import unicode_literals

import pytest

from httoop.exceptions import InvalidLine, InvalidURI


@pytest.mark.parametrize('token', (b'GET /', b'GET / foo HTTP/1.1', b'foo bar baz blah'))
def test_invalid_request_startline(token, request_):
	with pytest.raises(InvalidLine):
		request_.parse(token)


@pytest.mark.parametrize('token', (b'GET // HTTP/1.1', b'GET //example.com/ HTTP/1.1'))
def test_invalid_request_uri_startline(token, request_):
	with pytest.raises(InvalidURI):
		request_.parse(token)


@pytest.mark.parametrize('token', (b'HTTP/1.1', b'foo', b'FOOO/1.1 200 OK'))
def test_invalid_response_startline(token, response):
	with pytest.raises(InvalidLine):
		response.parse(token)
