from httoop.exceptions import InvalidHeader
import pytest
from datetime import datetime


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
		},
		'NID': {
			'cookie_value': '71=qx1aDrIv1ZCfe9nzprBX_6_GMe5jmnD2RniOFz5UINXwR_3TQU0Kon20XczY4aUNlt75z_2r1wHOJw4FKL9RMUCo5QIEbmKGw3W4U7nkpZZolbPBCGbw6RN2N0p7D3q6fhXQbg',
			'expires': datetime(2016, 3, 21, 11, 58, 57),
			'path': '/',
			'domain': '.google.de',
			'httponly': True,
			'secure': False,
		},
	}),)
)

@pytest.mark.parametrize('cookie,values', set_cookie)
def test_set_cookie(cookie, values, headers):
	headers['Set-Cookie'] = cookie
	for e in headers.elements('Set-Cookie'):
		for key, value in values[e.cookie_name].iteritems():
			assert getattr(e, key) == value
