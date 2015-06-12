import pytest

from httoop import Request, Response, Headers, Body, ClientStateMachine, ServerStateMachine

@pytest.fixture
def request():
	return Request()

@pytest.fixture
def response():
	return Response()

@pytest.fixture
def headers():
	return Headers()

@pytest.fixture
def body():
	return Body()

@pytest.fixture
def statemachine():
	return ServerStateMachine('http', 'localhost', 8090)

@pytest.fixture
def clientstatemachine():
	return ClientStateMachine()
