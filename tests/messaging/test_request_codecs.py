# -*- coding: utf-8 -*-
import pytest
from httoop import Body
from httoop.exceptions import InvalidHeader

try:
	unicode
except NameError:
	unicode = str


def test_json(body):
	body.mimetype = 'application/json'
	assert body.decode('{"foo": "bar"}') == {u"foo": u"bar"}
	body.encode({u"bar": u"foo"})
	assert bytes(body) == '{"bar": "foo"}'
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
	'''--------------------------409e1d7f8fe3763a\r\nContent-Disposition: form-data; name="foo"\r\n\r\nfoocontent\r\n'''
	'''--------------------------409e1d7f8fe3763a\r\nContent-Disposition: form-data; name="bar"; filename="test.txt"\r\n'''
	'''Content-Type: text/plain\r\n\r\nbarcontent\r\n--------------------------409e1d7f8fe3763a--\r\n'''
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
	assert bytes(foo) == 'foocontent'
	assert bytes(bar) == 'barcontent'
	assert foo.headers.element('Content-Disposition') == 'form-data'
	assert bar.headers.element('Content-Disposition') == 'form-data'
	assert foo.headers.element('Content-Disposition').params['name'] == 'foo'
	assert bar.headers.element('Content-Disposition').params['name'] == 'bar'
	assert 'filename' not in foo.headers.element('Content-Disposition').params
	assert bar.headers.element('Content-Disposition').params['filename'] == 'test.txt'


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
	assert sorted(multipart_string.split('\r\n')) == sorted(bytes(body).split('\r\n'))


def test_invalid_boundary(headers):
	for invalid in (b'', b'foo ', b'foo\tbar', b'a'*202):
		headers.parse('Content-Type: multipart/mixed; boundary="%s"' % (invalid,))
		with pytest.raises(InvalidHeader):
			headers.elements('Content-Type')

def test_invalid_form_data_content_disposition(headers):
	headers.parse('Content-Disposition: form-data; form-data=1')
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
