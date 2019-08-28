# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
	assert bytes(body) == u'{"bar": "foo"}'
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
	assert resource.get_relations() == [u'orders', u'curie', u'self', u'find', u'next']
	assert resource.get_link('next') == {'profile': None, 'deprecation': False, 'name': None, 'hreflang': None, 'href': u'/orders?page=2', 'templated': False, 'type': None}
	assert resource.self == u'/orders'
	assert resource.get_curie('acme:widgets') == u'http://docs.acme.com/relations/widgets'
	assert resource.get_resource('orders').self == u'/orders/123'


def check_encoding_dict(body, data):
	for byte, string in data.items():
		body.set(byte)
		assert unicode(body) == string
		body.set(string)
		assert bytes(body) == byte


def check_raises(body, chars, type_, exception):
	for chr_ in chars:
		with pytest.raises(exception):
			body.set(chr_)
			type_(body)
