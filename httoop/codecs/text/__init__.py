# -*- coding: utf-8 -*-
from httoop.codecs.common import Codec, Enconv


class PlainText(Enconv):
	mimetype = 'text/plain'


class HTML(Codec):
	mimetype = 'text/html'
