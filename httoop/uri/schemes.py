from httoop.uri.uri import URI


class GitSSH(URI, scheme='git+ssh'):
    __slots__ = ()
    PORT = 22


class SvnSSH(URI, scheme='svn+ssh'):
    __slots__ = ()
    PORT = 22


class IMAP(URI, scheme='imap'):
    __slots__ = ()
    PORT = 143


class NFS(URI, scheme='nfs'):
    __slots__ = ()
    PORT = 2049


class MMS(URI, scheme='mms'):
    __slots__ = ()
    PORT = 1755


class FTP(URI, scheme='ftp'):
    __slots__ = ()
    PORT = 21


class LDAP(URI, scheme='ldap'):
    __slots__ = ()
    PORT = 389
