# -*- coding: utf-8 -*-

from httoop.uri.uri import URI


class GitSSH(URI):
	__slots__ = ()
	SCHEME = b'git+ssh'
	PORT = 22


class SvnSSH(URI):
	__slots__ = ()
	SCHEME = b'svn+ssh'
	PORT = 22


class IMAP(URI):
	__slots__ = ()
	SCHEME = b'imap'
	PORT = 143


class NFS(URI):
	__slots__ = ()
	SCHEME = b'nfs'
	PORT = 2049


class MMS(URI):
	__slots__ = ()
	SCHEME = b'mms'
	PORT = 1755


class FTP(URI):
	__slots__ = ()
	SCHEME = b'ftp'
	PORT = 21


class LDAP(URI):
	__slots__ = ()
	SCHEME = b'ldap'
	PORT = 389
