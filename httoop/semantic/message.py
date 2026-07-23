from contextlib import contextmanager
from typing import Iterator


class ComposedMessage:

    # FIXME: use it
    @property
    def close(self):  # pragma: no cover
        # TODO: find out why this constraint
        return 'Transfer-Encoding' in self.message.headers and 'chunked' not in self.message.headers.elements('Transfer-Encoding')

    @property
    def transfer_encoding(self):
        return self.message.headers.elements('Transfer-Encoding')

    @transfer_encoding.setter
    def transfer_encoding(self, transfer_encoding) -> None:
        if transfer_encoding:
            self.message.headers['Transfer-Encoding'] = bytes(transfer_encoding)
        #    self.message.transfer_codec = None  #self.message.transfer_encoding.iterdecode()
        else:
            self.message.headers.pop('Transfer-Encoding', None)
        #    self.message.transfer_codec = None

    @property
    def chunked(self):
        return 'chunked' in self.message.headers.elements('Transfer-Encoding')

    @chunked.setter
    def chunked(self, chunked) -> None:
        self.message.body.chunked = chunked
        if chunked:
            self.message.headers.pop('Content-Length', None)
            if self.chunked:
                return
            self.message.headers.append('Transfer-Encoding', b'chunked')
        else:
            if not self.chunked:
                return
            te = self.message.headers.elements('Transfer-Encoding')
            te.remove('chunked')
            self.message.headers['Transfer-Encoding'] = b''.join(map(bytes, te))
            if not te:
                self.message.headers.pop('Transfer-Encoding')

    @contextmanager
    def _composing(self) -> Iterator[None]:  # noqa: PLR6301
        yield

    def __iter__(self) -> Iterator[bytes]:
        with self._composing():
            start_line = bytes(self.message)
            headers = bytes(self.message.headers)
            yield start_line + headers
            yield from self.message.body
