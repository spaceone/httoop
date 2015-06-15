import pytest
from httoop.client import ComposedRequest


def test_chunked_body_without_trailer(request):
	def content():
		yield 'Let us test this chunked'
		yield '\n'
		yield 'Transfer Encoding.'
		yield ''
		yield 'It is nice '
		yield 'and seems to work'
	request.body = content()
	request.body.chunked = True
	assert '18\r\nLet us test this chunked\r\n1\r\n\n\r\n12\r\nTransfer Encoding.\r\nb\r\nIt is nice \r\n11\r\nand seems to work\r\n0\r\n\r\n' == bytes(request.body)


def test_parse_chunked_body_without_trailer(statemachine):
	request_body = ''.join([
		'This is a chunked body with some lines',
		'foo', 'bar', 'Baz', '\n', '', 'blah!', 'blub'
	])
	data = 'POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\nAccept: */*\r\nUser-Agent: httoop/0.0\r\nHost: localhost\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n26\r\nThis is a chunked body with some lines\r\n3\r\nfoo\r\n3\r\nbar\r\n3\r\nBaz\r\n1\r\n\n\r\n5\r\nblah!\r\n4\r\nblub\r\n0\r\n\r\n'
	request = statemachine.parse(data)[0][0]
	assert bytes(request.body) == request_body


def test_parse_chunked_body_without_trailer_2(request):
	request.body = [
		'This is a chunked body with some lines',
		'foo', 'bar', 'Baz', '\n', '', 'blah!', 'blub'
	]
	request_body = ''.join(request.body)
	request.method = 'POST'
	request.headers['Transfer-Encoding'] = 'chunked'
	request.headers['Host'] = 'localhost'
	c = ComposedRequest(request)
	c.prepare()
	''.join(c)


def test_chunked_body_with_trailer():
	pass


def test_chunked_body_with_untold_trailer():
	pass


def test_chunked_body_with_forbidden_trailer():
	pass


def test_body_gzip_compressed():
	pass


def test_body_deflate_compressed():
	pass


def test_body_invalid_gzip():
	pass


def test_body_invalid_deflate():
	pass
