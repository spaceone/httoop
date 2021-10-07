import pytest

from httoop import URI, Body, Date, Headers, Method, Protocol, Request, Response, Status
from httoop.gateway.wsgi import WSGIBody
from httoop.messages.message import Message
from httoop.uri.http import HTTP, HTTPS
from httoop.uri.schemes import FTP, IMAP, LDAP, MMS, NFS, GitSSH, SvnSSH


@pytest.mark.parametrize('class_,args', [
	(FTP, ()),
	(HTTP, ()),
	(HTTPS, ()),
	(IMAP, ()),
	(LDAP, ()),
	(MMS, ()),
	(NFS, ()),
	(URI, ()),
	(Body, ()),
	(Date, ()),
	(GitSSH, ()),
	(Headers, ()),
	(Message, ()),
	(Method, ()),
	(Protocol, ()),
	(Request, ()),
	(Response, ()),
	pytest.param(Status, (), marks=pytest.mark.xfail(reason='Conflict')),
	(SvnSSH, ()),
	(WSGIBody, ()),
])
def test_slots(class_, args):
	obj = class_(*args)
	assert obj.__slots__ is not None
	with pytest.raises(AttributeError):
		obj.__dict__
	with pytest.raises(AttributeError):
		obj.foo = True
