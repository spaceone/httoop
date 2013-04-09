# -*- coding: utf-8 -*-
"""HTTP date

.. seealso:: :rfc:`2616#section-3.3`
"""

__all__ = ['Date']

# ripped from cherrypy (http://www.cherrypy.org/) (MIT license)
# TODO: implement the function wrapper thing from circuits.web
try:
	from email.utils import formatdate
	def Date(timeval=None):
		return formatdate(timeval, usegmt=True)
except ImportError:
	from rfc822 import formatdate as Date

# TODO: create a class here which can handle every 3 HTTP Date formats (parse and convert from timestamp/datetime)
