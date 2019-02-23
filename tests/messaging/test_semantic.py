from httoop import ComposedResponse


def test_composing(request_, response):
	c = ComposedResponse(response, request_)
	c.prepare()
