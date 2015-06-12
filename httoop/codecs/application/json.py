# -*- coding: utf-8 -*-
from __future__ import absolute_import

from httoop.codecs.common import Codec

from json import dumps as json_encode
from json import loads as json_decode


class JSON(Codec):
	mimetype = 'application/json'

	@classmethod
	def encode(cls, data, charset=None, mimetype=None):
		return json_encode(data)

	@classmethod
	def decode(cls, data, charset=None, mimetype=None):
		return json_decode(data)
