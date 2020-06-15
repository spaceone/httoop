# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
from httoop.codecs import register, lookup, Codec
from httoop.exceptions import DecodeError, EncodeError


class FooBar(Codec):

	mimetype = 'text/foobar'


def test_codec_registering():
	assert lookup(FooBar.mimetype, raise_errors=False) is None
	with pytest.raises(KeyError):
		lookup(FooBar.mimetype, raise_errors=True)
	register(FooBar.mimetype, FooBar)
	assert lookup(FooBar.mimetype) is FooBar


def test_body_invalid_gzip():
	with pytest.raises(DecodeError) as exc:
		lookup('application/gzip').decode(b'asdf')
	assert 'Invalid gzip data' in str(exc.value)


def test_body_invalid_deflate():
	with pytest.raises(DecodeError) as exc:
		lookup('application/zlib').decode(b'asdf')
	assert 'Invalid zlib/deflate data' in str(exc.value)


def test_body_invalid_xml():
	with pytest.raises(DecodeError):
		lookup('application/xml').decode(b'asdf')


def test_body_invalid_hal():
	hal = lookup('application/hal+json')
	with pytest.raises(EncodeError):
		hal.encode([])
	with pytest.raises(EncodeError):
		hal.encode({'_embedded': None})
	with pytest.raises(EncodeError):
		hal.encode({'_links': None})
	with pytest.raises(DecodeError):
		hal.decode(b'[]')
	with pytest.raises(DecodeError):
		hal.decode(b'{"_links": {"foo": {}}}').get_link('foo')
	with pytest.raises(DecodeError):
		hal.decode(b'{"_links": {"foo": 1}}').get_link('foo')
	with pytest.raises(DecodeError):
		hal.decode(b'{"_links": {"foo": [1]}}').get_link('foo')
	with pytest.raises(DecodeError):
		hal.decode(b'{"_embedded": {"foo": 1}}').get_resource('foo')


def test_invalid_multipart(body):
	body.mimetype = 'multipart/x; boundary=asdf'
	codec = body.mimetype.codec
	'--asdf\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nfoo\r\n--asdf\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nbar\r\n--asdf\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nbaz\r\n--asdf--\r\n'
	with pytest.raises(DecodeError):
		codec.decode(b'foo--asdf\r\n', None, body.mimetype)
	with pytest.raises(DecodeError):
		codec.decode(b'--asdf\r\n', None, body.mimetype)
	with pytest.raises(DecodeError):
		codec.decode(b'--asdf--\r\nfooasdf--\r\n', None, body.mimetype)
	with pytest.raises(DecodeError):
		codec.decode(b'--asdf\r\nContent-Type: text/plain; charset=UTF-8\r\nfoo\r\n--asdf--\r\n', None, body.mimetype)
	with pytest.raises(DecodeError):
		codec.decode(b'--asdf\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nfoo--asdf--\r\n', None, body.mimetype)
	with pytest.raises(DecodeError):
		codec.decode(b'--asdf\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nfoo\r\n--asdfContent-Type: text/plain; charset=UTF-8\r\n\r\nbaz\r\n--asdf--\r\n', None, body.mimetype)


def test_body_invalid_plain_text():
	with pytest.raises(DecodeError):
		lookup('text/plain').decode(b'\xff')
	with pytest.raises(EncodeError):
		lookup('text/plain').encode(u'→', 'ISO8859-1')


def test_application_x_ww_form_urlencoded():
	codec = lookup('application/x-www-form-urlencoded')
	assert codec.encode({u'value': u''.join(chr(i) for i in range(128))}) == b'value=%0%1%2%3%4%5%6%7%8%9%A%B%C%D%E%F%10%11%12%13%14%15%16%17%18%19%1A%1B%1C%1D%1E%1F+%21%22%23%24%25%26%27%28%29%2A%2B%2C-.%2F0123456789%3A%3B%3C%3D%3E%3F%40ABCDEFGHIJKLMNOPQRSTUVWXYZ%5B%5C%5D%5E_%60abcdefghijklmnopqrstuvwxyz%7B%7C%7D~%7F'
