import pytest
from httoop import Status

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

	assert response.status != 'foo'
	assert not response.status == 'foo'

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


def test_status_aliases(response):
	assert response.status.reason == response.status.reason_phrase
	assert response.status.code == response.status.status


@pytest.mark.xfail
def test_status_parse(response):
	response.status.parse('400 bad request')
	assert response.status == 400
	assert response.status.reason == u'bad request'

	response.status.parse('401 ')
	assert response.status == 401
	assert not response.status.reason

	response.parse('HTTP/1.1 402')
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
