# -*- coding: utf-8 -*-
from httoop.meta import HTTPSemantic


class URIType(HTTPSemantic):

	def __new__(mcs, name, bases, dict_):
		cls = super(URIType, mcs).__new__(mcs, name, tuple(bases), dict_)
		if dict_.get('SCHEME'):
			for base in bases:
				if getattr(base, 'SCHEMES', None) is not None:
					base.SCHEMES.setdefault(dict_['SCHEME'].lower(), cls)
		return cls
