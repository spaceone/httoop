# -*- coding: utf-8 -*-
from __future__ import absolute_import

from httoop.codecs.common import Codec

# TODO: http://stackoverflow.com/questions/712791/what-are-the-differences-between-json-and-simplejson-python-modules#answer-16131316
try:
	from simplejson import dumps as json_encode
	from simplejson import loads as json_decode
except ImportError:
	from json import dumps as json_encode
	from json import loads as json_decode


class JSON(Codec):
	mimetype = 'application/json'

	@classmethod
	def encode(cls, data, charset=None):
		return json_encode(data)

	@classmethod
	def decode(cls, data, charset=None):
		return json_decode(data)
