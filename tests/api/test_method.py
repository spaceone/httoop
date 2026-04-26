# See also: tests/request_/test_request_method.py

import pytest


def test_safe_methods(request_):
    all_methods = (
        ('GET', True, True),
        ('HEAD', True, True),
        ('PUT', False, True),
        ('POST', False, False),
        ('DELETE', False, True),
        ('OPTIONS', False, True),
        ('TRACE', False, True),
    )
    for method, safe, idempotent in all_methods:
        request_.method = method
        assert request_.method.safe == safe
        assert request_.method.idempotent == idempotent


@pytest.mark.xfail(reason='hash changing + fixed references')
def test_hashable_methods(request_):
    methods = {}
    request_.method = 'GET'
    methods[request_.method] = 1
    assert b'GET' in methods
    assert b'POST' not in methods
    request_.method = 'POST'
    assert b'POST' not in methods
    methods[request_.method] = 1
    assert b'POST' in methods
    assert b'GET' in methods
