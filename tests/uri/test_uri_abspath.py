import pytest
from httoop import URI


@pytest.mark.parametrize('url,expected', (
	('http://..', (u'http', u'', u'', u'..', 80, u'', u'', u'')),
	('http:///..', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	('http://.', (u'http', u'', u'', u'.', 80, u'', u'', u'')),
	('http:///.', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	('http:.', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	('http:..', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	('http:/', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	pytest.mark.xfail((b'http://f/..%2f..', (u'http', u'', u'', u'f', 80, u'/', u'', u'')), reason='Incorrect but we want to preserve /.'),
))
def test_abspath(url, expected):
	uri = URI()
	uri.parse(url)
	uri.abspath()
	assert uri.tuple == expected
	uri.normalize()
	assert uri.tuple == expected
