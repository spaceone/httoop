import pytest

from httoop.semantic.request import ComposedRequest
from httoop.semantic.response import ComposedResponse


def test_composing(request_, response):
	c = ComposedResponse(response, request_)
	c.prepare()


def test_request_close(request_):
	c = ComposedRequest(request_)
	c.close = True
	assert request_.headers['Connection'] == 'close'


def test_request_trace_header_removal(request_):
	request_.headers['Cookie'] = 'foo=bar'
	request_.headers['WWW-Authenticate'] = 'foo bar'
	request_.method = 'TRACE'
	c = ComposedRequest(request_)
	c.prepare()
	assert 'Cookie' not in request_.headers
	assert 'WWW-Authenticate' not in request_.headers


def test_request_host_header_set(request_):
	request_.uri = 'http://www.example.com/foo'
	c = ComposedRequest(request_)
	c.prepare()
	assert request_.headers['Host'] == 'www.example.com'


def test_request_defaults(request_):
	request_.body = 'foo'
	c = ComposedRequest(request_)
	c.chunked = True
	c.prepare()
	assert 'User-Agent' in request_.headers
	assert 'Accept' in request_.headers
	assert not request_.body
	assert not c.chunked


@pytest.mark.parametrize('method', ['POST', 'PUT'])
def test_request_defaults_body(request_, method):
	request_.method = method
	request_.body = 'foo'
	c = ComposedRequest(request_)
	c.prepare()
	assert 'Date' in request_.headers
	assert request_.headers.get('Content-Length') == '3'


def test_chunked(request_):
	c = ComposedRequest(request_)
	c.transfer_encoding = None
	c.transfer_encoding = b'chunked'
	assert c.chunked
	c.chunked = False
	assert 'Transfer-Encoding' not in request_.headers
	assert not c.transfer_encoding


@pytest.mark.parametrize('status', [100, 204, 205, 304])
def test_response_no_body(request_, response, status):
	response.status = status
	response.body = 'foo'
	c = ComposedResponse(response, request_)
	c.prepare()
	assert not response.body


def test_response_no_body_head(request_, response):
	response.body = 'foo'
	request_.method = 'HEAD'
	c = ComposedResponse(response, request_)
	c.prepare()
	assert not response.body


def test_response_allow_default_header(request_, response):
	response.status = 405
	c = ComposedResponse(response, request_)
	c.prepare()
	assert response.headers['Allow'] == 'GET, HEAD'


def test_byte_ranges(request_, response):
	request_.headers['Range'] = 'bytes=3-5'
	response.headers['ETag'] = 'foo'
	response.body = 'foobarbaz'
	c = ComposedResponse(response, request_)
	c.prepare()
	assert response.headers['Accept-Ranges'] == 'bytes'
	assert bytes(response.body) == b'bar'
	assert response.headers['Content-Range'] == 'bytes 3-5/9'


def test_invalid_byte_ranges(request_, response):
	request_.headers['Range'] = 'bytes=5-3'
	response.headers['ETag'] = 'foo'
	response.body = 'foobarbaz'
	c = ComposedResponse(response, request_)
	c.prepare()
	assert response.headers['Accept-Ranges'] == 'bytes'
	assert bytes(response.body) == b'foobarbaz'
	assert 'Content-Range' not in response.headers


def test_multipart_byte_ranges(request_, response):
	request_.headers['Range'] = 'bytes=0-2, 6-'
	response.headers['ETag'] = 'foo'
	response.body = 'foobarbaz'
	c = ComposedResponse(response, request_)
	c.prepare()
	assert response.headers['Accept-Ranges'] == 'bytes'
	assert response.headers['Content-Type'].startswith('multipart/byteranges; boundary=')
	assert bytes(response.body) == b'--%(boundary)s\r\nContent-Range: bytes 0-2/9\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nfoo\r\n--%(boundary)s\r\nContent-Range: bytes 6-9/9\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nbaz\r\n--%(boundary)s--\r\n' % {b'boundary': response.headers.get_element('Content-Type').boundary.encode('ASCII')}


def test_content_range_is_set(request_, response):
	response.status = 416
	response.body = 'foobarbaz'
	c = ComposedResponse(response, request_)
	c.prepare()
	assert response.headers['Content-Range'] == 'bytes */9'


def test_response_trace_header_removal(request_, response):
	response.headers['Set-Cookie'] = 'foo=bar'
	request_.method = 'TRACE'
	c = ComposedResponse(response, request_)
	c.prepare()
	assert 'Set-Cookie' not in response.headers


def test_response_close(request_, response):
	c = ComposedResponse(response, request_)
	c.close = True
	assert response.headers['Connection'] == 'close'
	c.close = False
	assert 'Connection' not in response.headers
	response.protocol = (1, 0)
	c.close = False
	assert response.headers['Connection'] == 'keep-alive'
