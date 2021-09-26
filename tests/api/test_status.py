from __future__ import unicode_literals

import pytest

from httoop import Status
from httoop.status import (
	CREATED, INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED, MOVED_PERMANENTLY, MULTIPLE_CHOICES, NOT_FOUND,
	NOT_MODIFIED, OK, REQUEST_TIMEOUT, UNAUTHORIZED, UPGRADE_REQUIRED,
)

try:
	unicode
except NameError:
	unicode = str


def test_staus_comparision(response):
	response.status = 204
	assert response.status == 204
	assert response.status != 200
	assert response.status >= 204
	assert response.status <= 204
	assert response.status >= 203
	assert response.status <= 205
	assert response.status > 203
	assert response.status < 205

	assert not response.status != 204
	assert not response.status == 200
	assert not response.status <= 203
	assert not response.status >= 205
	assert not response.status < 203
	assert not response.status > 205

	assert response.status != u'foo'
	assert not response.status == u'foo'
	assert response.status != b'foo'
	assert not response.status == b'foo'

	assert response.status == b'204 No Content'


def test_status_with_status_comparisions(response):
	response.status = 204
	assert response.status == Status(204)
	assert response.status != Status(200)
	assert response.status >= Status(204)
	assert response.status <= Status(204)
	assert response.status >= Status(203)
	assert response.status <= Status(205)
	assert response.status > Status(203)
	assert response.status < Status(205)

	assert not response.status != Status(204)
	assert not response.status == Status(200)
	assert not response.status <= Status(203)
	assert not response.status >= Status(205)
	assert not response.status < Status(203)
	assert not response.status > Status(205)


def test_stats_int(response):
	response.status = 100
	assert int(response.status) == 100


def test_status_tuple(response):
	response.status = 200
	assert response.status.code == 200
	assert response.status.reason == u'OK'
	response.status = (299, u'MyReason')
	assert response.status == 299
	assert response.status.reason == u'MyReason'


def test_status_string(response):
	response.status = u'299 Yes'
	assert response.status == 299
	assert unicode(response.status) == u'299 Yes'
	assert bytes(response.status) == b'299 Yes'
	response.status = b'298 Yep'
	assert response.status == 298
	assert response.status.reason == u'Yep'
	assert bytes(response.status) == b'298 Yep'
	assert unicode(response.status) == u'298 Yep'


def test_set_status_status(response):
	status = Status(203, b'Foobar')
	response.status = status
	assert response.status.code == 203
	assert response.status.reason == u'Foobar'
	assert response.status == b'203 Foobar'


def test_set_status_code(response):
	response.status.code = 400
	assert response.status.reason == 'OK'
	response.status.reason = 'Bad Request'
	assert response.status.reason == 'Bad Request'


def test_status_aliases(response):
	assert response.status.reason == response.status.reason_phrase
	assert response.status.code == response.status.status


@pytest.mark.xfail
def test_status_parse(response):
	response.status.parse(b'400 bad request')
	assert response.status == 400
	assert response.status.reason == u'bad request'

	response.status.parse(b'401 ')
	assert response.status == 401
	assert not response.status.reason

	response.parse(b'HTTP/1.1 402')
	assert response.status == 402
	assert not response.status.reason


def test_status_type(response):
	response.status = 100
	assert response.status.informational
	assert not response.status.successful
	assert not response.status.redirection
	assert not response.status.client_error
	assert not response.status.server_error

	response.status = 200
	assert not response.status.informational
	assert response.status.successful
	assert not response.status.redirection
	assert not response.status.client_error
	assert not response.status.server_error

	response.status = 300
	assert not response.status.informational
	assert not response.status.successful
	assert response.status.redirection
	assert not response.status.client_error
	assert not response.status.server_error

	response.status = 400
	assert not response.status.informational
	assert not response.status.successful
	assert not response.status.redirection
	assert response.status.client_error
	assert not response.status.server_error

	response.status = 500
	assert not response.status.informational
	assert not response.status.successful
	assert not response.status.redirection
	assert not response.status.client_error
	assert response.status.server_error


@pytest.mark.parametrize('code', (99, 600, 1000))
def test_invalid_status_code(code, response):
	with pytest.raises(TypeError):
		response.status = code


def test_invalid_status_subclasses():
	from httoop.status import ServerErrorStatus
	with pytest.raises(RuntimeError):
		class MyServerError(ServerErrorStatus):
			code = 600

	with pytest.raises(RuntimeError):
		class MyInformational(ServerErrorStatus):
			code = 100


def test_created_location():
	with pytest.raises(CREATED) as exc:
		raise CREATED(u'http://example.com')
	assert exc.value.to_dict()['Location'] == u'http://example.com'
	assert exc.value.body.data == {'status': 201, 'headers': {'Location': u'http://example.com'}, 'reason': 'Created', 'description': 'Document created, URL follows', 'Location': u'http://example.com'}
	exc.value.body = None
	assert exc.value.body.data is None


def test_repr():
	assert repr(OK()) == "<HTTP Status 200 'OK' (Request fulfilled, document follows)>"


def test_internal_server_error_traceback():
	with pytest.raises(INTERNAL_SERVER_ERROR) as exc:
		raise INTERNAL_SERVER_ERROR(traceback='Traceback (most recent call last):')
	assert exc.value.to_dict()['traceback'] == u'Traceback (most recent call last):'


def test_redirection_mulitple():
	with pytest.raises(MULTIPLE_CHOICES) as exc:
		raise MULTIPLE_CHOICES(('http://example.org', 'https://example.org'))
	assert exc.value.headers == {'Location': 'http://example.org, https://example.org'}
	assert exc.value.to_dict()['Location'] == 'http://example.org, https://example.org'


def test_redirection_not_modified():
	with pytest.raises(NOT_MODIFIED) as exc:
		raise NOT_MODIFIED()
	assert 'Location' not in exc.value.headers


def test_redirection_moved_permanently():
	with pytest.raises(MOVED_PERMANENTLY) as exc:
		raise MOVED_PERMANENTLY('http://example.org')
	assert exc.value.headers == {'Location': 'http://example.org'}


def test_unauthorized():
	with pytest.raises(UNAUTHORIZED) as exc:
		raise UNAUTHORIZED('basic realm="foo"')
	assert exc.value.to_dict()['WWW-Authenticate'] == 'basic realm="foo"'


def test_not_found():
	with pytest.raises(NOT_FOUND) as exc:
		raise NOT_FOUND('/foo')
	assert repr(exc.value) == "<HTTP Status 404 'Not Found' (The requested resource \"/foo\" was not found on this server.)>"


def test_method_not_allowed():
	with pytest.raises(METHOD_NOT_ALLOWED) as exc:
		raise METHOD_NOT_ALLOWED('GET')
	assert exc.value.to_dict()['Allow'] == 'GET'


def test_request_timeout():
	with pytest.raises(REQUEST_TIMEOUT) as exc:
		raise REQUEST_TIMEOUT()
	assert exc.value.headers['Connection'] == 'close'


def test_upgrade_required():
	with pytest.raises(UPGRADE_REQUIRED) as exc:
		raise UPGRADE_REQUIRED('foo')
	assert exc.value.headers['Connection'] == 'Upgrade'
	assert exc.value.headers['Upgrade'] == 'foo'
