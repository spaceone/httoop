from __future__ import unicode_literals
from httoop.semantic.request import ComposedRequest


def test_chunked_body_without_trailer(request_):
	def content():
		yield 'Let us test this chunked'
		yield '\n'
		yield 'Transfer Encoding.'
		yield ''
		yield 'It is nice '
		yield 'and seems to work'
	request_.body = content()
	request_.body.chunked = True
	assert b'18\r\nLet us test this chunked\r\n1\r\n\n\r\n12\r\nTransfer Encoding.\r\nb\r\nIt is nice \r\n11\r\nand seems to work\r\n0\r\n\r\n' == bytes(request_.body)


def test_parse_chunked_body_without_trailer(statemachine):
	request_body = b''.join([
		b'This is a chunked body with some lines',
		b'foo', b'bar', b'Baz', b'\n', b'', b'blah!', b'blub'
	])
	data = b'POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\nAccept: */*\r\nUser-Agent: httoop/0.0\r\nHost: localhost\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n26\r\nThis is a chunked body with some lines\r\n3\r\nfoo\r\n3\r\nbar\r\n3\r\nBaz\r\n1\r\n\n\r\n5\r\nblah!\r\n4\r\nblub\r\n0\r\n\r\n'
	request_ = statemachine.parse(data)[0][0]
	assert bytes(request_.body) == request_body


def test_parse_chunked_body_without_trailer_2(request_):
	request_.body = [
		'This is a chunked body with some lines',
		'foo', 'bar', 'Baz', '\n', '', 'blah!', 'blub'
	]
	b''.join(request_.body)
	request_.method = 'POST'
	request_.headers['Transfer-Encoding'] = 'chunked'
	request_.headers['Host'] = 'localhost'
	c = ComposedRequest(request_)
	c.prepare()
	b''.join(c)


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
