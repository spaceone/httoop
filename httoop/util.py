from six import PY3, text_type, binary_type, BytesIO, iteritems

class CaseInsensitiveDict(dict):
	"""A case-insensitive dict subclass.

		Each key is changed on entry to str(key).title().
	"""

	def __init__(self, *args, **kwargs):
		d = dict(*args, **kwargs)
		for key, value in iteritems(d):
			dict.__setitem__(self, str(key).title(), value)
		dict.__init__(self)

	def __getitem__(self, key):
		return dict.__getitem__(self, str(key).title())

	def __setitem__(self, key, value):
		dict.__setitem__(self, str(key).title(), value)

	def __delitem__(self, key):
		dict.__delitem__(self, str(key).title())

	def __contains__(self, key):
		return dict.__contains__(self, str(key).title())

	def get(self, key, default=None):
		return dict.get(self, str(key).title(), default)

	def update(self, E):
		for k in E.keys():
			self[str(k).title()] = E[k]

	@classmethod
	def fromkeys(cls, seq, value=None):
		newdict = cls()
		for k in seq:
			newdict[k] = value
		return newdict

	def setdefault(self, key, x=None):
		key = str(key).title()
		try:
			return dict.__getitem__(self, key)
		except KeyError:
			self[key] = x
			return x

	def pop(self, key, default=None):
		return dict.pop(self, str(key).title(), default)

class HTTPString(object):
	def __str__(self):
		if PY3:
			return self.__unicode__()
		else:
			return self.__bytes__()

	def __unicode__(self):
		return bytes(self).decode('utf-8')

	def __bytes__(self):
		raise NotImplemented
