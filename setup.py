#!/usr/bin/env python

#from glob import glob
from setuptools import setup, find_packages

from httoop.version import __version__ as version


setup(
	name='httoop',
	version=version,
	description='object oriented HTTP protocol library',
	long_description=open('README.md').read(),
	long_description_content_type='text/markdown',
	author='SpaceOne',
	author_email='space@wechall.net',
	url='https://github.com/spaceone/httoop',
	#download_url='',
	classifiers=[
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: POSIX :: BSD',
		'Operating System :: POSIX :: Linux',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
		'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
		'Topic :: Software Development :: Libraries :: Application Frameworks',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
	license='MIT',
	keywords='HTTP web proxy cache client server library',
	platforms='POSIX',
	packages=find_packages('.', exclude=['tests.*', 'tests']),
	#scripts=glob('bin/*'),
	install_requires=['six'],
	entry_points={},
	test_suite='tests.main.main',
	zip_safe=True
)
