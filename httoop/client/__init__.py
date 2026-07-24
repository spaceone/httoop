from __future__ import annotations

from httoop.exceptions import InvalidLine
from httoop.messages import Request, Response
from httoop.parser import NOT_RECEIVED_YET, StateMachine


class ClientStateMachine(StateMachine):

    Message = Response
    request: Request
    message: Response

    def __init__(self, *, strict: bool = True, max_status_line_length: float = 256) -> None:
        super().__init__(strict=strict)
        self.max_status_line_length = max_status_line_length

    def parse_startline(self) -> bool | None:
        state = super().parse_startline()
        if state is NOT_RECEIVED_YET:
            self._check_status_line_max_length(self.buffer)
        return state

    def _check_status_line_max_length(self, response_line: bytearray | bytes) -> None:
        if len(response_line) > self.max_status_line_length:
            raise InvalidLine('The maximum length of the response status line is %d' % self.max_status_line_length)

    def on_headers_complete(self) -> None:
        super().on_headers_complete()
        self.remove_invalid_headers()

    def remove_invalid_headers(self) -> None:
        if self.request.method == 'CONNECT':
            self.message.headers.pop('Transfer-Encoding', None)
            self.message.headers.pop('Content-Length', None)
