from . import util as _util, define, parse
from .util import FormatError


class StreamReader:
    def __init__ (self, f, name):
        self._f = f
        self.name = name
        self.skip_to(0)

    def read (self, n):
        data = self._f.read(n)
        self.pos += len(data)
        return data

    def read_exactly (self, n):
        data = self.read(n)
        if len(data) != n:
            raise EOFError(
                'expected to read {} bytes; only found {}'.format(n, len(data)))
        return data

    def skip_to (self, n):
        self.pos = self._f.seek(n)
        if self.pos != n:
            raise _util._FormatError('unable to seek to {}'.format(n))

    def skip (self, n):
        self.skip_to(self.pos + n)
