import pytest
from httoop import URI


@pytest.mark.parametrize('query_string,query', [
	(b'', ()),
	(b'&', ()),
	(b'&&', ()),
#	(b'=', ((u'', u''),)),
#	(b'=a', ((u'', u'a'),)),
	(b'a', ((u'a', u''),)),
	(b'a=', ((u'a', u''),)),
	(b'&a=b', ((u'a', u'b'),)),
	(b'&&a=b&&b=c&d=f&', ((u'a', u'b'), (u'b', u'c'), (u'd', u'f'))),
	(b'a=a+b&b=b+c', ((u'a', u'a b'), (u'b', u'b c'))),
	(b'a=1&a=2', ((u'a', u'1'), (u'a', u'2'))),
])
def test_query_string_parse(query_string, query):
	uri = URI(b'http://example.com/?%s' % (query_string,))
	assert uri.query == query


@pytest.mark.parametrize('query_string,query', [
	(b'', ()),
#	(b'=', ((u'', u''),)),
#	(b'=a', ((u'', u'a'),)),
	(b'a', ((u'a', u''),)),
#	(b'a=', ((u'a', u''),)),
	(b'a=b', ((u'a', u'b'),)),
	(b'a=b&b=c&d=f', ((u'a', u'b'), (u'b', u'c'), (u'd', u'f'))),
	(b'a=a+b&b=b+c', ((u'a', u'a b'), (u'b', u'b c'))),
	(b'a=1&a=2', ((u'a', u'1'), (u'a', u'2'))),
])
def test_query_string_compose(query_string, query):
	uri = URI(b'http://example.com/')
	uri.query = query
	assert uri.query_string == query_string
