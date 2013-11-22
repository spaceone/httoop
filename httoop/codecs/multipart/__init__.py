# -*- coding: utf-8 -*-
from httoop.codecs.common import Codec


class MultipartFormData(Codec):
	mimetype = 'multipart/form-data'


class MultipartMixed(Codec):
	mimetype = 'multipart/mixed'
