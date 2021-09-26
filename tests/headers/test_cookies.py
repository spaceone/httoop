from __future__ import unicode_literals

from datetime import datetime

import pytest

from httoop.exceptions import InvalidHeader


@pytest.mark.parametrize('cookie,values', [
	('Foo=bar', {'Foo': 'bar'}),
	('foo="bar"', {'foo': 'bar'}),
	('PREF=ID=1111111111111111:FF=0:TM=1442748479:LM=1442748479:V=1:S=65Xs1xpQVvq8hzFq; NID=71=mxdu-SNqsp8LWMgThQgDi6po2Hg-Hjd0BKRVs2l53eh70CacIMBNFPXldZLCQICeCmOwl68I6_7hr6Tuhku8wvnc1uJQt9r1zBy7J4TsELuTv8jsod_0WoWR-1neDai_uJiiNA', dict((
		('PREF', 'ID=1111111111111111:FF=0:TM=1442748479:LM=1442748479:V=1:S=65Xs1xpQVvq8hzFq'),
		('NID', '71=mxdu-SNqsp8LWMgThQgDi6po2Hg-Hjd0BKRVs2l53eh70CacIMBNFPXldZLCQICeCmOwl68I6_7hr6Tuhku8wvnc1uJQt9r1zBy7J4TsELuTv8jsod_0WoWR-1neDai_uJiiNA'),
	))),
])
def test_cookie(cookie, values, headers):
	headers['Cookie'] = cookie
	for e in headers.elements('Cookie'):
		assert e.cookie_value == values[e.cookie_name]


set_cookie = (
	(('PREF=ID=1111111111111111:FF=0:TM=1442750337:LM=1442750337:V=1:S=OzLcd0aN7JCguSAs; expires=Thu, 31-Dec-2015 16:02:17 GMT; path=/; domain=.google.de, NID=71=qx1aDrIv1ZCfe9nzprBX_6_GMe5jmnD2RniOFz5UINXwR_3TQU0Kon20XczY4aUNlt75z_2r1wHOJw4FKL9RMUCo5QIEbmKGw3W4U7nkpZZolbPBCGbw6RN2N0p7D3q6fhXQbg; expires=Mon, 21-Mar-2016 11:58:57 GMT; path=/; domain=.google.de; HttpOnly', {
		'PREF': {
			'cookie_value': 'ID=1111111111111111:FF=0:TM=1442750337:LM=1442750337:V=1:S=OzLcd0aN7JCguSAs',
			'expires': datetime(2015, 12, 31, 16, 2, 17),
			'path': '/',
			'domain': '.google.de',
			'httponly': False,
			'secure': False,
			'persistent': True,
			'max_age': None,
		},
		'NID': {
			'cookie_value': '71=qx1aDrIv1ZCfe9nzprBX_6_GMe5jmnD2RniOFz5UINXwR_3TQU0Kon20XczY4aUNlt75z_2r1wHOJw4FKL9RMUCo5QIEbmKGw3W4U7nkpZZolbPBCGbw6RN2N0p7D3q6fhXQbg',
			'expires': datetime(2016, 3, 21, 11, 58, 57),
			'path': '/',
			'domain': '.google.de',
			'httponly': True,
			'secure': False,
			'persistent': True,
			'max_age': None,
		},
	}),)
)


@pytest.mark.parametrize('cookie,values', set_cookie)
def test_set_cookie(cookie, values, headers):
	headers['Set-Cookie'] = cookie
	for e in headers.elements('Set-Cookie'):
		for key, value in values[e.cookie_name].items():
			assert getattr(e, key) == value


def test_invalid_expires(headers):
	headers['Set-Cookie'] = 'foo=bar; expires=xyz'
	with pytest.raises(InvalidHeader):
		headers.get_element('Set-Cookie').expires


def test_invalid_max_age(headers):
	headers['Set-Cookie'] = 'foo=bar; max-age=1.1'
	with pytest.raises(InvalidHeader):
		headers.get_element('Set-Cookie').max_age


def test_persistent(headers):
	headers['Set-Cookie'] = 'foo=bar; '
	assert not headers.get_element('Set-Cookie').persistent
	headers['Set-Cookie'] = 'foo=bar; expires=Thu, 31-Dec-2015 16:02:17 GMT'
	assert headers.get_element('Set-Cookie').persistent
	headers['Set-Cookie'] = 'foo=bar; max-age=1'
	assert headers.get_element('Set-Cookie').persistent


def test_mulitline_set_cookie(headers):
	headers.append('Set-Cookie', b'foo=bar;')
	headers.append('Set-Cookie', b'bar=baz; max-age=1')
	assert bytes(headers) == b'Set-Cookie: foo=bar;\r\nSet-Cookie: bar=baz; max-age=1\r\n\r\n'


def test_joining_multiple_cookies(headers):
	headers.append('Cookie', b'foo=bar')
	headers.append('Cookie', b'bar=baz')
	assert bytes(headers) == b'Cookie: foo=bar; bar=baz\r\n\r\n'


@pytest.mark.xfail(reason='Cookie must only be one header, separated by ;')
def test_parsing_multiple_cookie_lines(statemachine):
	statemachine.parse(b'GET / HTTP/1.1\r\nHost: www.example.com\r\n')
	statemachine.parse(b'Cookie: foo=bar\r\n')
	with pytest.raises(InvalidHeader):
		statemachine.parse(b'Cookie: bar=baz\r\n\r\n')
