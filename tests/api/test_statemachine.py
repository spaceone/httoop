from __future__ import unicode_literals
import pytest
from httoop import BAD_REQUEST


def test_statemachine_parsing_with_streamed_input():
	pass


def test_parse_continuation_lines(clientstatemachine):
	clientstatemachine.parse(b'HTTP/1.1 200 OK\r\nHost: foo\r\n')
	assert not clientstatemachine.message.headers
	clientstatemachine.parse(b'Content-Type: text/\r\n')
	assert clientstatemachine.message.headers == {"Host": "foo"}
	clientstatemachine.parse(b' ht\r\n')
	clientstatemachine.parse(b'\tml\r\n')
	assert clientstatemachine.message.headers == {"Host": "foo"}
	clientstatemachine.parse(b'f')
	clientstatemachine.parse(b'oo')
	assert clientstatemachine.message.headers == {"Host": "foo", "Content-Type": "text/html"}
	clientstatemachine.parse(b': bar\r')
	clientstatemachine.parse(b'\n baz\r\nContent-Length: 0\r\n')
	assert clientstatemachine.message.headers == {"Host": "foo", "Content-Type": "text/html", "Foo": "barbaz"}
	assert clientstatemachine.parse(b'\r\n')[0].headers == {"Host": "foo", "Content-Type": "text/html", "Foo": "barbaz", "Content-Length": "0"}


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
