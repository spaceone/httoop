from __future__ import unicode_literals
import pytest
from httoop.codecs import register, lookup, Codec


class FooBar(Codec):

	mimetype = 'text/foobar'


def test_codec_registering():
	assert lookup(FooBar.mimetype, raise_errors=False) is None
	with pytest.raises(KeyError):
		lookup(FooBar.mimetype, raise_errors=True)
	register(FooBar.mimetype, FooBar)
	assert lookup(FooBar.mimetype) is FooBar
