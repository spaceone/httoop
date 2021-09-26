from __future__ import unicode_literals

import pytest

from httoop import URI


@pytest.mark.parametrize('url,expected', (
	(b'http://..', (u'http', u'', u'', u'..', 80, u'', u'', u'')),
	(b'http:///..', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	(b'http://.', (u'http', u'', u'', u'.', 80, u'', u'', u'')),
	(b'http:///.', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	(b'http:.', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	(b'http:..', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	(b'http:/', (u'http', u'', u'', u'', 80, u'/', u'', u'')),
	pytest.param(b'http://f/..%2f..', (u'http', u'', u'', u'f', 80, u'/', u'', u''), marks=pytest.mark.xfail(reason='Incorrect but we want to preserve /.')),
))
def test_abspath(url, expected):
	uri = URI()
	uri.parse(url)
	uri.abspath()
	assert uri.tuple == expected
	uri.normalize()
	assert uri.tuple == expected
