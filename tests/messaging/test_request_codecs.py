# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import pytest

from httoop import Body
from httoop.exceptions import InvalidHeader

try:
	unicode
except NameError:
	unicode = str


def test_json(body):
	body.mimetype = 'application/json'
	assert body.decode(b'{"foo": "bar"}') == {u"foo": u"bar"}
	body.encode({u"bar": u"foo"})
	assert bytes(body) == b'{"bar": "foo"}'
	# TODO: non-utf8


def test_invalid_json(body):
	body.mimetype = 'application/json'
	with pytest.raises(ValueError):
		body.decode('{"foo" "bar"}')


def test_form_urlencoded(body):
	body.mimetype = 'application/x-www-form-urlencoded'
	body.set(b'foo=bar&bar=bar1&bar=bar2&baz')
	assert body.decode() == ((u'foo', u'bar'), (u'bar', u'bar1'), (u'bar', u'bar2'), (u'baz', u''))
	# TODO: percent encoded


def test_percent_encoding(body):
	pass


multipart_string = (
	b'''--------------------------409e1d7f8fe3763a\r\nContent-Disposition: form-data; name="foo"\r\n\r\nfoocontent\r\n'''
	b'''--------------------------409e1d7f8fe3763a\r\nContent-Disposition: form-data; name="bar"; filename="test.txt"\r\n'''
	b'''Content-Type: text/plain\r\n\r\nbarcontent\r\n--------------------------409e1d7f8fe3763a--\r\n'''
)


def test_parse_multipart_form_data(body):
	body.mimetype = 'multipart/form-data'
	content_type = body.mimetype
	content_type.boundary = '------------------------409e1d7f8fe3763a'
	body.mimetype = content_type
	body.set(multipart_string)

	parts = body.decode()
	assert len(parts) == 2
	foo, bar = parts
	assert bytes(foo) == b'foocontent'
	assert bytes(bar) == b'barcontent'
	assert foo.headers.element('Content-Disposition') == u'form-data'
	assert bar.headers.element('Content-Disposition') == u'form-data'
	assert foo.headers.element('Content-Disposition').params[u'name'] == u'foo'
	assert bar.headers.element('Content-Disposition').params[u'name'] == u'bar'
	assert u'filename' not in foo.headers.element('Content-Disposition').params
	assert bar.headers.element(u'Content-Disposition').params[u'filename'] == u'test.txt'


def test_compose_multipart_form_data(body):
	body.mimetype = 'multipart/form-data'
	content_type = body.mimetype
	content_type.boundary = '------------------------409e1d7f8fe3763a'
	body.mimetype = content_type
	foo, bar = Body('foocontent'), Body('barcontent')
	foo.headers.pop('Content-Type')
	foo.headers['Content-Disposition'] = 'form-data; name="foo"'
	bar.headers['Content-Disposition'] = 'form-data; name="bar"; filename="test.txt"'
	bar.mimetype = 'text/plain'
	body.encode([foo, bar])
	assert sorted(multipart_string.split(b'\r\n')) == sorted(bytes(body).split(b'\r\n'))


@pytest.mark.parametrize('invalid', (b'', b'foo ', b'foo\tbar', b'a' * 202))
def test_invalid_boundary(invalid, headers):
	headers.parse(b'Content-Type: multipart/mixed; boundary="%s"' % (invalid,))
	with pytest.raises(InvalidHeader):
		headers.elements('Content-Type')


def test_invalid_form_data_content_disposition(headers):
	headers.parse(b'Content-Disposition: form-data; form-data=1')
	with pytest.raises(InvalidHeader):
		headers.elements('Content-Disposition')


def test_plain_text_utf8(body):
	body.mimetype = 'text/plain'
	body.encoding = 'UTF-8'
	check_encoding_dict(body, {
		b'foo': u'foo',
		b'b\xc3\xa4r': u'b\xe4r',
		b'\xe2\x86\x92': u'\u2192'
	})
	check_raises(body, [b'\xe4'], unicode, UnicodeDecodeError)


def test_plain_text_latin1(body):
	body.mimetype = 'text/plain'
	body.encoding = 'ISO8859-1'
	check_encoding_dict(body, {
		b'foo': u'foo',
		b'b\xe4r': u'b\xe4r',
		b'\xe2\x86\x92': u'\xe2\x86\x92'
	})
	check_raises(body, (u'\u2192',), bytes, UnicodeEncodeError)


def test_plain_text_ascii(body):
	body.mimetype = 'text/plain'
	body.encoding = 'ascii'
	check_encoding_dict(body, {
		b'foo': u'foo',
		b'bar': u'bar',
	})
	check_raises(body, (u'b\xe4r', u'\u2192'), bytes, UnicodeEncodeError)
	check_raises(body, (b'b\xc3\xa4r', b'\xe2\x86\x92', b'\xe4'), unicode, UnicodeDecodeError)


def test_hal_json(body):
	body.mimetype = 'application/hal+json'
	hal_doc = b'''{"_embedded": {"orders": [{"status": "shipped", "currency": "USD", "total": 30.0, "_links": {"basket": {"href": "/baskets/98712"}, "customer": {"href": "/customers/7809"}, "self": {"profile": null, "deprecation": false, "name": null, "hreflang": null, "href": "/orders/123", "templated": false, "type": null}}}, {"status": "processing", "currency": "USD", "total": 20.0, "_links": {"basket": {"href": "/baskets/97213"}, "customer": {"href": "/customers/12369"}, "self": {"href": "/orders/124"}}}]}, "currentlyProcessing": 14, "_links": {"curie": [{"profile": null, "deprecation": false, "name": "acme", "hreflang": null, "href": "http://docs.acme.com/relations/{rel}", "templated": true, "type": null}], "self": {"profile": null, "deprecation": false, "name": null, "hreflang": null, "href": "/orders", "templated": false, "type": null}, "find": {"href": "/orders{?id}", "templated": true}, "next": {"href": "/orders?page=2"}}, "shippedToday": 20}'''
	resource = body.decode(hal_doc)
	assert set(resource.get_relations()) == set([u'orders', u'curie', u'self', u'find', u'next'])
	assert resource.get_link('next') == {'profile': None, 'deprecation': False, 'name': None, 'hreflang': None, 'href': u'/orders?page=2', 'templated': False, 'type': None}
	assert resource.self == u'/orders'
	assert resource.get_curie('acme:widgets') == u'http://docs.acme.com/relations/widgets'
	assert resource.get_resource('orders').self == u'/orders/123'
	assert resource.get_link('not-existing') is None
	assert resource.get_resource('not-existing') is None
	assert resource.get_curie('acme') == 'acme'
	resource.add_link('find', {'href': 'bar', 'name': 'xx'})
	resource.add_link('relation', {'href': 'bar', 'name': 'xx'})
	resource.add_link('relation', {'href': 'foo', 'templated': 'true', 'name': 'name', 'deprecation': 'true'})
	assert resource.get_link('relation', 'name') == {'deprecation': False, 'href': u'foo', 'hreflang': None, 'name': 'name', 'templated': False, 'type': None, 'profile': None}
	resource.add_resource('relation', {})
	assert resource.get_resource('relation') == {'_embedded': {}, '_links': {}}

	body.encode(resource)
	assert {"_embedded": {"relation": [{}], "orders": [{"status": "shipped", "currency": "USD", "total": 30.0, "_links": {"basket": {"href": "/baskets/98712"}, "customer": {"href": "/customers/7809"}, "self": {"profile": None, "deprecation": False, "name": None, "hreflang": None, "href": "/orders/123", "templated": False, "type": None}}}, {"status": "processing", "currency": "USD", "total": 20.0, "_links": {"basket": {"href": "/baskets/97213"}, "customer": {"href": "/customers/12369"}, "self": {"href": "/orders/124"}}}]}, "currentlyProcessing": 14, "_links": {"curie": [{"profile": None, "deprecation": False, "name": "acme", "hreflang": None, "href": "http://docs.acme.com/relations/{rel}", "templated": True, "type": None}], "self": {"profile": None, "deprecation": False, "name": None, "hreflang": None, "href": "/orders", "templated": False, "type": None}, "relation": [{"profile": None, "deprecation": False, "name": "xx", "hreflang": None, "href": "bar", "templated": False, "type": None}, {"profile": None, "deprecation": False, "name": "name", "hreflang": None, "href": "foo", "templated": False, "type": None}], "find": [{"href": "/orders{?id}", "templated": True, "profile": None, "deprecation": False, "hreflang": None, "type": None, "name": None}, {'href': 'bar', 'name': 'xx', "profile": None, "deprecation": False, "hreflang": None, "templated": False, "type": None}], "next": {"profile": None, "deprecation": False, "name": None, "hreflang": None, "href": "/orders?page=2", "templated": False, "type": None}}, "shippedToday": 20} == json.loads(bytes(body).decode('ASCII'))


def check_encoding_dict(body, data):
	for byte, string in data.items():
		body.set(byte)
		assert unicode(body) == string
		body.set(string)
		assert bytes(body) == byte

		# use the codec for text/plain explicit
		body.set(None)
		body.decode(byte)
		assert unicode(body) == string
		body.set(None)
		body.encode(string)
		assert bytes(body) == byte


def check_raises(body, chars, type_, exception):
	for chr_ in chars:
		with pytest.raises(exception):
			body.set(chr_)
			type_(body)


def test_message_http_response(body, request_):
	body.mimetype = 'message/http'
	request_.headers['User-Agent'] = 'foo'
	body.encode(request_)
	assert bytes(body) == b'GET / HTTP/1.1\r\nUser-Agent: foo\r\n\r\n'
	body.decode(b'HTTP/1.1 200 OK\r\nContent-Length: 12\r\n\r\n')
	assert body.data.status == 200
	assert body.data.headers['Content-Length'] == '12'


def test_message_http_request(body, response):
	body.mimetype = 'message/http'
	response.headers['Content-Length'] = '0'
	body.encode(response)
	assert bytes(body) == b'HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n'
	body.decode(b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n')
	assert body.data.method == 'GET'
	assert body.data.headers['Host'] == 'example.com'


def test_application_xml(body):
	body.mimetype = 'application/xml'
	body.decode(b'<?xml version="1.0" encoding="UTF-8" ?><fooml><head foo="bar"></head></fooml>')
	assert body.data.find('head').attrib == {'foo': 'bar'}
	root = body.data
	body.set(None)
	body.encode(root)
	assert b'<fooml><head foo="bar" /></fooml>' in bytes(body)
