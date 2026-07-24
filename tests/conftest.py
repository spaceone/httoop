import pytest

from httoop import URI, Body, ClientStateMachine, Headers, Request, Response, ServerStateMachine


@pytest.fixture
def request_() -> Request:
    return Request()


@pytest.fixture
def response() -> Response:
    return Response()


@pytest.fixture
def headers() -> Headers:
    return Headers()


@pytest.fixture
def body() -> Body:
    return Body()


@pytest.fixture
def statemachine() -> ServerStateMachine:
    return ServerStateMachine('http', 'localhost', 8090)


@pytest.fixture
def clientstatemachine() -> ClientStateMachine:
    c = ClientStateMachine()
    c.request = Request()
    return c


@pytest.fixture
def uri() -> URI:
    return URI()
