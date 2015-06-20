# -*- coding: utf-8 -*-
from httoop.parser import StateMachine
from httoop.messages import Response


class ClientStateMachine(StateMachine):

	Message = Response
