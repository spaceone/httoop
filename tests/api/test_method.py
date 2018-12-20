# See also: tests/request_/test_request_method.py
import pytest


def test_safe_methods(request_):
	all_methods = (
		(u'GET', True, True),
		(u'HEAD', True, True),
		(u'PUT', False, True),
		(u'POST', False, False),
		(u'DELETE', False, True),
		(u'OPTIONS', False, True),
		(u'TRACE', False, True),
	)
	for method, safe, idempotent in all_methods:
		request_.method = method
		assert request_.method.safe == safe
		assert request_.method.idempotent == idempotent


@pytest.mark.xfail(reason='hash changing + fixed references')
def test_hashable_methods(request_):
	methods = {}
	request_.method = u'GET'
	methods[request_.method] = 1
	assert 'GET' in methods
	assert 'POST' not in methods
	request_.method = u'POST'
	assert 'POST' not in methods
	methods[request_.method] = 1
	assert 'POST' in methods
	assert 'GET' in methods
