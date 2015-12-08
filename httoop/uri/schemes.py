# -*- coding: utf-8 -*-

from httoop.uri.uri import URI


class GitSSH(URI):
	SCHEME = b'git+ssh'
	PORT = 22


class SvnSSH(URI):
	SCHEME = b'svn+ssh'
	PORT = 22


class IMAP(URI):
	SCHEME = b'imap'
	PORT = 143


class NFS(URI):
	SCHEME = b'nfs'
	PORT = 2049


class MMS(URI):
	SCHEME = b'mms'
	PORT = 1755


class FTP(URI):
	SCHEME = b'ftp'
	PORT = 21


class LDAP(URI):
	SCHEME = b'ldap'
	PORT = 389
