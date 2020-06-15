from __future__ import unicode_literals
import pytest
from httoop import BAD_REQUEST, URI_TOO_LONG, HTTP_VERSION_NOT_SUPPORTED, LENGTH_REQUIRED, SWITCHING_PROTOCOLS, MOVED_PERMANENTLY, NOT_IMPLEMENTED


def test_statemachine_parsing_with_streamed_input():
	pass


def test_parse_continuation_lines(clientstatemachine):
	clientstatemachine.parse(b'HTTP/1.1 200 OK\r\nHost: foo\r\n')
	assert not clientstatemachine.message.headers
	clientstatemachine.parse(b'Content-Type: text/\r\n')
	assert clientstatemachine.message.headers == {"Host": b"foo"}
	clientstatemachine.parse(b' ht\r\n')
	clientstatemachine.parse(b'\tml\r\n')
	assert clientstatemachine.message.headers == {"Host": b"foo"}
	clientstatemachine.parse(b'f')
	clientstatemachine.parse(b'oo')
	assert clientstatemachine.message.headers == {"Host": b"foo", "Content-Type": b"text/html"}
	clientstatemachine.parse(b': bar\r')
	clientstatemachine.parse(b'\n baz\r\nContent-Length: 0\r\n')
	assert clientstatemachine.message.headers == {"Host": b"foo", "Content-Type": b"text/html", "Foo": b"barbaz"}
	assert clientstatemachine.parse(b'\r\n')[0].headers == {"Host": b"foo", "Content-Type": b"text/html", "Foo": b"barbaz", "Content-Length": b"0"}


def test_parse_without_header(clientstatemachine):
	response = clientstatemachine.parse(b'HTTP/1.0 202 OK\r\n\r\n')[0]
	assert response.protocol == (1, 0)
	assert response.status == 202
	assert not response.body


def test_host_header_required(statemachine):
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'GET / HTTP/1.1\r\nContent-Length: 0\r\n\r\n')
	assert 'Missing Host header' in str(exc.value.description)
	statemachine.parse(b'GET / HTTP/1.0\r\nContent-Length: 0\r\n\r\n')


def test_max_uri_length(statemachine):
	statemachine.MAX_URI_LENGTH = 100
	path = b'A' * (statemachine.MAX_URI_LENGTH - 5)
	statemachine.parse(b'GET /%s HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n' % (path,))
	with pytest.raises(URI_TOO_LONG) as exc:
		path = b'A' * statemachine.MAX_URI_LENGTH
		statemachine.parse(b'GET /%s HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n' % (path,))
	assert 'The maximum length of the request is 100' in str(exc.value.description)


def test_max_request_line_length(statemachine):
	statemachine.MAX_URI_LENGTH = 100
	with pytest.raises(URI_TOO_LONG) as exc:
		path = b'A' * statemachine.MAX_URI_LENGTH
		statemachine.parse(b'GET /%s HTTP/' % (path,))
		statemachine.parse(b'1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n')
	assert 'The maximum length of the request is 100' in str(exc.value.description)


@pytest.mark.parametrize('protocol_version', [b'1.2', pytest.param(b'0.9', marks=pytest.mark.xfail(reason='No check for minimum version yet.')), b'2.0'])
def test_max_protocol(statemachine, protocol_version):
	with pytest.raises(HTTP_VERSION_NOT_SUPPORTED) as exc:
		statemachine.parse(b'GET / HTTP/%s\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n' % (protocol_version,))
	assert 'The server only supports HTTP/1.0 and HTTP/1.1.' in str(exc.value.description)


def test_body_length_required(statemachine):
	with pytest.raises(LENGTH_REQUIRED) as exc:
		statemachine.parse(b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\nabcde')
	assert 'Missing Content-Length header.' in str(exc.value.description)


@pytest.mark.parametrize('method', [b'GET', b'HEAD', b'TRACE'])
def test_safe_request_with_body(statemachine, method):
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'%s / HTTP/1.1\r\nHost: example.com\r\nContent-Length: 5\r\n\r\nabcde' % (method,))
	assert 'is considered as safe and MUST NOT contain a request body.' in str(exc.value.description)


def test_redirection_with_unusual_path(statemachine):
	with pytest.raises(MOVED_PERMANENTLY):
		statemachine.parse(b'GET /../user HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n')


def test_invalid_uri_schemes(statemachine):
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'GET ftp://example.com/ HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n')
	# assert 'Invalid URL: wrong scheme' in str(exc.value.description)
	assert 'The request URI scheme must be HTTP based.' in str(exc.value.description)


def test_invalid_uri_fragment(statemachine):
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'GET /foo#bar HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n')
	assert 'The request URI must not contain fragments or user information.' in str(exc.value.description)


@pytest.mark.parametrize('double_slash', [b'//foo', b'http://example.com//foo'])
def test_invalid_uri_double_slash(statemachine, double_slash):
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'GET %s HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n' % (double_slash,))
	assert 'The request URI must be an absolute path or contain a scheme.' in str(exc.value.description) or 'The request URI path must not start with //.' in str(exc.value.description)


@pytest.mark.parametrize('slash_path', [b'foo'])
def test_invalid_uri_path_slash(statemachine, slash_path):
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'GET %s HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n' % (slash_path,))
	assert 'The request URI path must start with /.' in str(exc.value.description)


@pytest.mark.parametrize('slash_path', [b'*', b'http://example.com'])  # TODO: allow only on CONNECT?
def test_uri_star(statemachine, slash_path):
	statemachine.parse(b'GET %s HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n' % (slash_path,))


@pytest.mark.parametrize('connect_uri', [b'/foo'])
def test_invalid_uri_connect(statemachine, connect_uri):
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'CONNECT %s HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\n\r\n' % (connect_uri,))
	assert 'The request URI of an CONNECT request must be a authority.' in str(exc.value.description)


def test_http2_upgrade(statemachine):
	statemachine.parse(b'GET / HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\nConnection: Upgrade, HTTP2-Settings\r\nUpgrade: h2c\r\nHTTP2-Settings: Zm9v\r\n\r\n')
	statemachine.HTTP2 = type(statemachine)
	with pytest.raises(SWITCHING_PROTOCOLS):
		statemachine.parse(b'GET / HTTP/1.1\r\nHost: example.com\r\nContent-Length: 0\r\nConnection: Upgrade, HTTP2-Settings\r\nUpgrade: h2c\r\nHTTP2-Settings: Zm9v\r\n\r\n')
	assert statemachine.response.headers['Upgrade'] == 'h2c'
	assert statemachine.response.headers['Connection'] == 'Upgrade'


def test_removed_invalid_headers(clientstatemachine):
	clientstatemachine.request.method = 'CONNECT'
	response = clientstatemachine.parse(b'HTTP/1.0 202 OK\r\nTransfer-Encoding: chunked\r\nContent-Length: 5\r\n\r\n')[0]
	assert 'Transfer-Encoding' not in response.headers
	assert not response.headers.get('Content-Length') or response.headers.get('Content-Length') == '0'


def test_parse_message_with_content_length_header(statemachine):
	statemachine.parse(b'POST / HTTP/1.1\r\nHost: www.example.com\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 7\r\n\r\nfoo=')
	request = statemachine.parse(b'bar')[0][0]
	assert bytes(request.body) == b'foo=bar'


@pytest.mark.xfail()  # FIXME: new line not recognized in header parsing
def test_parse_message_without_carriage_return(statemachine):
	statemachine.parse(b'POST / HTTP/1.1\nHost: www.example.com\nContent-Type: application/x-www-form-urlencoded\nContent-Length: 7\n\nfoo=')
	request = statemachine.parse(b'bar')[0][0]
	assert bytes(request.body) == b'foo=bar'


@pytest.mark.parametrize('cl', [b'-1', b'a', b'1_0'])
def test_parse_invalid_content_length(statemachine, cl):
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'POST / HTTP/1.1\r\nHost: www.example.com\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %s\r\n\r\nfoo=' % (cl,))
	assert 'Invalid Content-Length header' in str(exc.value.description)


def test_parse_unknown_transfer_encoding(statemachine):
	with pytest.raises(NOT_IMPLEMENTED) as exc:
		statemachine.parse(b'POST / HTTP/1.1\r\nHost: www.example.com\r\nTransfer-Encoding: foo\r\n\r\nfoo=')
	assert 'Unknown HTTP/1.1 Transfer-Encoding' in str(exc.value.description)


def test_parse_unknown_content_encoding(statemachine):
	with pytest.raises(NOT_IMPLEMENTED) as exc:
		statemachine.parse(b'POST / HTTP/1.1\r\nHost: www.example.com\r\nContent-Encoding: foo\r\n\r\nfoo=')
	assert 'Unknown Content-Encoding' in str(exc.value.description)


def test_parse_invalid_header_as_bad_request(statemachine):
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'GET / HTTP/1.1\r\nHost: www.example.com\r\nFoo\r\n\r\n')
	assert 'Invalid header line' in str(exc.value)


def test_parse_invalid_trailer_as_bad_request(statemachine):
	statemachine.parse(b'POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\nTrailer: Foo, bar\r\nAccept: */*\r\nUser-Agent: httoop/0.0\r\nHost: localhost\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n')
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'11\r\nand seems to work\r\n0\r\nBar baz\r\nfoo: test\r\n\r\n')
	assert 'Invalid trailers' in str(exc.value)


def test_parse_request_startline_in_chunks(statemachine):
	statemachine.parse(b'GET')
	statemachine.parse(b' ')
	statemachine.parse(b'/')
	statemachine.parse(b' ')
	statemachine.parse(b'HTTP/')
	statemachine.parse(b'1.1\r')
	statemachine.parse(b'\n')
	statemachine.parse(b'Host: www.example.com\r\n\r\n')[0][0]


def test_parse_response_startline_in_chunks(clientstatemachine):
	clientstatemachine.parse(b'HTTP')
	clientstatemachine.parse(b'/')
	clientstatemachine.parse(b'1.1')
	clientstatemachine.parse(b' ')
	clientstatemachine.parse(b'200')
	clientstatemachine.parse(b' ')
	clientstatemachine.parse(b'OK\r')
	clientstatemachine.parse(b'\n')
	clientstatemachine.parse(b'\r\n')[0]
