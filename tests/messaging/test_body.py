from __future__ import unicode_literals

import sys
import pytest

from httoop.semantic.request import ComposedRequest
from httoop.semantic.response import ComposedResponse
from httoop import BAD_REQUEST
from httoop.codecs import lookup


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


@pytest.mark.skipif(sys.version_info[:2] == (3, 5), reason='exception handling broken in py3.[4,5}')
@pytest.mark.xfail(reason='501 not implemented. why?!')
def test_parse_transfer_encoding_deflate(statemachine):
	statemachine.parse(b'POST / HTTP/1.1\r\nTransfer-Encoding: deflate\r\nAccept: */*\r\nUser-Agent: httoop/0.0\r\nHost: localhost\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n')
	request = statemachine.parse(b'x\x9c+\xc9\xc8,V\x00\xa2D\x85\x92\xd4\xe2\x12\x00&3\x05\x16')[0][0]
	assert request.body == 'this is a test'


def test_body_parse_transfer_encoding_deflate(request_):
	request_.body.transfer_encoding = 'deflate'
	request_.body.parse(b'x\x9c+\xc9\xc8,V\x00\xa2D\x85\x92\xd4\xe2\x12\x00&3\x05\x16')
	assert request_.body == 'this is a test'


def test_parse_chunked_body_with_trailer(statemachine):
	statemachine.parse(b'POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\nTrailer: Foo, bar\r\nAccept: */*\r\nUser-Agent: httoop/0.0\r\nHost: localhost\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n')
	statemachine.parse(b'11\r\nand seems to work\r\n0\r\nBar: baz\r\nfoo:')
	request_ = statemachine.parse(b' test\r\n\r\n')[0][0]
	assert request_.headers['Trailer'] == 'Foo, bar'
	assert request_.headers['foo'] == 'test'
	assert request_.headers['Bar'] == 'baz'


def test_parse_chunked_body_with_untold_trailer(statemachine):
	statemachine.parse(b'POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\nTrailer: Foo\r\nAccept: */*\r\nUser-Agent: httoop/0.0\r\nHost: localhost\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n')
	statemachine.parse(b'18\r\nLet us test ')
	statemachine.parse(b'this chunked\r\n1\r\n\n\r\n')
	statemachine.parse(b'12\r')
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'\nTransfer Encoding.\r\nb\r\nIt is nice \r\n11\r\nand seems to work\r\n0\r\nBar: baz\r\nFoo: test\r\n\r\n')[0][0]
	assert 'untold trailers: "Bar"' in str(exc.value)


def test_chunked_body_with_trailer(request_):
	def content():
		yield 'Let us test this chunked'
		yield '\n'
		yield 'Transfer Encoding.'
		yield ''
		yield 'It is nice '
		yield 'and seems to work'
	request_.body = content()
	request_.body.chunked = True
	request_.headers['Trailer'] = 'Foo, bar'
	request_.headers['foo'] = 'test'
	request_.headers['Bar'] = 'baz'
	request_.body.trailer = request_.trailer
	assert b'18\r\nLet us test this chunked\r\n1\r\n\n\r\n12\r\nTransfer Encoding.\r\nb\r\nIt is nice \r\n11\r\nand seems to work\r\n0\r\nBar: baz\r\nFoo: test\r\n\r\n' == bytes(request_.body)


def test_chunked_body_with_untold_trailer():
	pass


def test_chunked_body_with_forbidden_trailer():
	pass


def test_chunked_body_without_mentioned_trailer(statemachine):
	statemachine.parse(b'POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\nTrailer: Foo, bar, foo\r\nAccept: */*\r\nUser-Agent: httoop/0.0\r\nHost: localhost\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n')
	assert statemachine.parse(b'11\r\nand seems to work\r\n0\r\nfoo: test\r\n\r\n')[0][0].trailer == {u'Foo': b'test'}


def test_body_gzip_compressed(request_, response, clientstatemachine):
	response.body = u'this is a test'
	response.headers['Content-Encoding'] = 'gzip'
	c = ComposedResponse(response, request_)
	c.prepare()
	assert b'Content-Encoding: gzip\r\n' in bytes(c.response.headers)
	assert b'Transfer-Encoding: chunked\r\n' in bytes(c.response.headers)  # automatically added
	# assert bytes(c.response.body) == b'20\r\n\x1f\x8b\x00N\xed\xdb^\x02\xff+\xc9\xc8,V\x00\xa2D\x85\x92\xd4\xe2\x12\x00\xea\xe7\x1e\r\x0e\x00\x00\x00\r\n0\r\n\r\n'
	clientstatemachine.request = request_
	clientstatemachine.parse(bytes(c.response))
	clientstatemachine.parse(bytes(c.response.headers))
	res = clientstatemachine.parse(bytes(c.response.body))[0]
	assert str(res.body) == 'this is a test'


def test_body_deflate_compressed(request_, response, clientstatemachine):
	response.body = u'this is a test'
	response.headers['Content-Encoding'] = 'deflate'
	c = ComposedResponse(response, request_)
	c.prepare()
	assert b'Content-Encoding: deflate\r\n' in bytes(c.response.headers)
	assert b'Transfer-Encoding: chunked\r\n' in bytes(c.response.headers)  # automatically added
	print(repr(bytes(c.response.body)))
	clientstatemachine.request = request_
	clientstatemachine.parse(bytes(c.response))
	clientstatemachine.parse(bytes(c.response.headers))
	res = clientstatemachine.parse(bytes(c.response.body))[0]
	assert str(res.body) == 'this is a test'


@pytest.mark.parametrize('chunk_size', [b'-18', b'fg'])
def test_parse_chunked_body_with_invalid_chunk_size(statemachine, chunk_size):
	statemachine.parse(b'POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\nTrailer: Foo\r\nAccept: */*\r\nUser-Agent: httoop/0.0\r\nHost: localhost\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n')
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'%s\r\nLet us test ' % (chunk_size,))
	assert 'Invalid chunk size' in str(exc.value)


def test_parse_chunked_body_with_invalid_terminator(statemachine):
	statemachine.parse(b'POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\nAccept: */*\r\nUser-Agent: httoop/0.0\r\nHost: localhost\r\nContent-Type: text/plain; charset="UTF-8"\r\n\r\n')
	with pytest.raises(BAD_REQUEST) as exc:
		statemachine.parse(b'11\r\nand seems to work!\r\n0\r\n\r\n')
	assert 'Invalid chunk terminator' in str(exc.value.description)


def test_body_compress(request_):
	request_.body = 'this is a test'
	request_.body.content_encoding = 'deflate'
	request_.body.compress()
	assert lookup('application/zlib').decode(bytes(request_.body)) == 'this is a test'


def test_body_encode_none(request_):
	request_.body.mimetype = 'application/json'
	request_.body.encode()
