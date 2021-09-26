# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from httoop import Headers, InvalidHeader
from httoop.util import to_unicode


def test_merging_header(headers):
	h2 = Headers()
	headers['Host'] = 'localhost'
	h2['Host'] = 'localhost'
	headers['Accept'] = 'text/plain; q=1.6, text/html; q=0.3'
	h2['Accept'] = 'application/json; q=0.4'
	h2['Foo'] = 'bar'
	headers.merge(h2)
	assert set(headers.keys()) == set(['Host', 'Accept', 'Foo'])
	assert headers['Host'] == 'localhost, localhost'
	assert headers['Accept'] == 'text/plain; q=1.6, application/json; q=0.4, text/html; q=0.3'
	assert headers['Foo'] == 'bar'


def test_replace_headers(request_):
	request_.headers['A'] = 'a'
	request_.headers['B'] = 'B'
	request_.headers['C'] = 'c'
	request_.headers = {'D': 'D', 'E': 'e'}
	assert set(request_.headers.keys()) == {'D', 'E'}
	assert request_.headers['D'] == 'D'
	assert request_.headers['E'] == 'e'


def test_trailer(request_):
	request_.headers['A'] = 'a'
	request_.headers['B'] = 'B'
	request_.headers['C'] = 'c'
	request_.headers['D'] = 'D'
	request_.headers['E'] = 'e'
	request_.headers['Trailer'] = 'B, C, E, F'
	assert set(request_.trailer.keys()) == {'B', 'C', 'E'}
	assert request_.trailer['B'] == 'B'
	assert request_.trailer['C'] == 'c'
	assert request_.trailer['E'] == 'e'


def test_string_type(headers):
	headers['Content-Type'] = 'text/html'
	assert headers.get('Content-Type', '').startswith('text/html')


def test_utf8_in_headers(headers):
	headers['foo'] = u'→'
	assert bytes(headers) == b'Foo: =?utf-8?b?4oaS?=\r\n\r\n'

	e = headers.create_element('foo', 'bar', dict(param=u'→'))
	assert bytes(e) == b"bar; param*=utf-8''%E2%86%92"


#def test_latin1_in_headers(headers):
#	headers['foo'] = u'ä'
#	assert bytes(headers) == b'Foo: =?ISO8859-1?b?...?=\r\n\r\n'


@pytest.mark.parametrize('headstring', [b'Foo: =?%s?b?4oaS?=', b"Foo: bar; param*=%s''%%E2%%86%%92"])
@pytest.mark.parametrize('encoding', [b'foo', b'heX', b'base64'])
def test_invalid_header_encoding(headers, headstring, encoding):
	headers.parse(headstring % (encoding,))
	with pytest.raises(InvalidHeader):
		headers.get_element('Foo')


def test_pop_header(headers):
	headers['Foo'] = 'bar'
	del headers['Foo']
	assert 'Foo' not in headers


def test_util_to_unicode():
	assert to_unicode(None) == u''
	assert to_unicode(b'\xff') == u'\xff'


def test_fromkeys():
	h = Headers.fromkeys(('foo', 'bar', 'Baz'), '1')
	assert h['foo'] == '1'
	assert h['Bar'] == '1'
	assert h['Baz'] == '1'


def test_get_element_default(headers):
	obj = object()
	assert headers.get_element('foo', default=obj) is obj


def test_header_values(headers):
	headers['Foo'] = 'bar; baz=blub'
	headers['Bar'] = 'foo; baz=blub'
	assert set(headers.values()) == {b'bar; baz=blub', b'foo; baz=blub'}


def test_header_append_params(headers):
	headers.append('Foo', 'bar', baz='val')
	assert dict(headers.items())['Foo'] == b'bar; baz=val'
	headers.append('Bar', 'bar', baz=None)
	assert dict(headers.items())['Bar'] == b'bar; baz'
