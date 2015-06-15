# See also: tests/request/test_request_method.py

def test_safe_methods(request):
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
		request.method = method
		assert request.method.safe == safe
		assert request.method.idempotent == idempotent
